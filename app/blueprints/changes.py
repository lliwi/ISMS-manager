"""
Blueprint para gestión de cambios
ISO 27001:2023 - Control 6.3 y 8.32
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Asset, Incident, NonConformity, User
from app.models.change import (
    Change, ChangeApproval, ChangeTask, ChangeDocument, ChangeHistory,
    ChangeReview, ChangeRiskAssessment, ChangeAsset,
    ChangeType, ChangeCategory, ChangePriority, ChangeStatus, RiskLevel,
    ApprovalLevel, ApprovalStatus, TaskStatus, DocumentType, ReviewStatus
)
from app.services.change_service import ChangeService
from app.services.change_workflow import ChangeWorkflow
from datetime import datetime, timedelta
from sqlalchemy import or_, and_, func
from werkzeug.utils import secure_filename
import os

changes_bp = Blueprint('changes', __name__, url_prefix='/changes')

# Configuración de uploads
UPLOAD_FOLDER = 'uploads/changes'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'png', 'jpg', 'jpeg', 'log', 'zip'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ============================================================================
# VISTAS PRINCIPALES
# ============================================================================

@changes_bp.route('/')
@login_required
def index():
    """Dashboard de cambios"""
    # Filtros
    status_filter = request.args.get('status')
    category_filter = request.args.get('category')
    priority_filter = request.args.get('priority')
    type_filter = request.args.get('type')
    search = request.args.get('search', '')

    # Query base
    query = Change.query

    # Aplicar filtros
    if status_filter and status_filter != 'all':
        try:
            query = query.filter(Change.status == ChangeStatus[status_filter])
        except KeyError:
            flash('Estado no válido', 'error')

    if category_filter and category_filter != 'all':
        try:
            query = query.filter(Change.category == ChangeCategory[category_filter])
        except KeyError:
            flash('Categoría no válida', 'error')

    if priority_filter and priority_filter != 'all':
        try:
            query = query.filter(Change.priority == ChangePriority[priority_filter])
        except KeyError:
            flash('Prioridad no válida', 'error')

    if type_filter and type_filter != 'all':
        try:
            query = query.filter(Change.change_type == ChangeType[type_filter])
        except KeyError:
            flash('Tipo no válido', 'error')

    if search:
        query = query.filter(
            or_(
                Change.change_code.ilike(f'%{search}%'),
                Change.title.ilike(f'%{search}%'),
                Change.description.ilike(f'%{search}%')
            )
        )

    # Ordenar y paginar
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    changes_pagination = query.order_by(Change.requested_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    # Estadísticas rápidas
    stats = {
        'total': Change.query.count(),
        'pending': Change.query.filter(Change.status.in_([
            ChangeStatus.SUBMITTED, ChangeStatus.UNDER_REVIEW,
            ChangeStatus.PENDING_APPROVAL
        ])).count(),
        'scheduled': Change.query.filter(Change.status == ChangeStatus.SCHEDULED).count(),
        'in_progress': Change.query.filter(Change.status == ChangeStatus.IN_PROGRESS).count(),
        'this_month': Change.query.filter(
            Change.requested_date >= datetime.utcnow().replace(day=1)
        ).count()
    }

    return render_template('changes/index.html',
                          changes=changes_pagination.items,
                          pagination=changes_pagination,
                          stats=stats,
                          ChangeStatus=ChangeStatus,
                          ChangeCategory=ChangeCategory,
                          ChangePriority=ChangePriority,
                          ChangeType=ChangeType)


@changes_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """Crear nuevo cambio"""
    if request.method == 'POST':
        try:
            data = {
                'title': request.form.get('title'),
                'description': request.form.get('description'),
                'change_type': ChangeType[request.form.get('change_type')],
                'category': ChangeCategory[request.form.get('category', 'STANDARD')],
                'priority': ChangePriority[request.form.get('priority', 'MEDIUM')],
                'business_justification': request.form.get('business_justification'),
                'implementation_plan': request.form.get('implementation_plan'),
                'rollback_plan': request.form.get('rollback_plan'),
                'owner_id': int(request.form.get('owner_id', current_user.id))
            }

            # Campos opcionales
            if request.form.get('expected_benefits'):
                data['expected_benefits'] = request.form.get('expected_benefits')

            if request.form.get('impact_analysis'):
                data['impact_analysis'] = request.form.get('impact_analysis')

            if request.form.get('test_plan'):
                data['test_plan'] = request.form.get('test_plan')

            if request.form.get('estimated_duration'):
                data['estimated_duration'] = int(request.form.get('estimated_duration'))

            if request.form.get('scheduled_start_date'):
                data['scheduled_start_date'] = datetime.fromisoformat(
                    request.form.get('scheduled_start_date')
                )

            if request.form.get('scheduled_end_date'):
                data['scheduled_end_date'] = datetime.fromisoformat(
                    request.form.get('scheduled_end_date')
                )

            # Crear el cambio
            change = ChangeService.create_change(data, current_user.id)

            flash(f'Cambio {change.change_code} creado exitosamente', 'success')
            return redirect(url_for('changes.detail', change_id=change.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el cambio: {str(e)}', 'error')

    # GET - Mostrar formulario
    users = User.query.filter_by(is_active=True).order_by(User.username).all()

    return render_template('changes/form.html',
                          change=None,
                          users=users,
                          ChangeType=ChangeType,
                          ChangeCategory=ChangeCategory,
                          ChangePriority=ChangePriority)


@changes_bp.route('/<int:change_id>')
@login_required
def detail(change_id):
    """Detalle de un cambio"""
    change = Change.query.get_or_404(change_id)

    # Obtener próximas acciones disponibles
    next_actions = ChangeWorkflow.get_next_actions(change)

    # Obtener progreso
    progress = ChangeWorkflow.get_workflow_progress(change)

    # Obtener badge class
    badge_class = ChangeWorkflow.get_status_badge_class(change.status)

    # Determinar permisos del usuario actual
    # TODO: Implementar lógica de permisos basada en roles
    # Por ahora, permitir todas las acciones para testing
    can_edit = change.status in [ChangeStatus.DRAFT, ChangeStatus.SUBMITTED]
    can_approve = True  # TODO: Verificar rol de aprobador
    can_schedule = True  # TODO: Verificar rol de planificador
    can_implement = True  # TODO: Verificar rol de implementador

    return render_template('changes/detail.html',
                          change=change,
                          next_actions=next_actions,
                          progress=progress,
                          badge_class=badge_class,
                          can_edit=can_edit,
                          can_approve=can_approve,
                          can_schedule=can_schedule,
                          can_implement=can_implement,
                          ChangeWorkflow=ChangeWorkflow)


@changes_bp.route('/<int:change_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(change_id):
    """Editar un cambio"""
    change = Change.query.get_or_404(change_id)

    # Verificar si es editable
    if not ChangeWorkflow.is_editable(change.status):
        flash(f'No se puede editar un cambio en estado {change.status.value}', 'error')
        return redirect(url_for('changes.detail', change_id=change_id))

    if request.method == 'POST':
        try:
            data = {}

            # Campos editables
            editable_fields = [
                'title', 'description', 'change_type', 'category', 'priority',
                'business_justification', 'implementation_plan', 'rollback_plan',
                'expected_benefits', 'impact_analysis', 'test_plan',
                'communication_plan', 'owner_id', 'estimated_duration',
                'estimated_cost', 'scheduled_start_date', 'scheduled_end_date'
            ]

            for field in editable_fields:
                if field in request.form and request.form.get(field):
                    value = request.form.get(field)

                    # Conversiones de tipo
                    if field in ['change_type', 'category', 'priority']:
                        value = eval(field.split('_')[0].capitalize() + field.split('_')[1].capitalize())[value]
                    elif field in ['owner_id', 'estimated_duration']:
                        value = int(value)
                    elif field in ['estimated_cost']:
                        value = float(value)
                    elif field in ['scheduled_start_date', 'scheduled_end_date']:
                        value = datetime.fromisoformat(value)

                    data[field] = value

            ChangeService.update_change(change_id, data, current_user.id)

            flash('Cambio actualizado exitosamente', 'success')
            return redirect(url_for('changes.detail', change_id=change_id))

        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el cambio: {str(e)}', 'error')

    # GET - Mostrar formulario
    users = User.query.filter_by(is_active=True).order_by(User.username).all()

    return render_template('changes/form.html',
                          change=change,
                          users=users,
                          ChangeType=ChangeType,
                          ChangeCategory=ChangeCategory,
                          ChangePriority=ChangePriority)


# ============================================================================
# ACCIONES DE WORKFLOW
# ============================================================================

@changes_bp.route('/<int:change_id>/submit', methods=['POST'])
@login_required
def submit(change_id):
    """Enviar cambio para revisión"""
    try:
        change = ChangeService.submit_for_review(change_id, current_user.id)
        flash(f'Cambio {change.change_code} enviado para revisión', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(f'Error al enviar el cambio: {str(e)}', 'error')

    return redirect(url_for('changes.detail', change_id=change_id))


@changes_bp.route('/<int:change_id>/approve', methods=['POST'])
@login_required
def approve(change_id):
    """Aprobar un cambio"""
    try:
        comments = request.form.get('comments')
        conditions = request.form.get('conditions')

        approval = ChangeService.approve(change_id, current_user.id, comments, conditions)

        flash(f'Cambio aprobado exitosamente', 'success')
    except Exception as e:
        flash(f'Error al aprobar el cambio: {str(e)}', 'error')

    return redirect(url_for('changes.detail', change_id=change_id))


@changes_bp.route('/<int:change_id>/reject', methods=['POST'])
@login_required
def reject(change_id):
    """Rechazar un cambio"""
    try:
        comments = request.form.get('comments')

        if not comments:
            flash('Debe proporcionar comentarios para el rechazo', 'error')
            return redirect(url_for('changes.detail', change_id=change_id))

        approval = ChangeService.reject(change_id, current_user.id, comments)

        flash(f'Cambio rechazado', 'warning')
    except Exception as e:
        flash(f'Error al rechazar el cambio: {str(e)}', 'error')

    return redirect(url_for('changes.detail', change_id=change_id))


@changes_bp.route('/<int:change_id>/schedule', methods=['POST'])
@login_required
def schedule(change_id):
    """Programar o reprogramar implementación del cambio"""
    try:
        # Verificar si es una reprogramación
        change = Change.query.get_or_404(change_id)
        is_reschedule = change.scheduled_start_date is not None

        scheduled_date = request.form.get('scheduled_date')
        scheduled_time = request.form.get('scheduled_time')
        estimated_duration = request.form.get('estimated_duration')

        if not scheduled_date or not scheduled_time or not estimated_duration:
            flash('Debe proporcionar fecha, hora y duración estimada', 'error')
            return redirect(url_for('changes.detail', change_id=change_id))

        # Combinar fecha y hora en un datetime
        datetime_str = f"{scheduled_date} {scheduled_time}"
        start_date = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')

        # Calcular fecha de fin automáticamente sumando la duración en horas
        duration_hours = float(estimated_duration)
        end_date = start_date + timedelta(hours=duration_hours)

        change = ChangeService.schedule(change_id, start_date, end_date, current_user.id)

        action = 'reprogramado' if is_reschedule else 'programado'
        flash(f'Cambio {action} desde {start_date.strftime("%d/%m/%Y %H:%M")} hasta {end_date.strftime("%d/%m/%Y %H:%M")}', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(f'Error al programar el cambio: {str(e)}', 'error')

    return redirect(url_for('changes.detail', change_id=change_id))


@changes_bp.route('/<int:change_id>/start', methods=['POST'])
@login_required
def start(change_id):
    """Iniciar implementación del cambio"""
    try:
        change = ChangeService.start_implementation(change_id, current_user.id)
        flash(f'Implementación iniciada', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(f'Error al iniciar la implementación: {str(e)}', 'error')

    return redirect(url_for('changes.detail', change_id=change_id))


@changes_bp.route('/<int:change_id>/complete', methods=['POST'])
@login_required
def complete(change_id):
    """Completar implementación del cambio"""
    try:
        notes = request.form.get('implementation_notes')
        change = ChangeService.complete_implementation(change_id, current_user.id, notes)
        flash(f'Implementación completada', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(f'Error al completar la implementación: {str(e)}', 'error')

    return redirect(url_for('changes.detail', change_id=change_id))


@changes_bp.route('/<int:change_id>/close', methods=['POST'])
@login_required
def close(change_id):
    """Cerrar un cambio"""
    try:
        success = request.form.get('success', 'true') == 'true'
        change = ChangeService.close(change_id, current_user.id, success)
        flash(f'Cambio cerrado exitosamente', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(f'Error al cerrar el cambio: {str(e)}', 'error')

    return redirect(url_for('changes.detail', change_id=change_id))


@changes_bp.route('/<int:change_id>/rollback', methods=['POST'])
@login_required
def rollback(change_id):
    """Revertir un cambio"""
    try:
        reason = request.form.get('reason')

        if not reason:
            flash('Debe proporcionar una razón para el rollback', 'error')
            return redirect(url_for('changes.detail', change_id=change_id))

        change = ChangeService.rollback(change_id, current_user.id, reason)
        flash(f'Cambio revertido', 'warning')
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(f'Error al revertir el cambio: {str(e)}', 'error')

    return redirect(url_for('changes.detail', change_id=change_id))


@changes_bp.route('/<int:change_id>/cancel', methods=['POST'])
@login_required
def cancel(change_id):
    """Cancelar un cambio"""
    try:
        reason = request.form.get('reason')

        if not reason:
            flash('Debe proporcionar una razón para la cancelación', 'error')
            return redirect(url_for('changes.detail', change_id=change_id))

        change = ChangeService.cancel(change_id, current_user.id, reason)
        flash(f'Cambio cancelado', 'info')
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(f'Error al cancelar el cambio: {str(e)}', 'error')

    return redirect(url_for('changes.detail', change_id=change_id))


@changes_bp.route('/<int:change_id>/delete', methods=['POST'])
@login_required
def delete(change_id):
    """Eliminar un cambio (solo administradores)"""
    try:
        # Verificar que el usuario sea administrador
        if current_user.role.name != 'admin':
            flash('No tiene permisos para eliminar cambios', 'error')
            return redirect(url_for('changes.index'))

        change = Change.query.get_or_404(change_id)
        change_code = change.change_code

        # Eliminar todas las relaciones asociadas
        # Las relaciones con cascade='all, delete-orphan' se eliminarán automáticamente
        db.session.delete(change)
        db.session.commit()

        flash(f'Cambio {change_code} eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el cambio: {str(e)}', 'error')

    return redirect(url_for('changes.index'))


# ============================================================================
# TAREAS
# ============================================================================

@changes_bp.route('/<int:change_id>/tasks/add', methods=['POST'])
@login_required
def add_task(change_id):
    """Añadir tarea al cambio"""
    try:
        task_data = {
            'title': request.form.get('title'),
            'description': request.form.get('description'),
            'order': int(request.form.get('order', 0)),
            'is_critical': request.form.get('is_critical') == 'on',
            'assigned_to_id': int(request.form.get('assigned_to_id')) if request.form.get('assigned_to_id') else None,
            'estimated_duration': int(request.form.get('estimated_duration')) if request.form.get('estimated_duration') else None
        }

        task = ChangeService.add_task(change_id, task_data, current_user.id)

        flash(f'Tarea añadida exitosamente', 'success')
    except Exception as e:
        flash(f'Error al añadir tarea: {str(e)}', 'error')

    return redirect(url_for('changes.detail', change_id=change_id))


# ============================================================================
# EVALUACIÓN DE RIESGOS
# ============================================================================

@changes_bp.route('/<int:change_id>/risks/add', methods=['POST'])
@login_required
def add_risk(change_id):
    """Añadir evaluación de riesgo"""
    try:
        risk_data = {
            'description': request.form.get('description'),
            'probability': int(request.form.get('probability')),
            'impact': int(request.form.get('impact')),
            'mitigation_measures': request.form.get('mitigation_measures'),
            'contingency_plan': request.form.get('contingency_plan')
        }

        risk = ChangeService.add_risk_assessment(change_id, risk_data, current_user.id)

        flash(f'Evaluación de riesgo añadida - Nivel: {risk.risk_level.value}', 'success')
    except Exception as e:
        flash(f'Error al añadir evaluación de riesgo: {str(e)}', 'error')

    return redirect(url_for('changes.detail', change_id=change_id))


# ============================================================================
# REVISIÓN POST-IMPLEMENTACIÓN
# ============================================================================

@changes_bp.route('/<int:change_id>/review', methods=['POST'])
@login_required
def add_review(change_id):
    """Añadir revisión post-implementación"""
    try:
        review_data = {
            'success_status': ReviewStatus[request.form.get('success_status')],
            'objectives_met': request.form.get('objectives_met') == 'on',
            'success_criteria_met': request.form.get('success_criteria_met') == 'on',
            'lessons_learned': request.form.get('lessons_learned'),
            'what_went_well': request.form.get('what_went_well'),
            'what_went_wrong': request.form.get('what_went_wrong'),
            'issues_found': request.form.get('issues_found'),
            'recommendations': request.form.get('recommendations'),
            'downtime_occurred': int(request.form.get('downtime_occurred')) if request.form.get('downtime_occurred') else None,
            'incidents_caused': int(request.form.get('incidents_caused')) if request.form.get('incidents_caused') else None,
            'rollback_required': request.form.get('rollback_required') == 'on'
        }

        review = ChangeService.add_review(change_id, review_data, current_user.id)

        flash(f'Revisión post-implementación registrada', 'success')
    except Exception as e:
        flash(f'Error al registrar revisión: {str(e)}', 'error')

    return redirect(url_for('changes.detail', change_id=change_id))


# ============================================================================
# CALENDARIO
# ============================================================================

@changes_bp.route('/calendar')
@login_required
def calendar():
    """Vista de calendario de cambios"""
    # Estados finales que no deben mostrarse en el calendario
    excluded_statuses = [
        ChangeStatus.CANCELLED,
        ChangeStatus.CLOSED,
        ChangeStatus.FAILED,
        ChangeStatus.ROLLED_BACK
    ]

    # Obtener cambios programados (con fecha programada y no en estado final)
    scheduled_changes = Change.query.filter(
        Change.scheduled_start_date.isnot(None),
        ~Change.status.in_(excluded_statuses)
    ).order_by(Change.scheduled_start_date).all()

    # Para la tabla de próximos cambios (próximos 30 días)
    from datetime import datetime, timedelta
    now = datetime.utcnow()
    thirty_days_later = now + timedelta(days=30)

    upcoming_changes = Change.query.filter(
        Change.scheduled_start_date.isnot(None),
        Change.scheduled_start_date >= now,
        Change.scheduled_start_date <= thirty_days_later,
        ~Change.status.in_(excluded_statuses)
    ).order_by(Change.scheduled_start_date).all()

    return render_template('changes/calendar.html',
                          scheduled_changes=scheduled_changes,
                          upcoming_changes=upcoming_changes,
                          ChangeCategory=ChangeCategory,
                          ChangePriority=ChangePriority)


# ============================================================================
# API ENDPOINTS (JSON)
# ============================================================================

@changes_bp.route('/api/pending-approvals')
@login_required
def api_pending_approvals():
    """API: Obtener cambios pendientes de aprobación del usuario"""
    changes = ChangeService.get_pending_approvals(current_user.id)
    return jsonify([change.to_dict() for change in changes])


@changes_bp.route('/api/<int:change_id>')
@login_required
def api_detail(change_id):
    """API: Obtener detalle de un cambio"""
    change = Change.query.get_or_404(change_id)
    return jsonify(change.to_dict())


@changes_bp.route('/api/<int:change_id>/history')
@login_required
def api_history(change_id):
    """API: Obtener historial de un cambio"""
    history = ChangeHistory.query.filter_by(change_id=change_id).order_by(
        ChangeHistory.changed_at.desc()
    ).all()

    return jsonify([{
        'id': h.id,
        'field_changed': h.field_changed,
        'old_value': h.old_value,
        'new_value': h.new_value,
        'changed_by': {
            'id': h.changed_by.id,
            'name': h.changed_by.name
        } if h.changed_by else None,
        'changed_at': h.changed_at.isoformat(),
        'comments': h.comments
    } for h in history])
