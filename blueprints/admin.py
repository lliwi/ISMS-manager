from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import User, Role, AuditLog, DocumentType, ISOVersion, db
from forms.user_forms import UserCreateForm, UserEditForm, ChangePasswordForm, ResetPasswordForm, UserSearchForm
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

    return render_template('admin/settings.html',
                         doc_types_count=doc_types_count,
                         iso_versions_count=iso_versions_count)


@admin_bp.route('/settings/document-types')
@login_required
@role_required('admin', 'ciso')
def document_types():
    """Gestión de tipos de documentos"""
    doc_types = DocumentType.query.order_by(DocumentType.order).all()
    return render_template('admin/document_types.html', document_types=doc_types)


@admin_bp.route('/settings/iso-versions')
@login_required
@role_required('admin', 'ciso')
def iso_versions():
    """Gestión de versiones ISO"""
    iso_versions = ISOVersion.query.order_by(ISOVersion.year.desc()).all()
    return render_template('admin/iso_versions.html', iso_versions=iso_versions)