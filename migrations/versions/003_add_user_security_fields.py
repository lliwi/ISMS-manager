"""Add user security and audit fields

Revision ID: 003
Revises: 002
Create Date: 2025-10-04

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    """Agrega campos de seguridad al modelo User y crea tabla AuditLog"""

    # Agregar campos de seguridad a users
    op.add_column('users', sa.Column('phone', sa.String(length=20), nullable=True))
    op.add_column('users', sa.Column('failed_login_attempts', sa.Integer(), server_default='0', nullable=True))
    op.add_column('users', sa.Column('account_locked_until', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('password_changed_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('must_change_password', sa.Boolean(), server_default='0', nullable=True))
    op.add_column('users', sa.Column('last_password_change_notification', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('last_login_ip', sa.String(length=45), nullable=True))
    op.add_column('users', sa.Column('last_activity', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('created_by_id', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('updated_by_id', sa.Integer(), nullable=True))

    # Agregar foreign keys
    op.create_foreign_key('fk_users_created_by', 'users', 'users', ['created_by_id'], ['id'])
    op.create_foreign_key('fk_users_updated_by', 'users', 'users', ['updated_by_id'], ['id'])

    # Crear tabla audit_logs
    op.create_table('audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=True),
        sa.Column('entity_id', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('old_values', sa.JSON(), nullable=True),
        sa.Column('new_values', sa.JSON(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('username', sa.String(length=80), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=255), nullable=True),
        sa.Column('session_id', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=20), server_default='success', nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Crear índices para mejor performance
    op.create_index('idx_audit_logs_created_at', 'audit_logs', ['created_at'], unique=False)
    op.create_index('idx_audit_logs_user_id', 'audit_logs', ['user_id'], unique=False)
    op.create_index('idx_audit_logs_action', 'audit_logs', ['action'], unique=False)
    op.create_index('idx_audit_logs_entity', 'audit_logs', ['entity_type', 'entity_id'], unique=False)

    # Inicializar password_changed_at para usuarios existentes
    op.execute("UPDATE users SET password_changed_at = created_at WHERE password_changed_at IS NULL")


def downgrade():
    """Revertir cambios"""

    # Eliminar tabla audit_logs
    op.drop_index('idx_audit_logs_entity', table_name='audit_logs')
    op.drop_index('idx_audit_logs_action', table_name='audit_logs')
    op.drop_index('idx_audit_logs_user_id', table_name='audit_logs')
    op.drop_index('idx_audit_logs_created_at', table_name='audit_logs')
    op.drop_table('audit_logs')

    # Eliminar foreign keys de users
    op.drop_constraint('fk_users_updated_by', 'users', type_='foreignkey')
    op.drop_constraint('fk_users_created_by', 'users', type_='foreignkey')

    # Eliminar columnas de users
    op.drop_column('users', 'updated_by_id')
    op.drop_column('users', 'created_by_id')
    op.drop_column('users', 'last_activity')
    op.drop_column('users', 'last_login_ip')
    op.drop_column('users', 'last_password_change_notification')
    op.drop_column('users', 'must_change_password')
    op.drop_column('users', 'password_changed_at')
    op.drop_column('users', 'account_locked_until')
    op.drop_column('users', 'failed_login_attempts')
    op.drop_column('users', 'phone')
