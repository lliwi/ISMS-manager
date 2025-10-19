"""
Blueprint para Gestión de Tareas Periódicas
Control 5.37 - Procedimientos operativos documentados
Requisitos ISO/IEC 27001:2023 - Capítulos 6.2, 8.1, 9.1-9.3
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os

from models import db, User, Role, SOAControl
from app.models.task import (
    TaskTemplate, Task, TaskEvidence, TaskComment,
    TaskStatus, TaskPriority, TaskCategory, TaskFrequency
)
from app.services.task_service import TaskService
from app.services.notification_service import NotificationService
from app.forms.task_forms import (
    TaskTemplateForm, TaskForm, TaskUpdateForm, TaskCompleteForm,
    TaskCommentForm, TaskEvidenceForm, TaskFilterForm, TaskApprovalForm
)
from app.utils.decorators import role_required


tasks_bp = Blueprint('tasks', __name__, url_prefix='/tasks')


# ==================== DASHBOARD ====================

@tasks_bp.route('/')
@tasks_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal de tareas"""
    return index()


@tasks_bp.route('/index')
@login_required
def index():
    """Vista principal de tareas"""

    # Obtener estadísticas del usuario actual
    stats = TaskService.get_task_statistics(user_id=current_user.id)

    # Mis tareas asignadas
    my_tasks = Task.query.filter(
        Task.assigned_to_id == current_user.id,
        Task.status.in_([TaskStatus.PENDIENTE, TaskStatus.EN_PROGRESO, TaskStatus.VENCIDA])
    ).order_by(Task.due_date.asc()).all()

    # Tareas prioritarias (críticas y altas)
    priority_tasks = Task.query.filter(
        Task.assigned_to_id == current_user.id,
        Task.priority.in_([TaskPriority.CRITICA, TaskPriority.ALTA]),
        Task.status != TaskStatus.COMPLETADA
    ).order_by(Task.due_date.asc()).limit(6).all()

    # Categorías para filtros
    categories = TaskCategory

    # Estadísticas por categoría
    category_stats = {}
    for category in TaskCategory:
        count = Task.query.filter(
            Task.assigned_to_id == current_user.id,
            Task.category == category,
            Task.status != TaskStatus.COMPLETADA
        ).count()
        if count > 0:
            category_stats[category.value] = count

    return render_template(
        'tasks/index.html',
        stats=stats,
        my_tasks=my_tasks,
        priority_tasks=priority_tasks,
        categories=categories,
        category_stats=category_stats
    )


# ==================== LISTA DE TAREAS ====================

@tasks_bp.route('/list')
@login_required
def list_tasks():
    """Lista de todas las tareas"""

    # Formulario de filtros
    filter_form = TaskFilterForm(request.args, meta={'csrf': False})

    # Poblar choices de usuarios
    filter_form.assigned_to_id.choices = [('', 'Todos')] + [
        (str(u.id), f"{u.first_name} {u.last_name}" if u.first_name else u.username)
        for u in User.query.filter_by(is_active=True).order_by(User.username).all()
    ]

    # Query base
    query = Task.query

    # Aplicar filtros
    if filter_form.status.data:
        query = query.filter(Task.status == TaskStatus(filter_form.status.data))

    if filter_form.category.data:
        query = query.filter(Task.category == TaskCategory(filter_form.category.data))

    if filter_form.priority.data:
        query = query.filter(Task.priority == TaskPriority(filter_form.priority.data))

    if filter_form.assigned_to_id.data:
        query = query.filter(Task.assigned_to_id == int(filter_form.assigned_to_id.data))

    if filter_form.search.data:
        search_term = f"%{filter_form.search.data}%"
        query = query.filter(
            db.or_(
                Task.title.ilike(search_term),
                Task.description.ilike(search_term),
                Task.iso_control.ilike(search_term)
            )
        )

    # Ordenar por fecha de vencimiento
    query = query.order_by(Task.due_date.asc())

    # Paginación
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    tasks = pagination.items

    return render_template(
        'tasks/list.html',
        tasks=tasks,
        pagination=pagination,
        filter_form=filter_form
    )


# ==================== VER DETALLE DE TAREA ====================

@tasks_bp.route('/<int:id>')
@login_required
def view(id):
    """Ver detalle de una tarea"""

    task = Task.query.get_or_404(id)

    # Verificar permisos: solo el asignado, creador o admin puede ver
    if not (current_user.id == task.assigned_to_id or
            current_user.id == task.created_by_id or
            current_user.role.name in ['Administrador', 'CISO', 'Auditor Interno']):
        flash('No tienes permiso para ver esta tarea', 'danger')
        return redirect(url_for('tasks.dashboard'))

    # Formularios
    comment_form = TaskCommentForm()
    evidence_form = TaskEvidenceForm()
    update_form = TaskUpdateForm(obj=task)
    complete_form = TaskCompleteForm()
    approval_form = TaskApprovalForm()

    # Obtener usuarios activos para asignación
    active_users = User.query.filter_by(is_active=True).order_by(User.username).all()

    return render_template(
        'tasks/view.html',
        task=task,
        comment_form=comment_form,
        evidence_form=evidence_form,
        update_form=update_form,
        complete_form=complete_form,
        approval_form=approval_form,
        active_users=active_users
    )


# ==================== CREAR TAREA MANUAL ====================

@tasks_bp.route('/new', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'Administrador', 'CISO', 'Auditor Interno', 'Propietario de Proceso'])
def create():
    """Crear una tarea manualmente"""

    form = TaskForm()

    # Poblar choices (usando None para valores opcionales en lugar de '')
    form.assigned_to_id.choices = [(0, 'Seleccionar usuario...')] + [
        (u.id, f"{u.first_name} {u.last_name}" if u.first_name else u.username)
        for u in User.query.filter_by(is_active=True).order_by(User.username).all()
    ]

    form.assigned_role_id.choices = [(0, 'Seleccionar rol...')] + [
        (r.id, r.name) for r in Role.query.order_by(Role.name).all()
    ]

    if form.validate_on_submit():
        try:
            # Procesar checklist: convertir texto a JSON
            checklist_json = None
            if form.checklist.data:
                checklist_lines = [line.strip() for line in form.checklist.data.split('\n') if line.strip()]
                if checklist_lines:
                    checklist_json = [{'text': line, 'completed': False} for line in checklist_lines]

            data = {
                'title': form.title.data,
                'description': form.description.data,
                'category': TaskCategory(form.category.data),
                'priority': TaskPriority(form.priority.data),
                'due_date': form.due_date.data,
                'assigned_to_id': form.assigned_to_id.data if form.assigned_to_id.data and form.assigned_to_id.data != 0 else None,
                'assigned_role_id': form.assigned_role_id.data if form.assigned_role_id.data and form.assigned_role_id.data != 0 else None,
                'iso_control': form.iso_control.data,
                'estimated_hours': form.estimated_hours.data,
                'checklist': checklist_json,
                'requires_approval': form.requires_approval.data
            }

            task = TaskService.create_manual_task(data, current_user.id)

            # Procesar controles SOA relacionados
            related_control_ids = request.form.getlist('related_controls')
            print(f"DEBUG: Control IDs recibidos: {related_control_ids}")
            if related_control_ids:
                # Convertir a enteros
                control_ids_int = [int(id) for id in related_control_ids if id]
                print(f"DEBUG: Control IDs convertidos: {control_ids_int}")
                controls = SOAControl.query.filter(SOAControl.id.in_(control_ids_int)).all()
                print(f"DEBUG: Controles encontrados: {len(controls)}")
                task.related_controls = controls
                db.session.commit()
                print(f"DEBUG: Controles guardados correctamente")

            # Enviar notificación si está asignada
            if task.assigned_to:
                try:
                    NotificationService.send_task_assignment_notification(task)
                except Exception as email_error:
                    print(f"Error enviando notificación: {email_error}")
                    # No fallar si falla el email

            flash(f'Tarea "{task.title}" creada correctamente', 'success')
            return redirect(url_for('tasks.view', id=task.id))

        except Exception as e:
            print(f"ERROR creando tarea: {e}")
            import traceback
            traceback.print_exc()
            flash(f'Error al crear la tarea: {str(e)}', 'danger')

    # Obtener controles SOA disponibles
    controls = SOAControl.query.order_by(SOAControl.control_id).all()

    return render_template('tasks/form.html', form=form, task=None, controls=controls)


# ==================== EDITAR TAREA ====================

@tasks_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'Administrador', 'CISO', 'Propietario de Proceso'])
def edit(id):
    """Editar todos los detalles de una tarea"""

    task = Task.query.get_or_404(id)

    # Verificar permisos
    if not (current_user.id == task.assigned_to_id or
            current_user.id == task.created_by_id or
            current_user.role.name in ['Administrador', 'CISO']):
        flash('No tienes permiso para editar esta tarea', 'danger')
        return redirect(url_for('tasks.view', id=id))

    form = TaskForm(obj=task)

    # Poblar choices
    form.assigned_to_id.choices = [(0, 'Seleccionar usuario...')] + [
        (u.id, f"{u.first_name} {u.last_name}" if u.first_name else u.username)
        for u in User.query.filter_by(is_active=True).order_by(User.username).all()
    ]

    form.assigned_role_id.choices = [(0, 'Seleccionar rol...')] + [
        (r.id, r.name) for r in Role.query.order_by(Role.name).all()
    ]

    # Pre-seleccionar valores actuales
    if request.method == 'GET':
        if task.assigned_to_id:
            form.assigned_to_id.data = task.assigned_to_id
        if task.assigned_role_id:
            form.assigned_role_id.data = task.assigned_role_id

        # Convertir checklist JSON a texto
        if task.checklist:
            try:
                # Manejar diferentes formatos de checklist
                checklist_lines = []
                if isinstance(task.checklist, list):
                    for item in task.checklist:
                        if isinstance(item, dict):
                            # Formato 1: [{'text': '...', 'completed': bool}, ...]
                            # Formato 2: [{'item': '...', 'completed': bool}, ...]
                            text = item.get('text') or item.get('item') or str(item)
                            checklist_lines.append(text)
                        elif isinstance(item, str):
                            # Formato: ['texto1', 'texto2', ...]
                            checklist_lines.append(item)
                        else:
                            # Otro formato, convertir a string
                            checklist_lines.append(str(item))
                elif isinstance(task.checklist, str):
                    # Si es string, usar directamente
                    form.checklist.data = task.checklist
                else:
                    # Formato desconocido
                    checklist_lines = [str(task.checklist)]

                if checklist_lines:
                    form.checklist.data = '\n'.join(checklist_lines)
            except Exception as e:
                print(f"Error procesando checklist: {e}")
                print(f"Checklist original: {task.checklist}")
                # En caso de error, dejar vacío
                form.checklist.data = ''

    if form.validate_on_submit():
        try:
            # Procesar checklist
            checklist_json = None
            if form.checklist.data:
                checklist_lines = [line.strip() for line in form.checklist.data.split('\n') if line.strip()]
                if checklist_lines:
                    # Preservar estado de items existentes si es posible
                    existing_checklist = task.checklist or []
                    checklist_json = []
                    for line in checklist_lines:
                        # Buscar si ya existía este item (buscar en 'text' o 'item')
                        existing_item = None
                        if isinstance(existing_checklist, list):
                            for item in existing_checklist:
                                if isinstance(item, dict):
                                    item_text = item.get('text') or item.get('item')
                                    if item_text == line:
                                        existing_item = item
                                        break

                        # Guardar siempre con formato 'text' (normalizado)
                        checklist_json.append({
                            'text': line,
                            'completed': existing_item.get('completed', False) if existing_item else False
                        })

            # Actualizar campos
            task.title = form.title.data
            task.description = form.description.data
            task.category = TaskCategory(form.category.data)
            task.priority = TaskPriority(form.priority.data)
            task.due_date = form.due_date.data
            task.assigned_to_id = form.assigned_to_id.data if form.assigned_to_id.data and form.assigned_to_id.data != 0 else None
            task.assigned_role_id = form.assigned_role_id.data if form.assigned_role_id.data and form.assigned_role_id.data != 0 else None
            task.iso_control = form.iso_control.data
            task.estimated_hours = form.estimated_hours.data
            task.checklist = checklist_json
            task.requires_approval = form.requires_approval.data
            task.updated_by_id = current_user.id

            # Procesar controles SOA relacionados
            related_control_ids = request.form.getlist('related_controls')
            if related_control_ids:
                control_ids_int = [int(id) for id in related_control_ids if id]
                controls = SOAControl.query.filter(SOAControl.id.in_(control_ids_int)).all()
                task.related_controls = controls

            db.session.commit()

            flash(f'Tarea "{task.title}" actualizada correctamente', 'success')
            return redirect(url_for('tasks.view', id=task.id))

        except Exception as e:
            print(f"ERROR actualizando tarea: {e}")
            import traceback
            traceback.print_exc()
            flash(f'Error al actualizar la tarea: {str(e)}', 'danger')

    # Obtener controles SOA disponibles
    controls = SOAControl.query.order_by(SOAControl.control_id).all()

    return render_template('tasks/form.html', form=form, task=task, controls=controls)


# ==================== ACTUALIZAR ESTADO/PROGRESO ====================

@tasks_bp.route('/<int:id>/update', methods=['POST'])
@login_required
def update(id):
    """Actualizar el estado y progreso de una tarea"""

    task = Task.query.get_or_404(id)

    # Verificar que el usuario puede actualizar esta tarea
    if current_user.id != task.assigned_to_id and current_user.role.name not in ['Administrador', 'CISO']:
        flash('No tienes permiso para actualizar esta tarea', 'danger')
        return redirect(url_for('tasks.view', id=id))

    form = TaskUpdateForm()

    if form.validate_on_submit():
        try:
            # Actualizar estado
            if form.status.data:
                new_status = TaskStatus(form.status.data)
                TaskService.update_task_status(
                    task.id,
                    new_status,
                    current_user.id,
                    observations=form.observations.data
                )

            # Actualizar progreso
            if form.progress.data is not None:
                task.progress = form.progress.data

            # Actualizar horas reales
            if form.actual_hours.data:
                task.actual_hours = form.actual_hours.data

            db.session.commit()

            flash('Tarea actualizada correctamente', 'success')

        except Exception as e:
            flash(f'Error al actualizar la tarea: {str(e)}', 'danger')

    return redirect(url_for('tasks.view', id=id))


# ==================== COMPLETAR TAREA ====================

@tasks_bp.route('/<int:id>/complete', methods=['POST'])
@login_required
def complete(id):
    """Marcar una tarea como completada"""

    task = Task.query.get_or_404(id)

    # Verificar permisos
    if current_user.id != task.assigned_to_id and current_user.role.name not in ['Administrador', 'CISO']:
        flash('No tienes permiso para completar esta tarea', 'danger')
        return redirect(url_for('tasks.view', id=id))

    form = TaskCompleteForm()

    if form.validate_on_submit():
        try:
            TaskService.complete_task(
                task.id,
                current_user.id,
                observations=form.observations.data,
                result=form.result.data,
                actual_hours=form.actual_hours.data
            )

            # Enviar notificación de completado
            NotificationService.send_task_completed_notification(task)

            flash('Tarea completada correctamente', 'success')

        except Exception as e:
            flash(f'Error al completar la tarea: {str(e)}', 'danger')

    return redirect(url_for('tasks.view', id=id))


# ==================== ASIGNAR TAREA ====================

@tasks_bp.route('/<int:id>/assign', methods=['POST'])
@login_required
@role_required(['admin', 'Administrador', 'CISO'])
def assign_task(id):
    """Asignar una tarea a un usuario"""

    task = Task.query.get_or_404(id)

    assigned_to_id = request.form.get('assigned_to_id', type=int)

    if not assigned_to_id:
        flash('Debes seleccionar un usuario', 'danger')
        return redirect(url_for('tasks.view', id=id))

    try:
        TaskService.assign_task(task.id, assigned_to_id, current_user.id)

        # Enviar notificación al nuevo asignado
        try:
            NotificationService.send_task_assignment_notification(task)
        except Exception as email_error:
            print(f"Error enviando notificación: {email_error}")
            # No fallar si falla el email

        flash('Tarea asignada correctamente', 'success')

    except Exception as e:
        print(f"Error asignando tarea: {e}")
        flash(f'Error al asignar tarea: {str(e)}', 'danger')

    return redirect(url_for('tasks.view', id=id))


# ==================== COMENTARIOS ====================

@tasks_bp.route('/<int:id>/comment', methods=['POST'])
@login_required
def add_comment(id):
    """Agregar un comentario a una tarea"""

    task = Task.query.get_or_404(id)
    form = TaskCommentForm()

    if form.validate_on_submit():
        try:
            TaskService.add_comment(
                task.id,
                current_user.id,
                form.comment.data,
                form.comment_type.data
            )

            flash('Comentario agregado', 'success')

        except Exception as e:
            flash(f'Error al agregar comentario: {str(e)}', 'danger')

    return redirect(url_for('tasks.view', id=id))


# ==================== EVIDENCIAS ====================

@tasks_bp.route('/<int:id>/evidence', methods=['POST'])
@login_required
def add_evidence(id):
    """Subir evidencia a una tarea"""

    task = Task.query.get_or_404(id)
    form = TaskEvidenceForm()

    if form.validate_on_submit():
        try:
            file = form.file.data

            if file:
                # Generar nombre seguro
                filename = secure_filename(file.filename)
                timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                unique_filename = f"{timestamp}_{filename}"

                # Crear directorio si no existe
                upload_folder = os.path.join('uploads', 'tasks', str(task.id))
                os.makedirs(upload_folder, exist_ok=True)

                # Guardar archivo
                file_path = os.path.join(upload_folder, unique_filename)
                file.save(file_path)

                # Registrar evidencia
                TaskService.add_evidence(
                    task.id,
                    current_user.id,
                    filename=unique_filename,
                    original_filename=filename,
                    file_path=file_path,
                    file_size=os.path.getsize(file_path),
                    mime_type=file.content_type,
                    description=form.description.data
                )

                flash('Evidencia subida correctamente', 'success')

        except Exception as e:
            flash(f'Error al subir evidencia: {str(e)}', 'danger')

    return redirect(url_for('tasks.view', id=id))


@tasks_bp.route('/evidence/<int:evidence_id>/download')
@login_required
def download_evidence(evidence_id):
    """Descargar archivo de evidencia"""

    evidence = TaskEvidence.query.get_or_404(evidence_id)

    # Verificar permisos
    task = evidence.task
    if not (current_user.id == task.assigned_to_id or
            current_user.id == task.created_by_id or
            current_user.role.name in ['Administrador', 'CISO', 'Auditor Interno']):
        flash('No tienes permiso para descargar esta evidencia', 'danger')
        return redirect(url_for('tasks.dashboard'))

    return send_file(
        evidence.file_path,
        as_attachment=True,
        download_name=evidence.original_filename
    )


@tasks_bp.route('/evidence/<int:evidence_id>/delete', methods=['POST'])
@login_required
def delete_evidence(evidence_id):
    """Eliminar evidencia de una tarea"""

    evidence = TaskEvidence.query.get_or_404(evidence_id)
    task = evidence.task

    # Verificar permisos: solo el creador de la evidencia, el asignado de la tarea o administradores
    if not (current_user.id == evidence.uploaded_by_id or
            current_user.id == task.assigned_to_id or
            current_user.id == task.created_by_id or
            current_user.role.name in ['Administrador', 'CISO']):
        flash('No tienes permiso para eliminar esta evidencia', 'danger')
        return redirect(url_for('tasks.view', id=task.id))

    try:
        # Eliminar archivo físico
        if os.path.exists(evidence.file_path):
            os.remove(evidence.file_path)

        # Eliminar registro de base de datos
        db.session.delete(evidence)
        db.session.commit()

        flash('Evidencia eliminada correctamente', 'success')
    except Exception as e:
        print(f"Error eliminando evidencia: {e}")
        flash(f'Error al eliminar evidencia: {str(e)}', 'danger')

    return redirect(url_for('tasks.view', id=task.id))


# ==================== PLANTILLAS DE TAREAS ====================

@tasks_bp.route('/templates')
@login_required
def templates():
    """Lista de plantillas de tareas"""

    templates = TaskTemplate.query.order_by(
        TaskTemplate.is_active.desc(),
        TaskTemplate.category.asc(),
        TaskTemplate.title.asc()
    ).all()

    categories = TaskCategory

    return render_template('tasks/templates.html', templates=templates, categories=categories)


@tasks_bp.route('/templates/new', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'Administrador', 'CISO'])
def create_template():
    """Crear una plantilla de tarea"""

    form = TaskTemplateForm()

    # Poblar choices
    form.default_assignee_id.choices = [(0, 'Sin asignar por defecto')] + [
        (u.id, f"{u.first_name} {u.last_name}" if u.first_name else u.username)
        for u in User.query.filter_by(is_active=True).order_by(User.username).all()
    ]

    form.default_role_id.choices = [(0, 'Sin rol por defecto')] + [
        (r.id, r.name) for r in Role.query.order_by(Role.name).all()
    ]

    if form.validate_on_submit():
        try:
            template = TaskTemplate(
                title=form.title.data,
                description=form.description.data,
                category=TaskCategory(form.category.data),
                frequency=TaskFrequency(form.frequency.data),
                priority=TaskPriority(form.priority.data),
                iso_control=form.iso_control.data,
                estimated_hours=form.estimated_hours.data,
                default_assignee_id=form.default_assignee_id.data if form.default_assignee_id.data and form.default_assignee_id.data != 0 else None,
                default_role_id=form.default_role_id.data if form.default_role_id.data and form.default_role_id.data != 0 else None,
                notify_days_before=form.notify_days_before.data,
                requires_evidence=form.requires_evidence.data,
                requires_approval=form.requires_approval.data,
                is_active=form.is_active.data,
                created_by_id=current_user.id
            )

            db.session.add(template)
            db.session.commit()

            flash(f'Plantilla "{template.title}" creada correctamente', 'success')
            return redirect(url_for('tasks.list_templates'))

        except Exception as e:
            flash(f'Error al crear la plantilla: {str(e)}', 'danger')

    return render_template('tasks/templates/create.html', form=form)


@tasks_bp.route('/templates/<int:id>')
@login_required
def view_template(id):
    """Ver detalle de una plantilla"""

    template = TaskTemplate.query.get_or_404(id)

    return render_template('tasks/template_view.html', template=template)


@tasks_bp.route('/templates/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'Administrador', 'CISO'])
def edit_template(id):
    """Editar una plantilla de tarea"""

    template = TaskTemplate.query.get_or_404(id)
    form = TaskTemplateForm(obj=template)

    # Poblar choices
    form.default_assignee_id.choices = [(0, 'Sin asignar por defecto')] + [
        (u.id, f"{u.first_name} {u.last_name}" if u.first_name else u.username)
        for u in User.query.filter_by(is_active=True).order_by(User.username).all()
    ]

    form.default_role_id.choices = [(0, 'Sin rol por defecto')] + [
        (r.id, r.name) for r in Role.query.order_by(Role.name).all()
    ]

    if form.validate_on_submit():
        try:
            template.title = form.title.data
            template.description = form.description.data
            template.category = TaskCategory(form.category.data)
            template.frequency = TaskFrequency(form.frequency.data)
            template.priority = TaskPriority(form.priority.data)
            template.iso_control = form.iso_control.data
            template.estimated_hours = form.estimated_hours.data
            template.default_assignee_id = form.default_assignee_id.data if form.default_assignee_id.data and form.default_assignee_id.data != 0 else None
            template.default_role_id = form.default_role_id.data if form.default_role_id.data and form.default_role_id.data != 0 else None
            template.notify_days_before = form.notify_days_before.data
            template.requires_evidence = form.requires_evidence.data
            template.requires_approval = form.requires_approval.data
            template.is_active = form.is_active.data
            template.updated_at = datetime.utcnow()

            db.session.commit()

            flash(f'Plantilla "{template.title}" actualizada correctamente', 'success')
            return redirect(url_for('tasks.templates'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar la plantilla: {str(e)}', 'danger')

    return render_template('tasks/template_form.html', form=form, template=template)


@tasks_bp.route('/templates/<int:id>/generate', methods=['POST'])
@login_required
@role_required(['admin', 'Administrador', 'CISO'])
def generate_from_template(id):
    """Generar una tarea desde una plantilla"""

    try:
        task = TaskService.create_task_from_template(id, current_user.id)

        # Determinar mensaje según si fue auto-asignada o tenía asignado predefinido
        template = TaskTemplate.query.get(id)
        if template.default_assignee_id:
            message = f'Tarea "{task.title}" generada y asignada a {task.assigned_to.first_name} {task.assigned_to.last_name}'
        else:
            message = f'Tarea "{task.title}" generada y auto-asignada a ti'

        # Enviar notificación si está asignada a alguien diferente del creador
        if task.assigned_to and task.assigned_to_id != current_user.id:
            try:
                NotificationService.send_task_assignment_notification(task)
                message += ' (notificación enviada)'
            except Exception as email_error:
                print(f"Error enviando notificación: {email_error}")
                message += ' (error al enviar notificación)'

        flash(message, 'success')
        return redirect(url_for('tasks.view', id=task.id))

    except Exception as e:
        print(f"Error generando tarea desde plantilla {id}: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error al generar tarea: {str(e)}', 'danger')
        return redirect(url_for('tasks.templates'))


# ==================== CALENDARIO ====================

@tasks_bp.route('/calendar')
@login_required
def calendar_view():
    """Vista de calendario de tareas - mensual o anual"""
    from calendar import monthrange, Calendar

    # Determinar vista (month o year)
    view = request.args.get('view', 'month')

    if view == 'year':
        return calendar_year_view()

    # Vista mensual
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)

    # Calcular mes anterior y siguiente
    if month == 1:
        prev_month = datetime(year - 1, 12, 1)
    else:
        prev_month = datetime(year, month - 1, 1)

    if month == 12:
        next_month = datetime(year + 1, 1, 1)
    else:
        next_month = datetime(year, month + 1, 1)

    # Obtener nombre del mes en español
    month_names_es = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    month_name = month_names_es[month]

    # Generar calendario del mes
    cal = Calendar(0)  # 0 = Lunes como primer día
    month_days = cal.monthdatescalendar(year, month)

    # Obtener tareas del usuario actual para todo el mes
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)

    # Expandir rango para incluir días de meses adyacentes visibles en el calendario
    if month_days:
        first_visible = month_days[0][0]
        last_visible = month_days[-1][-1]
        start_date = datetime.combine(first_visible, datetime.min.time())
        end_date = datetime.combine(last_visible, datetime.max.time())

    monthly_tasks = Task.query.filter(
        Task.assigned_to_id == current_user.id,
        Task.status.in_([TaskStatus.PENDIENTE, TaskStatus.EN_PROGRESO, TaskStatus.VENCIDA]),
        Task.due_date >= start_date,
        Task.due_date <= end_date
    ).order_by(Task.due_date.asc()).all()

    # Organizar tareas por fecha
    tasks_by_date = {}
    for task in monthly_tasks:
        date_key = task.due_date.strftime('%Y-%m-%d')
        if date_key not in tasks_by_date:
            tasks_by_date[date_key] = []
        tasks_by_date[date_key].append(task)

    # Obtener tareas próximas a vencer (siguiente semana)
    next_week = datetime.now() + timedelta(days=7)
    upcoming_tasks = Task.query.filter(
        Task.assigned_to_id == current_user.id,
        Task.status.in_([TaskStatus.PENDIENTE, TaskStatus.EN_PROGRESO]),
        Task.due_date >= datetime.now(),
        Task.due_date <= next_week
    ).order_by(Task.due_date.asc()).all()

    return render_template('tasks/calendar.html',
                         view='month',
                         year=year,
                         month=month,
                         month_name=month_name,
                         prev_month=prev_month,
                         next_month=next_month,
                         calendar_weeks=month_days,
                         tasks_by_date=tasks_by_date,
                         monthly_tasks=monthly_tasks,
                         upcoming_tasks=upcoming_tasks,
                         today=datetime.now().date(),
                         current_date=datetime.now())


def calendar_year_view():
    """Vista anual del calendario"""
    from calendar import monthrange, Calendar

    year = request.args.get('year', datetime.now().year, type=int)

    # Obtener todas las tareas del año
    start_date = datetime(year, 1, 1)
    end_date = datetime(year + 1, 1, 1)

    yearly_tasks = Task.query.filter(
        Task.assigned_to_id == current_user.id,
        Task.status.in_([TaskStatus.PENDIENTE, TaskStatus.EN_PROGRESO, TaskStatus.VENCIDA]),
        Task.due_date >= start_date,
        Task.due_date < end_date
    ).order_by(Task.due_date.asc()).all()

    # Organizar tareas por mes
    tasks_by_month = {i: [] for i in range(1, 13)}
    for task in yearly_tasks:
        tasks_by_month[task.due_date.month].append(task)

    # Estadísticas por mes
    stats_by_month = {}
    for month_num in range(1, 13):
        month_tasks = tasks_by_month[month_num]
        stats_by_month[month_num] = {
            'total': len(month_tasks),
            'critica': len([t for t in month_tasks if t.priority == TaskPriority.CRITICA]),
            'alta': len([t for t in month_tasks if t.priority == TaskPriority.ALTA]),
            'media': len([t for t in month_tasks if t.priority == TaskPriority.MEDIA]),
            'baja': len([t for t in month_tasks if t.priority == TaskPriority.BAJA]),
            'pendiente': len([t for t in month_tasks if t.status == TaskStatus.PENDIENTE]),
            'en_progreso': len([t for t in month_tasks if t.status == TaskStatus.EN_PROGRESO]),
            'vencida': len([t for t in month_tasks if t.status == TaskStatus.VENCIDA])
        }

    # Nombres de meses en español
    month_names_es = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }

    return render_template('tasks/calendar_year.html',
                         view='year',
                         year=year,
                         prev_year=year - 1,
                         next_year=year + 1,
                         tasks_by_month=tasks_by_month,
                         stats_by_month=stats_by_month,
                         month_names=month_names_es,
                         current_date=datetime.now())


# ==================== API JSON ====================

@tasks_bp.route('/api/stats')
@login_required
def api_stats():
    """API: Obtener estadísticas de tareas"""

    user_id = request.args.get('user_id', current_user.id, type=int)

    # Verificar permisos
    if user_id != current_user.id and current_user.role.name not in ['Administrador', 'CISO']:
        return jsonify({'error': 'No autorizado'}), 403

    stats = TaskService.get_task_statistics(user_id=user_id)

    return jsonify(stats)


@tasks_bp.route('/api/upcoming')
@login_required
def api_upcoming():
    """API: Tareas próximas a vencer"""

    days = request.args.get('days', 7, type=int)
    tasks = TaskService.get_tasks_due_soon(days=days, user_id=current_user.id)

    return jsonify([{
        'id': t.id,
        'title': t.title,
        'due_date': t.due_date.isoformat(),
        'priority': t.priority.value,
        'category': t.category.value,
        'days_until_due': t.days_until_due
    } for t in tasks])


# ==================== UTILIDADES ====================

@tasks_bp.context_processor
def utility_processor():
    """Funciones auxiliares para templates"""
    return {
        'TaskStatus': TaskStatus,
        'TaskPriority': TaskPriority,
        'TaskCategory': TaskCategory,
        'TaskFrequency': TaskFrequency
    }
