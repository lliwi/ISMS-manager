"""
Decoradores de seguridad y control de acceso
"""
from functools import wraps
from flask import abort, flash, redirect, url_for, request
from flask_login import current_user
from models import db, AuditLog


def role_required(*roles):
    """
    Decorador para restringir acceso por rol

    Uso:
        @role_required('admin')
        @role_required('admin', 'ciso')

    Soporta tanto nombres completos como aliases:
        'admin' -> 'Administrador del Sistema'
        'ciso' -> 'Responsable de Seguridad (CISO)'
        'auditor' -> 'Auditor Interno'
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Debes iniciar sesión para acceder a esta página', 'warning')
                return redirect(url_for('auth.login', next=request.url))

            if not current_user.is_active:
                flash('Tu cuenta está desactivada. Contacta al administrador.', 'danger')
                return redirect(url_for('auth.login'))

            # Verificar si el usuario tiene alguno de los roles permitidos
            has_required_role = any(current_user.has_role(role) for role in roles)

            if not has_required_role:
                # Registrar intento de acceso no autorizado
                AuditLog.log_action(
                    action='access_denied',
                    description=f'Intento de acceso a ruta restringida: {request.path}',
                    ip_address=request.remote_addr,
                    user_agent=request.user_agent.string,
                    status='failed'
                )
                db.session.commit()

                flash('No tienes permisos para acceder a esta página', 'danger')
                abort(403)

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def module_access_required(module_name):
    """
    Decorador para verificar acceso a módulos específicos

    Uso:
        @module_access_required('users')
        @module_access_required('documents')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Debes iniciar sesión para acceder a esta página', 'warning')
                return redirect(url_for('auth.login', next=request.url))

            if not current_user.is_active:
                flash('Tu cuenta está desactivada. Contacta al administrador.', 'danger')
                return redirect(url_for('auth.login'))

            if not current_user.can_access(module_name):
                AuditLog.log_action(
                    action='access_denied',
                    description=f'Intento de acceso al módulo: {module_name}',
                    ip_address=request.remote_addr,
                    user_agent=request.user_agent.string,
                    status='failed'
                )
                db.session.commit()

                flash(f'No tienes permisos para acceder al módulo {module_name}', 'danger')
                abort(403)

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def audit_action(action, entity_type=None):
    """
    Decorador para registrar automáticamente acciones en el audit log

    Uso:
        @audit_action('view_users', entity_type='User')
        @audit_action('create_document', entity_type='Document')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Ejecutar la función
            result = f(*args, **kwargs)

            # Registrar en audit log
            try:
                entity_id = kwargs.get('id') or kwargs.get('user_id') or kwargs.get('doc_id')

                AuditLog.log_action(
                    action=action,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    ip_address=request.remote_addr,
                    user_agent=request.user_agent.string
                )
                db.session.commit()
            except Exception as e:
                # No fallar si el registro de auditoría falla
                print(f"Error logging audit action: {e}")

            return result
        return decorated_function
    return decorator


def check_password_expiry(f):
    """
    Decorador para verificar si la contraseña del usuario ha expirado
    Redirige a cambio de contraseña si es necesario
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and current_user.needs_password_change():
            # Permitir acceso solo a rutas de cambio de contraseña y logout
            allowed_endpoints = ['auth.change_password', 'auth.logout', 'static']
            if request.endpoint not in allowed_endpoints:
                flash('Tu contraseña ha expirado. Debes cambiarla para continuar.', 'warning')
                return redirect(url_for('auth.change_password'))

        return f(*args, **kwargs)
    return decorated_function
