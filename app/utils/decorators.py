"""
Decoradores útiles para el ISMS Manager
"""
from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user


def role_required(*roles):
    """
    Decorador para restringir acceso por rol

    Args:
        roles: Roles permitidos (puede ser uno o más argumentos, o una lista)

    Usage:
        @role_required('admin', 'ciso')
        def admin_function():
            pass

        @role_required('admin')
        def super_admin_function():
            pass

        @role_required(['admin', 'ciso'])
        def another_function():
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Por favor, inicia sesión para acceder a esta página.', 'warning')
                return redirect(url_for('auth.login'))

            # Normalizar roles: si se pasó una lista como primer argumento, usarla
            roles_list = roles[0] if len(roles) == 1 and isinstance(roles[0], (list, tuple)) else roles

            # Verificar si el usuario tiene alguno de los roles permitidos
            # Usar el método has_role que maneja los aliases correctamente
            has_required_role = False
            for role in roles_list:
                if hasattr(current_user, 'has_role') and current_user.has_role(role):
                    has_required_role = True
                    break

            if not has_required_role:
                flash('No tienes permisos para acceder a esta función.', 'danger')
                return redirect(url_for('dashboard.index'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def permission_required(permission):
    """
    Decorador para restringir acceso por permiso específico

    Args:
        permission: Nombre del permiso requerido

    Usage:
        @permission_required('edit_soa')
        def edit_soa_function():
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Por favor, inicia sesión para acceder a esta página.', 'warning')
                return redirect(url_for('auth.login'))

            # Verificar si el usuario tiene el permiso
            # Esta implementación asume que has implementado un sistema de permisos
            # Si no lo tienes, puedes usar role_required en su lugar

            if not hasattr(current_user, 'has_permission'):
                # Fallback a verificación por rol si no existe sistema de permisos
                if not current_user.role or current_user.role.name not in ['admin', 'ciso']:
                    flash('No tienes permisos para acceder a esta función.', 'danger')
                    return redirect(url_for('dashboard.index'))
            elif not current_user.has_permission(permission):
                flash('No tienes permisos para acceder a esta función.', 'danger')
                return redirect(url_for('dashboard.index'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator
