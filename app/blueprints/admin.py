from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import User, Role, AuditLog, DocumentType, ISOVersion, AssetType, AssetCategory, DepreciationPeriod, db
from app.risks.models import Amenaza
from app.forms.user_forms import UserCreateForm, UserEditForm, ChangePasswordForm, ResetPasswordForm, UserSearchForm
from utils.decorators import role_required, audit_action
from utils.audit_helper import log_user_changes, log_password_change, log_account_lock, log_account_unlock, get_user_activity
from datetime import datetime
from sqlalchemy import or_

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
@login_required
@role_required('admin', 'ciso')
def index():
    """Panel de administración principal"""
    users_count = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    inactive_users = users_count - active_users

    # Usuarios bloqueados
    locked_users = User.query.filter(User.account_locked_until.isnot(None)).count()

    # Usuarios con contraseña expirada
    users_need_password_change = sum(1 for u in User.query.all() if u.needs_password_change())

    # Actividad reciente
    recent_activity = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(10).all()

    # Estadísticas por rol
    role_stats = db.session.query(Role.name, db.func.count(User.id))\
                           .join(User)\
                           .group_by(Role.name)\
                           .all()

    return render_template('admin/index.html',
                         users_count=users_count,
                         active_users=active_users,
                         inactive_users=inactive_users,
                         locked_users=locked_users,
                         users_need_password_change=users_need_password_change,
                         recent_activity=recent_activity,
                         role_stats=role_stats)

@admin_bp.route('/users')
@login_required
@role_required('admin', 'ciso')
def users():
    """Lista de usuarios con filtros y búsqueda"""
    page = request.args.get('page', 1, type=int)
    per_page = 20

    # Construir query base
    query = User.query

    # Aplicar filtros
    search = request.args.get('search', '')
    if search:
        query = query.filter(
            or_(
                User.username.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%'),
                User.first_name.ilike(f'%{search}%'),
                User.last_name.ilike(f'%{search}%')
            )
        )

    role_filter = request.args.get('role', type=int)
    if role_filter:
        query = query.filter_by(role_id=role_filter)

    status_filter = request.args.get('status', '')
    if status_filter == 'active':
        query = query.filter_by(is_active=True)
    elif status_filter == 'inactive':
        query = query.filter_by(is_active=False)

    department_filter = request.args.get('department', '')
    if department_filter:
        query = query.filter(User.department.ilike(f'%{department_filter}%'))

    # Ordenar
    sort_by = request.args.get('sort', 'username')
    if sort_by == 'username':
        query = query.order_by(User.username)
    elif sort_by == 'email':
        query = query.order_by(User.email)
    elif sort_by == 'created_at':
        query = query.order_by(User.created_at.desc())

    # Paginar
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    users_list = pagination.items

    # Roles para filtro
    roles = Role.query.all()

    return render_template('admin/users.html',
                         users=users_list,
                         pagination=pagination,
                         roles=roles,
                         search=search,
                         role_filter=role_filter,
                         status_filter=status_filter,
                         department_filter=department_filter)


@admin_bp.route('/users/new', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'ciso')
def create_user():
    """Crear nuevo usuario"""
    form = UserCreateForm()

    # Llenar choices de roles
    form.role_id.choices = [(r.id, r.description) for r in Role.query.all()]

    if form.validate_on_submit():
        try:
            # Crear usuario
            user = User(
                username=form.username.data,
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                phone=form.phone.data,
                department=form.department.data,
                position=form.position.data,
                role_id=form.role_id.data,
                is_active=form.is_active.data,
                must_change_password=form.must_change_password.data,
                created_by_id=current_user.id
            )

            # Establecer contraseña
            user.set_password(form.password.data)

            db.session.add(user)
            db.session.flush()  # Para obtener el ID

            # Registrar en audit log
            log_user_changes(
                user=user,
                old_data=None,
                new_data={
                    'username': user.username,
                    'email': user.email,
                    'role_id': user.role_id,
                    'department': user.department
                },
                action='create'
            )

            db.session.commit()

            flash(f'Usuario {user.username} creado correctamente', 'success')
            return redirect(url_for('admin.users'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear usuario: {str(e)}', 'danger')

    return render_template('admin/create_user.html', form=form)


@admin_bp.route('/users/<int:user_id>')
@login_required
@role_required('admin', 'ciso')
def view_user(user_id):
    """Ver detalle de un usuario"""
    user = User.query.get_or_404(user_id)

    # Obtener actividad reciente del usuario
    user_activity = get_user_activity(user_id, limit=50)

    return render_template('admin/view_user.html',
                         user=user,
                         user_activity=user_activity)


@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'ciso')
def edit_user(user_id):
    """Editar usuario"""
    user = User.query.get_or_404(user_id)
    form = UserEditForm(obj=user)

    # Llenar choices de roles
    form.role_id.choices = [(r.id, r.description) for r in Role.query.all()]

    if form.validate_on_submit():
        try:
            # Guardar valores antiguos para audit
            old_data = {
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': user.phone,
                'department': user.department,
                'position': user.position,
                'role_id': user.role_id,
                'is_active': user.is_active
            }

            # Actualizar usuario
            user.email = form.email.data
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.phone = form.phone.data
            user.department = form.department.data
            user.position = form.position.data
            user.role_id = form.role_id.data
            user.is_active = form.is_active.data
            user.updated_by_id = current_user.id
            user.updated_at = datetime.utcnow()

            # Nuevos valores
            new_data = {
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': user.phone,
                'department': user.department,
                'position': user.position,
                'role_id': user.role_id,
                'is_active': user.is_active
            }

            # Registrar cambios
            log_user_changes(user, old_data, new_data, action='update')

            db.session.commit()

            flash(f'Usuario {user.username} actualizado correctamente', 'success')
            return redirect(url_for('admin.view_user', user_id=user.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar usuario: {str(e)}', 'danger')

    return render_template('admin/edit_user.html', form=form, user=user)


@admin_bp.route('/users/<int:user_id>/reset-password', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'ciso')
def reset_password(user_id):
    """Resetear contraseña de usuario"""
    user = User.query.get_or_404(user_id)
    form = ResetPasswordForm()

    if form.validate_on_submit():
        try:
            # Cambiar contraseña
            user.set_password(form.new_password.data)
            user.must_change_password = form.must_change_password.data
            user.updated_by_id = current_user.id

            # Registrar cambio
            log_password_change(user, changed_by_admin=True)

            db.session.commit()

            flash(f'Contraseña del usuario {user.username} reseteada correctamente', 'success')

            # TODO: Enviar email si notify_user está marcado
            if form.notify_user.data:
                flash('Función de notificación por email pendiente de implementar', 'info')

            return redirect(url_for('admin.view_user', user_id=user.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al resetear contraseña: {str(e)}', 'danger')

    return render_template('admin/reset_password.html', form=form, user=user)


@admin_bp.route('/users/<int:user_id>/unlock', methods=['POST'])
@login_required
@role_required('admin', 'ciso')
def unlock_user(user_id):
    """Desbloquear cuenta de usuario"""
    user = User.query.get_or_404(user_id)

    try:
        user.reset_failed_login()
        log_account_unlock(user)

        db.session.commit()

        flash(f'Cuenta de {user.username} desbloqueada correctamente', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error al desbloquear cuenta: {str(e)}', 'danger')

    return redirect(url_for('admin.view_user', user_id=user.id))


@admin_bp.route('/users/<int:user_id>/toggle-active', methods=['POST'])
@login_required
@role_required('admin', 'ciso')
def toggle_active(user_id):
    """Activar/Desactivar usuario"""
    user = User.query.get_or_404(user_id)

    # No permitir desactivar propio usuario
    if user.id == current_user.id:
        flash('No puedes desactivar tu propia cuenta', 'warning')
        return redirect(url_for('admin.view_user', user_id=user.id))

    try:
        old_status = user.is_active
        user.is_active = not user.is_active
        user.updated_by_id = current_user.id

        # Registrar cambio
        log_user_changes(
            user,
            {'is_active': old_status},
            {'is_active': user.is_active},
            action='update'
        )

        db.session.commit()

        status_text = 'activado' if user.is_active else 'desactivado'
        flash(f'Usuario {user.username} {status_text} correctamente', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error al cambiar estado: {str(e)}', 'danger')

    return redirect(url_for('admin.view_user', user_id=user.id))


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_user(user_id):
    """Eliminar usuario (solo admin)"""
    user = User.query.get_or_404(user_id)

    # No permitir eliminar propio usuario
    if user.id == current_user.id:
        flash('No puedes eliminar tu propia cuenta', 'warning')
        return redirect(url_for('admin.users'))

    try:
        username = user.username

        # Registrar eliminación antes de borrar
        log_user_changes(
            user,
            {
                'username': user.username,
                'email': user.email,
                'role_id': user.role_id
            },
            None,
            action='delete'
        )

        db.session.delete(user)
        db.session.commit()

        flash(f'Usuario {username} eliminado correctamente', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar usuario: {str(e)}', 'danger')

    return redirect(url_for('admin.users'))


@admin_bp.route('/audit-logs')
@login_required
@role_required('admin', 'ciso', 'auditor')
def audit_logs():
    """Ver logs de auditoría"""
    page = request.args.get('page', 1, type=int)
    per_page = 50

    # Filtros
    action_filter = request.args.get('action', '')
    user_filter = request.args.get('user_id', type=int)
    entity_filter = request.args.get('entity_type', '')

    query = AuditLog.query

    if action_filter:
        query = query.filter_by(action=action_filter)

    if user_filter:
        query = query.filter_by(user_id=user_filter)

    if entity_filter:
        query = query.filter_by(entity_type=entity_filter)

    query = query.order_by(AuditLog.created_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    logs = pagination.items

    # Obtener acciones únicas para filtro
    actions = db.session.query(AuditLog.action).distinct().all()
    actions = [a[0] for a in actions]

    # Obtener tipos de entidad únicos
    entity_types = db.session.query(AuditLog.entity_type).distinct().all()
    entity_types = [e[0] for e in entity_types if e[0]]

    return render_template('admin/audit_logs.html',
                         logs=logs,
                         pagination=pagination,
                         actions=actions,
                         entity_types=entity_types,
                         action_filter=action_filter,
                         user_filter=user_filter,
                         entity_filter=entity_filter)


# ========================================================================
# CONFIGURACIÓN DEL SISTEMA
# ========================================================================

@admin_bp.route('/settings')
@login_required
@role_required('admin', 'ciso')
def settings():
    """Página de configuración general del sistema"""
    doc_types_count = DocumentType.query.count()
    iso_versions_count = ISOVersion.query.count()
    asset_types_count = AssetType.query.count()
    amenazas_count = Amenaza.query.count()

    return render_template('admin/settings.html',
                         doc_types_count=doc_types_count,
                         iso_versions_count=iso_versions_count,
                         asset_types_count=asset_types_count,
                         amenazas_count=amenazas_count)


@admin_bp.route('/settings/document-types')
@login_required
@role_required('admin', 'ciso')
def document_types():
    """Gestión de tipos de documentos"""
    doc_types = DocumentType.query.order_by(DocumentType.order).all()
    return render_template('admin/document_types.html', document_types=doc_types)


@admin_bp.route('/settings/document-types/new', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'ciso')
def create_document_type():
    """Crea un nuevo tipo de documento"""
    if request.method == 'POST':
        try:
            code = request.form.get('code')
            name = request.form.get('name')
            description = request.form.get('description')
            review_period_months = request.form.get('review_period_months')
            requires_approval = request.form.get('requires_approval') == 'on'
            approval_workflow = request.form.get('approval_workflow')
            icon = request.form.get('icon')
            color = request.form.get('color')
            is_active = request.form.get('is_active') == 'on'
            order = request.form.get('order')

            # Validaciones
            if not code or not name:
                flash('Los campos Código y Nombre son obligatorios', 'danger')
                return render_template('admin/document_type_form.html', form_data=request.form)

            # Verificar que el código no exista
            existing_type = DocumentType.query.filter_by(code=code).first()
            if existing_type:
                flash(f'Ya existe un tipo de documento con el código {code}', 'danger')
                return render_template('admin/document_type_form.html', form_data=request.form)

            new_type = DocumentType(
                code=code,
                name=name,
                description=description,
                review_period_months=int(review_period_months) if review_period_months else 12,
                requires_approval=requires_approval,
                approval_workflow=approval_workflow,
                icon=icon or 'fa-file',
                color=color or 'primary',
                is_active=is_active,
                order=int(order) if order else 0
            )

            db.session.add(new_type)
            db.session.commit()

            flash(f'Tipo de documento {name} creado exitosamente', 'success')
            return redirect(url_for('admin.document_types'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el tipo de documento: {str(e)}', 'danger')
            return render_template('admin/document_type_form.html', form_data=request.form)

    return render_template('admin/document_type_form.html', form_data=None)


@admin_bp.route('/settings/document-types/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'ciso')
def edit_document_type(id):
    """Edita un tipo de documento existente"""
    doc_type = DocumentType.query.get_or_404(id)

    if request.method == 'POST':
        try:
            code = request.form.get('code')
            name = request.form.get('name')
            description = request.form.get('description')
            review_period_months = request.form.get('review_period_months')
            requires_approval = request.form.get('requires_approval') == 'on'
            approval_workflow = request.form.get('approval_workflow')
            icon = request.form.get('icon')
            color = request.form.get('color')
            is_active = request.form.get('is_active') == 'on'
            order = request.form.get('order')

            # Validaciones
            if not code or not name:
                flash('Los campos Código y Nombre son obligatorios', 'danger')
                return render_template('admin/document_type_form.html', doc_type=doc_type, form_data=request.form)

            # Verificar que el código no exista (excepto el actual)
            existing_type = DocumentType.query.filter_by(code=code).first()
            if existing_type and existing_type.id != id:
                flash(f'Ya existe un tipo de documento con el código {code}', 'danger')
                return render_template('admin/document_type_form.html', doc_type=doc_type, form_data=request.form)

            doc_type.code = code
            doc_type.name = name
            doc_type.description = description
            doc_type.review_period_months = int(review_period_months) if review_period_months else 12
            doc_type.requires_approval = requires_approval
            doc_type.approval_workflow = approval_workflow
            doc_type.icon = icon or 'fa-file'
            doc_type.color = color or 'primary'
            doc_type.is_active = is_active
            doc_type.order = int(order) if order else 0
            doc_type.updated_at = datetime.utcnow()

            db.session.commit()

            flash(f'Tipo de documento {name} actualizado exitosamente', 'success')
            return redirect(url_for('admin.document_types'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el tipo de documento: {str(e)}', 'danger')
            return render_template('admin/document_type_form.html', doc_type=doc_type, form_data=request.form)

    return render_template('admin/document_type_form.html', doc_type=doc_type, form_data=None)


@admin_bp.route('/settings/document-types/<int:id>/delete', methods=['POST'])
@login_required
@role_required('admin', 'ciso')
def delete_document_type(id):
    """Elimina un tipo de documento"""
    doc_type = DocumentType.query.get_or_404(id)

    try:
        # Verificar si el tipo está siendo usado en documentos
        if doc_type.documents:
            flash(f'No se puede eliminar el tipo de documento {doc_type.name} porque está siendo usado en {len(doc_type.documents)} documento(s)', 'danger')
            return redirect(url_for('admin.document_types'))

        db.session.delete(doc_type)
        db.session.commit()

        flash(f'Tipo de documento {doc_type.name} eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el tipo de documento: {str(e)}', 'danger')

    return redirect(url_for('admin.document_types'))


@admin_bp.route('/settings/document-types/<int:id>/toggle-active', methods=['POST'])
@login_required
@role_required('admin', 'ciso')
def toggle_document_type_active(id):
    """Activa o desactiva un tipo de documento"""
    doc_type = DocumentType.query.get_or_404(id)

    try:
        doc_type.is_active = not doc_type.is_active
        doc_type.updated_at = datetime.utcnow()
        db.session.commit()

        status = 'activado' if doc_type.is_active else 'desactivado'
        flash(f'Tipo de documento {doc_type.name} {status} exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al cambiar el estado del tipo de documento: {str(e)}', 'danger')

    return redirect(url_for('admin.document_types'))


@admin_bp.route('/settings/iso-versions')
@login_required
@role_required('admin', 'ciso')
def iso_versions():
    """Gestión de versiones ISO"""
    iso_versions_list = ISOVersion.query.order_by(ISOVersion.year.desc()).all()
    return render_template('admin/iso_versions.html', iso_versions=iso_versions_list)


@admin_bp.route('/settings/iso-versions/new', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'ciso')
def create_iso_version():
    """Crea una nueva versión ISO"""
    if request.method == 'POST':
        try:
            version = request.form.get('version')
            year = request.form.get('year')
            title = request.form.get('title')
            description = request.form.get('description')
            number_of_controls = request.form.get('number_of_controls')
            is_active = request.form.get('is_active') == 'on'

            # Validaciones
            if not version or not year or not title:
                flash('Los campos Versión, Año y Título son obligatorios', 'danger')
                return render_template('admin/iso_version_form.html', form_data=request.form)

            # Verificar que la versión no exista
            existing_version = ISOVersion.query.filter_by(version=version).first()
            if existing_version:
                flash(f'Ya existe una versión ISO con el código {version}', 'danger')
                return render_template('admin/iso_version_form.html', form_data=request.form)

            new_version = ISOVersion(
                version=version,
                year=int(year),
                title=title,
                description=description,
                number_of_controls=int(number_of_controls) if number_of_controls else None,
                is_active=is_active
            )

            db.session.add(new_version)
            db.session.commit()

            flash(f'Versión ISO {version} creada exitosamente', 'success')
            return redirect(url_for('admin.iso_versions'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear la versión ISO: {str(e)}', 'danger')
            return render_template('admin/iso_version_form.html', form_data=request.form)

    return render_template('admin/iso_version_form.html', form_data=None)


@admin_bp.route('/settings/iso-versions/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'ciso')
def edit_iso_version(id):
    """Edita una versión ISO existente"""
    version = ISOVersion.query.get_or_404(id)

    if request.method == 'POST':
        try:
            version_code = request.form.get('version')
            year = request.form.get('year')
            title = request.form.get('title')
            description = request.form.get('description')
            number_of_controls = request.form.get('number_of_controls')
            is_active = request.form.get('is_active') == 'on'

            # Validaciones
            if not version_code or not year or not title:
                flash('Los campos Versión, Año y Título son obligatorios', 'danger')
                return render_template('admin/iso_version_form.html', version=version, form_data=request.form)

            # Verificar que la versión no exista (excepto la actual)
            existing_version = ISOVersion.query.filter_by(version=version_code).first()
            if existing_version and existing_version.id != id:
                flash(f'Ya existe una versión ISO con el código {version_code}', 'danger')
                return render_template('admin/iso_version_form.html', version=version, form_data=request.form)

            version.version = version_code
            version.year = int(year)
            version.title = title
            version.description = description
            version.number_of_controls = int(number_of_controls) if number_of_controls else None
            version.is_active = is_active
            version.updated_at = datetime.utcnow()

            db.session.commit()

            flash(f'Versión ISO {version_code} actualizada exitosamente', 'success')
            return redirect(url_for('admin.iso_versions'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar la versión ISO: {str(e)}', 'danger')
            return render_template('admin/iso_version_form.html', version=version, form_data=request.form)

    return render_template('admin/iso_version_form.html', version=version, form_data=None)


@admin_bp.route('/settings/iso-versions/<int:id>/delete', methods=['POST'])
@login_required
@role_required('admin', 'ciso')
def delete_iso_version(id):
    """Elimina una versión ISO"""
    version = ISOVersion.query.get_or_404(id)

    try:
        # TODO: Verificar si la versión está siendo usada en algún SOA
        # Si está en uso, no permitir eliminar
        db.session.delete(version)
        db.session.commit()

        flash(f'Versión ISO {version.version} eliminada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar la versión ISO: {str(e)}', 'danger')

    return redirect(url_for('admin.iso_versions'))


@admin_bp.route('/settings/iso-versions/<int:id>/toggle-active', methods=['POST'])
@login_required
@role_required('admin', 'ciso')
def toggle_iso_version_active(id):
    """Activa o desactiva una versión ISO"""
    version = ISOVersion.query.get_or_404(id)

    try:
        version.is_active = not version.is_active
        version.updated_at = datetime.utcnow()
        db.session.commit()

        status = 'activada' if version.is_active else 'desactivada'
        flash(f'Versión ISO {version.version} {status} exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al cambiar el estado de la versión ISO: {str(e)}', 'danger')

    return redirect(url_for('admin.iso_versions'))


# ========================================================================
# TIPOS DE ACTIVOS
# ========================================================================

@admin_bp.route('/settings/asset-types')
@login_required
@role_required('admin', 'ciso')
def asset_types():
    """Gestión de tipos de activos"""
    asset_types_list = AssetType.query.order_by(AssetType.category, AssetType.order).all()
    return render_template('admin/asset_types.html', asset_types=asset_types_list)


@admin_bp.route('/settings/asset-types/new', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'ciso')
def create_asset_type():
    """Crea un nuevo tipo de activo"""
    if request.method == 'POST':
        try:
            code = request.form.get('code')
            name = request.form.get('name')
            description = request.form.get('description')
            category = request.form.get('category')
            icon = request.form.get('icon')
            color = request.form.get('color')
            is_active = request.form.get('is_active') == 'on'
            order = request.form.get('order')

            # Validaciones
            if not code or not name or not category:
                flash('Los campos Código, Nombre y Categoría son obligatorios', 'danger')
                return render_template('admin/asset_type_form.html',
                                     form_data=request.form,
                                     categories=AssetCategory)

            # Verificar que el código no exista
            existing_type = AssetType.query.filter_by(code=code).first()
            if existing_type:
                flash(f'Ya existe un tipo de activo con el código {code}', 'danger')
                return render_template('admin/asset_type_form.html',
                                     form_data=request.form,
                                     categories=AssetCategory)

            new_type = AssetType(
                code=code,
                name=name,
                description=description,
                category=AssetCategory[category],
                icon=icon or 'fa-cube',
                color=color or 'primary',
                is_active=is_active,
                order=int(order) if order else 0
            )

            db.session.add(new_type)
            db.session.commit()

            flash(f'Tipo de activo {name} creado exitosamente', 'success')
            return redirect(url_for('admin.asset_types'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el tipo de activo: {str(e)}', 'danger')
            return render_template('admin/asset_type_form.html',
                                 form_data=request.form,
                                 categories=AssetCategory)

    return render_template('admin/asset_type_form.html',
                         form_data=None,
                         categories=AssetCategory)


@admin_bp.route('/settings/asset-types/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'ciso')
def edit_asset_type(id):
    """Edita un tipo de activo existente"""
    asset_type = AssetType.query.get_or_404(id)

    if request.method == 'POST':
        try:
            code = request.form.get('code')
            name = request.form.get('name')
            description = request.form.get('description')
            category = request.form.get('category')
            icon = request.form.get('icon')
            color = request.form.get('color')
            is_active = request.form.get('is_active') == 'on'
            order = request.form.get('order')

            # Validaciones
            if not code or not name or not category:
                flash('Los campos Código, Nombre y Categoría son obligatorios', 'danger')
                return render_template('admin/asset_type_form.html',
                                     asset_type=asset_type,
                                     form_data=request.form,
                                     categories=AssetCategory)

            # Verificar que el código no exista (excepto el actual)
            existing_type = AssetType.query.filter_by(code=code).first()
            if existing_type and existing_type.id != id:
                flash(f'Ya existe un tipo de activo con el código {code}', 'danger')
                return render_template('admin/asset_type_form.html',
                                     asset_type=asset_type,
                                     form_data=request.form,
                                     categories=AssetCategory)

            asset_type.code = code
            asset_type.name = name
            asset_type.description = description
            asset_type.category = AssetCategory[category]
            asset_type.icon = icon or 'fa-cube'
            asset_type.color = color or 'primary'
            asset_type.is_active = is_active
            asset_type.order = int(order) if order else 0
            asset_type.updated_at = datetime.utcnow()

            db.session.commit()

            flash(f'Tipo de activo {name} actualizado exitosamente', 'success')
            return redirect(url_for('admin.asset_types'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el tipo de activo: {str(e)}', 'danger')
            return render_template('admin/asset_type_form.html',
                                 asset_type=asset_type,
                                 form_data=request.form,
                                 categories=AssetCategory)

    return render_template('admin/asset_type_form.html',
                         asset_type=asset_type,
                         form_data=None,
                         categories=AssetCategory)


@admin_bp.route('/settings/asset-types/<int:id>/delete', methods=['POST'])
@login_required
@role_required('admin', 'ciso')
def delete_asset_type(id):
    """Elimina un tipo de activo"""
    asset_type = AssetType.query.get_or_404(id)

    try:
        # Verificar si el tipo está siendo usado en activos
        if asset_type.assets:
            flash(f'No se puede eliminar el tipo de activo {asset_type.name} porque está siendo usado en {len(asset_type.assets)} activo(s)', 'danger')
            return redirect(url_for('admin.asset_types'))

        db.session.delete(asset_type)
        db.session.commit()

        flash(f'Tipo de activo {asset_type.name} eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el tipo de activo: {str(e)}', 'danger')

    return redirect(url_for('admin.asset_types'))


@admin_bp.route('/settings/asset-types/<int:id>/toggle-active', methods=['POST'])
@login_required
@role_required('admin', 'ciso')
def toggle_asset_type_active(id):
    """Activa o desactiva un tipo de activo"""
    asset_type = AssetType.query.get_or_404(id)

    try:
        asset_type.is_active = not asset_type.is_active
        asset_type.updated_at = datetime.utcnow()
        db.session.commit()

        status = 'activado' if asset_type.is_active else 'desactivado'
        flash(f'Tipo de activo {asset_type.name} {status} exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al cambiar el estado del tipo de activo: {str(e)}', 'danger')

    return redirect(url_for('admin.asset_types'))


# ==================== GESTIÓN DE PERÍODOS DE DEPRECIACIÓN ====================

@admin_bp.route('/settings/depreciation')
@login_required
@role_required('admin', 'ciso')
def depreciation_periods():
    """Vista de gestión de períodos de depreciación"""
    periods = DepreciationPeriod.query.order_by(DepreciationPeriod.category).all()
    return render_template('admin/depreciation_periods.html', periods=periods, AssetCategory=AssetCategory)


@admin_bp.route('/settings/depreciation/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'ciso')
def edit_depreciation_period(id):
    """Editar período de depreciación"""
    period = DepreciationPeriod.query.get_or_404(id)

    if request.method == 'POST':
        try:
            period.years = int(request.form['years'])
            period.description = request.form.get('description', '')
            period.method = request.form.get('method', 'linear')
            period.residual_value_percentage = float(request.form.get('residual_value_percentage', 0.0))
            period.is_active = 'is_active' in request.form
            period.updated_at = datetime.utcnow()
            period.updated_by_id = current_user.id

            db.session.commit()

            flash(f'Período de depreciación para {period.category.value} actualizado exitosamente', 'success')
            return redirect(url_for('admin.depreciation_periods'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el período de depreciación: {str(e)}', 'danger')

    return render_template('admin/edit_depreciation_period.html', period=period)


@admin_bp.route('/api/depreciation/calculate', methods=['POST'])
@login_required
def calculate_depreciation_api():
    """API para calcular depreciación en tiempo real"""
    try:
        data = request.get_json()
        category_name = data.get('category')
        purchase_cost = float(data.get('purchase_cost', 0))
        acquisition_date_str = data.get('acquisition_date')

        if not all([category_name, purchase_cost, acquisition_date_str]):
            return jsonify({'error': 'Faltan parámetros requeridos'}), 400

        # Parsear fecha
        acquisition_date = datetime.strptime(acquisition_date_str, '%Y-%m-%d').date()

        # Obtener categoría
        category = AssetCategory[category_name]

        # Obtener período de depreciación
        period = DepreciationPeriod.query.filter_by(category=category, is_active=True).first()

        if not period:
            return jsonify({
                'current_value': purchase_cost,
                'depreciation': 0.0,
                'message': 'No hay configuración de depreciación para esta categoría'
            })

        # Calcular depreciación
        current_value = period.calculate_depreciation(purchase_cost, acquisition_date)
        depreciation = purchase_cost - current_value

        # Calcular años transcurridos
        today = datetime.now().date()
        days_elapsed = (today - acquisition_date).days
        years_elapsed = days_elapsed / 365.25

        return jsonify({
            'current_value': round(current_value, 2),
            'depreciation': round(depreciation, 2),
            'years_elapsed': round(years_elapsed, 2),
            'depreciation_years': period.years,
            'annual_depreciation': round(depreciation / years_elapsed, 2) if years_elapsed > 0 else 0,
            'residual_percentage': period.residual_value_percentage
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========================================================================
# GESTIÓN DE AMENAZAS
# ========================================================================

@admin_bp.route('/settings/amenazas')
@login_required
@role_required('admin', 'ciso')
def amenazas():
    """Gestión del catálogo de amenazas MAGERIT"""
    # Filtros
    grupo_filter = request.args.get('grupo', '')
    search = request.args.get('search', '')

    query = Amenaza.query

    if grupo_filter:
        query = query.filter_by(grupo=grupo_filter)

    if search:
        query = query.filter(
            or_(
                Amenaza.codigo.ilike(f'%{search}%'),
                Amenaza.nombre.ilike(f'%{search}%'),
                Amenaza.descripcion.ilike(f'%{search}%')
            )
        )

    amenazas_list = query.order_by(Amenaza.codigo).all()

    # Contar por grupo
    grupos_count = {}
    for grupo in Amenaza.GRUPOS:
        grupos_count[grupo] = Amenaza.query.filter_by(grupo=grupo).count()

    return render_template('admin/amenazas.html',
                         amenazas=amenazas_list,
                         grupos=Amenaza.GRUPOS,
                         grupos_count=grupos_count,
                         grupo_filter=grupo_filter,
                         search=search)


@admin_bp.route('/settings/amenazas/new', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'ciso')
def create_amenaza():
    """Crea una nueva amenaza"""
    if request.method == 'POST':
        try:
            codigo = request.form.get('codigo')
            nombre = request.form.get('nombre')
            descripcion = request.form.get('descripcion')
            grupo = request.form.get('grupo')
            categoria_magerit = request.form.get('categoria_magerit')

            # Dimensiones
            afecta_confidencialidad = 'afecta_confidencialidad' in request.form
            afecta_integridad = 'afecta_integridad' in request.form
            afecta_disponibilidad = 'afecta_disponibilidad' in request.form

            # Validaciones
            if not codigo or not nombre or not grupo:
                flash('Los campos Código, Nombre y Grupo son obligatorios', 'danger')
                return render_template('admin/amenaza_form.html',
                                     form_data=request.form,
                                     grupos=Amenaza.GRUPOS)

            # Verificar que el código no exista
            existing = Amenaza.query.filter_by(codigo=codigo).first()
            if existing:
                flash(f'Ya existe una amenaza con el código {codigo}', 'danger')
                return render_template('admin/amenaza_form.html',
                                     form_data=request.form,
                                     grupos=Amenaza.GRUPOS)

            # Al menos una dimensión debe estar marcada
            if not (afecta_confidencialidad or afecta_integridad or afecta_disponibilidad):
                flash('Debe seleccionar al menos una dimensión afectada (C, I o D)', 'danger')
                return render_template('admin/amenaza_form.html',
                                     form_data=request.form,
                                     grupos=Amenaza.GRUPOS)

            nueva_amenaza = Amenaza(
                codigo=codigo,
                nombre=nombre,
                descripcion=descripcion,
                grupo=grupo,
                categoria_magerit=categoria_magerit,
                afecta_confidencialidad=afecta_confidencialidad,
                afecta_integridad=afecta_integridad,
                afecta_disponibilidad=afecta_disponibilidad
            )

            db.session.add(nueva_amenaza)
            db.session.commit()

            flash(f'Amenaza {codigo} - {nombre} creada exitosamente', 'success')
            return redirect(url_for('admin.amenazas'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear la amenaza: {str(e)}', 'danger')
            return render_template('admin/amenaza_form.html',
                                 form_data=request.form,
                                 grupos=Amenaza.GRUPOS)

    return render_template('admin/amenaza_form.html',
                         form_data=None,
                         grupos=Amenaza.GRUPOS)


@admin_bp.route('/settings/amenazas/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'ciso')
def edit_amenaza(id):
    """Edita una amenaza existente"""
    amenaza = Amenaza.query.get_or_404(id)

    if request.method == 'POST':
        try:
            codigo = request.form.get('codigo')
            nombre = request.form.get('nombre')
            descripcion = request.form.get('descripcion')
            grupo = request.form.get('grupo')
            categoria_magerit = request.form.get('categoria_magerit')

            # Dimensiones
            afecta_confidencialidad = 'afecta_confidencialidad' in request.form
            afecta_integridad = 'afecta_integridad' in request.form
            afecta_disponibilidad = 'afecta_disponibilidad' in request.form

            # Validaciones
            if not codigo or not nombre or not grupo:
                flash('Los campos Código, Nombre y Grupo son obligatorios', 'danger')
                return render_template('admin/amenaza_form.html',
                                     amenaza=amenaza,
                                     form_data=request.form,
                                     grupos=Amenaza.GRUPOS)

            # Verificar código único (excepto el actual)
            existing = Amenaza.query.filter_by(codigo=codigo).first()
            if existing and existing.id != id:
                flash(f'Ya existe una amenaza con el código {codigo}', 'danger')
                return render_template('admin/amenaza_form.html',
                                     amenaza=amenaza,
                                     form_data=request.form,
                                     grupos=Amenaza.GRUPOS)

            # Al menos una dimensión debe estar marcada
            if not (afecta_confidencialidad or afecta_integridad or afecta_disponibilidad):
                flash('Debe seleccionar al menos una dimensión afectada (C, I o D)', 'danger')
                return render_template('admin/amenaza_form.html',
                                     amenaza=amenaza,
                                     form_data=request.form,
                                     grupos=Amenaza.GRUPOS)

            amenaza.codigo = codigo
            amenaza.nombre = nombre
            amenaza.descripcion = descripcion
            amenaza.grupo = grupo
            amenaza.categoria_magerit = categoria_magerit
            amenaza.afecta_confidencialidad = afecta_confidencialidad
            amenaza.afecta_integridad = afecta_integridad
            amenaza.afecta_disponibilidad = afecta_disponibilidad
            amenaza.updated_at = datetime.utcnow()

            db.session.commit()

            flash(f'Amenaza {codigo} - {nombre} actualizada exitosamente', 'success')
            return redirect(url_for('admin.amenazas'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar la amenaza: {str(e)}', 'danger')
            return render_template('admin/amenaza_form.html',
                                 amenaza=amenaza,
                                 form_data=request.form,
                                 grupos=Amenaza.GRUPOS)

    return render_template('admin/amenaza_form.html',
                         amenaza=amenaza,
                         form_data=None,
                         grupos=Amenaza.GRUPOS)


@admin_bp.route('/settings/amenazas/<int:id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_amenaza(id):
    """Elimina una amenaza"""
    amenaza = Amenaza.query.get_or_404(id)

    try:
        # Verificar si la amenaza está siendo usada en riesgos
        if amenaza.riesgos and len(amenaza.riesgos) > 0:
            flash(f'No se puede eliminar la amenaza {amenaza.codigo} porque está siendo usada en {len(amenaza.riesgos)} riesgo(s)', 'danger')
            return redirect(url_for('admin.amenazas'))

        # Verificar si tiene controles asociados
        if amenaza.controles and len(amenaza.controles) > 0:
            flash(f'No se puede eliminar la amenaza {amenaza.codigo} porque tiene {len(amenaza.controles)} control(es) asociado(s)', 'warning')
            return redirect(url_for('admin.amenazas'))

        codigo = amenaza.codigo
        nombre = amenaza.nombre

        db.session.delete(amenaza)
        db.session.commit()

        flash(f'Amenaza {codigo} - {nombre} eliminada exitosamente', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar la amenaza: {str(e)}', 'danger')

    return redirect(url_for('admin.amenazas'))


@admin_bp.route('/settings/amenazas/<int:id>')
@login_required
@role_required('admin', 'ciso')
def view_amenaza(id):
    """Ver detalle de una amenaza"""
    amenaza = Amenaza.query.get_or_404(id)

    # Obtener estadísticas
    riesgos_count = len(amenaza.riesgos)
    controles_count = len(amenaza.controles)
    recursos_count = len(amenaza.aplicabilidad_recursos)

    return render_template('admin/view_amenaza.html',
                         amenaza=amenaza,
                         riesgos_count=riesgos_count,
                         controles_count=controles_count,
                         recursos_count=recursos_count)