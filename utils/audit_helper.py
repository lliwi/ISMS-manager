"""
Helper para registro automático de auditoría
"""
from flask import request
from models import db, AuditLog
from flask_login import current_user


def get_client_ip():
    """Obtiene la IP del cliente considerando proxies"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    return request.remote_addr


def get_user_agent():
    """Obtiene el user agent del cliente"""
    return request.user_agent.string if request.user_agent else None


def log_user_action(action, entity_type=None, entity_id=None, description=None,
                    old_values=None, new_values=None, status='success', error_message=None):
    """
    Registra una acción del usuario en el audit log

    Args:
        action: Tipo de acción (create, update, delete, view, login, logout, etc.)
        entity_type: Tipo de entidad afectada (User, Document, Risk, etc.)
        entity_id: ID de la entidad afectada
        description: Descripción de la acción
        old_values: Valores anteriores (para updates)
        new_values: Valores nuevos (para creates y updates)
        status: Estado de la acción (success, failed, error)
        error_message: Mensaje de error si aplica
    """
    try:
        user = current_user if current_user.is_authenticated else None

        log = AuditLog(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            old_values=old_values,
            new_values=new_values,
            user_id=user.id if user else None,
            username=user.username if user else 'anonymous',
            ip_address=get_client_ip(),
            user_agent=get_user_agent(),
            status=status,
            error_message=error_message
        )

        db.session.add(log)
        db.session.commit()

        return log
    except Exception as e:
        # No fallar la operación principal si el log falla
        print(f"Error creating audit log: {e}")
        db.session.rollback()
        return None


def log_login_attempt(username, success, error_message=None, user=None):
    """
    Registra un intento de login

    Args:
        username: Nombre de usuario
        success: True si el login fue exitoso
        error_message: Mensaje de error si falló
        user: Objeto User si el login fue exitoso
    """
    action = 'login_success' if success else 'login_failed'
    status = 'success' if success else 'failed'

    description = f'Intento de login para usuario: {username}'
    if not success and error_message:
        description += f' - {error_message}'

    try:
        log = AuditLog(
            action=action,
            entity_type='User',
            entity_id=user.id if user else None,
            description=description,
            username=username,
            ip_address=get_client_ip(),
            user_agent=get_user_agent(),
            status=status,
            error_message=error_message
        )

        db.session.add(log)
        db.session.commit()

        return log
    except Exception as e:
        print(f"Error logging login attempt: {e}")
        db.session.rollback()
        return None


def log_user_changes(user, old_data, new_data, action='update'):
    """
    Registra cambios en un usuario

    Args:
        user: Objeto User
        old_data: Diccionario con valores anteriores
        new_data: Diccionario con valores nuevos
        action: Tipo de acción (create, update, delete)
    """
    # Filtrar campos sensibles
    sensitive_fields = ['password_hash', 'password']
    old_filtered = {k: v for k, v in old_data.items() if k not in sensitive_fields} if old_data else None
    new_filtered = {k: v for k, v in new_data.items() if k not in sensitive_fields} if new_data else None

    description = f'Usuario {user.username} '
    if action == 'create':
        description += 'creado'
    elif action == 'update':
        description += 'modificado'
    elif action == 'delete':
        description += 'eliminado'

    return log_user_action(
        action=f'user_{action}',
        entity_type='User',
        entity_id=user.id,
        description=description,
        old_values=old_filtered,
        new_values=new_filtered
    )


def log_password_change(user, changed_by_admin=False):
    """
    Registra un cambio de contraseña

    Args:
        user: Usuario que cambió su contraseña
        changed_by_admin: True si un admin cambió la contraseña
    """
    if changed_by_admin:
        description = f'Contraseña del usuario {user.username} reseteada por administrador'
        action = 'password_reset_by_admin'
    else:
        description = f'Usuario {user.username} cambió su contraseña'
        action = 'password_changed'

    return log_user_action(
        action=action,
        entity_type='User',
        entity_id=user.id,
        description=description
    )


def log_account_lock(user, reason='too_many_attempts'):
    """
    Registra el bloqueo de una cuenta

    Args:
        user: Usuario bloqueado
        reason: Razón del bloqueo
    """
    reasons = {
        'too_many_attempts': 'Demasiados intentos fallidos de login',
        'admin': 'Bloqueado por administrador',
        'security': 'Medida de seguridad'
    }

    description = f'Cuenta {user.username} bloqueada: {reasons.get(reason, reason)}'

    return log_user_action(
        action='account_locked',
        entity_type='User',
        entity_id=user.id,
        description=description,
        status='security_event'
    )


def log_account_unlock(user):
    """
    Registra el desbloqueo de una cuenta

    Args:
        user: Usuario desbloqueado
    """
    description = f'Cuenta {user.username} desbloqueada'

    return log_user_action(
        action='account_unlocked',
        entity_type='User',
        entity_id=user.id,
        description=description
    )


def get_user_activity(user_id, limit=50):
    """
    Obtiene el historial de actividad de un usuario

    Args:
        user_id: ID del usuario
        limit: Número máximo de registros a retornar

    Returns:
        Lista de AuditLog
    """
    return AuditLog.query.filter_by(user_id=user_id)\
                         .order_by(AuditLog.created_at.desc())\
                         .limit(limit)\
                         .all()


def get_recent_security_events(limit=100):
    """
    Obtiene eventos de seguridad recientes

    Args:
        limit: Número máximo de eventos

    Returns:
        Lista de AuditLog con eventos de seguridad
    """
    security_actions = [
        'login_failed',
        'account_locked',
        'account_unlocked',
        'password_reset_by_admin',
        'access_denied',
        'user_deleted'
    ]

    return AuditLog.query.filter(AuditLog.action.in_(security_actions))\
                         .order_by(AuditLog.created_at.desc())\
                         .limit(limit)\
                         .all()
