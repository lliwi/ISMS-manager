"""Add comprehensive task management tables

Revision ID: 009
Revises: 008
Create Date: 2025-10-19

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '009_add_comprehensive_task_management'
down_revision = '008_change_management'
branch_labels = None
depends_on = None


def upgrade():
    # Drop old simple tasks table and enums if they exist
    op.execute('DROP TABLE IF EXISTS tasks CASCADE')
    op.execute('DROP TYPE IF EXISTS taskstatus CASCADE')
    op.execute('DROP TYPE IF EXISTS taskpriority CASCADE')

    # Create task_templates table
    op.create_table('task_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.Enum('revision_controles', 'auditoria_interna', 'evaluacion_riesgos',
                                     'revision_politicas', 'formacion_concienciacion', 'mantenimiento_seguridad',
                                     'copias_seguridad', 'revision_accesos', 'actualizacion_inventarios',
                                     'revision_proveedores', 'gestion_vulnerabilidades', 'revision_incidentes',
                                     'continuidad_negocio', 'revision_legal', 'revision_direccion',
                                     'pruebas_recuperacion', 'otros', name='taskcategory'), nullable=False),
        sa.Column('frequency', sa.Enum('diaria', 'semanal', 'quincenal', 'mensual', 'bimestral',
                                      'trimestral', 'cuatrimestral', 'semestral', 'anual', 'bienal',
                                      'unica', name='taskfrequency'), nullable=False),
        sa.Column('priority', sa.Enum('baja', 'media', 'alta', 'critica', name='taskpriority'), nullable=True),
        sa.Column('estimated_hours', sa.Float(), nullable=True),
        sa.Column('iso_control', sa.String(length=10), nullable=True),
        sa.Column('default_role_id', sa.Integer(), nullable=True),
        sa.Column('default_assignee_id', sa.Integer(), nullable=True),
        sa.Column('notify_days_before', sa.Integer(), nullable=True),
        sa.Column('checklist_template', sa.JSON(), nullable=True),
        sa.Column('requires_evidence', sa.Boolean(), nullable=True),
        sa.Column('requires_approval', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by_id', sa.Integer(), nullable=True),
        sa.Column('updated_by_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['default_assignee_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['default_role_id'], ['roles.id'], ),
        sa.ForeignKeyConstraint(['updated_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create tasks table
    op.create_table('tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('template_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.Enum('revision_controles', 'auditoria_interna', 'evaluacion_riesgos',
                                     'revision_politicas', 'formacion_concienciacion', 'mantenimiento_seguridad',
                                     'copias_seguridad', 'revision_accesos', 'actualizacion_inventarios',
                                     'revision_proveedores', 'gestion_vulnerabilidades', 'revision_incidentes',
                                     'continuidad_negocio', 'revision_legal', 'revision_direccion',
                                     'pruebas_recuperacion', 'otros', name='taskcategory'), nullable=False),
        sa.Column('status', sa.Enum('pendiente', 'en_progreso', 'completada', 'vencida', 'cancelada',
                                   'reprogramada', name='taskstatus'), nullable=False),
        sa.Column('priority', sa.Enum('baja', 'media', 'alta', 'critica', name='taskpriority'), nullable=True),
        sa.Column('due_date', sa.DateTime(), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('completion_date', sa.DateTime(), nullable=True),
        sa.Column('assigned_to_id', sa.Integer(), nullable=True),
        sa.Column('assigned_role_id', sa.Integer(), nullable=True),
        sa.Column('estimated_hours', sa.Float(), nullable=True),
        sa.Column('actual_hours', sa.Float(), nullable=True),
        sa.Column('iso_control', sa.String(length=10), nullable=True),
        sa.Column('checklist', sa.JSON(), nullable=True),
        sa.Column('progress', sa.Integer(), nullable=True),
        sa.Column('observations', sa.Text(), nullable=True),
        sa.Column('result', sa.Text(), nullable=True),
        sa.Column('requires_approval', sa.Boolean(), nullable=True),
        sa.Column('approved_by_id', sa.Integer(), nullable=True),
        sa.Column('approval_date', sa.DateTime(), nullable=True),
        sa.Column('approval_comments', sa.Text(), nullable=True),
        sa.Column('last_notification_sent', sa.DateTime(), nullable=True),
        sa.Column('notification_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by_id', sa.Integer(), nullable=True),
        sa.Column('updated_by_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['approved_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['assigned_role_id'], ['roles.id'], ),
        sa.ForeignKeyConstraint(['assigned_to_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['template_id'], ['task_templates.id'], ),
        sa.ForeignKeyConstraint(['updated_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create task_evidences table
    op.create_table('task_evidences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('mime_type', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=True),
        sa.Column('uploaded_by_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create task_comments table
    op.create_table('task_comments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=False),
        sa.Column('comment_type', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('created_by_id', sa.Integer(), nullable=True),
        sa.Column('is_edited', sa.Boolean(), nullable=True),
        sa.Column('edited_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create task_history table
    op.create_table('task_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('old_value', sa.Text(), nullable=True),
        sa.Column('new_value', sa.Text(), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create task_notification_logs table
    op.create_table('task_notification_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('recipient_email', sa.String(length=120), nullable=False),
        sa.Column('notification_type', sa.String(length=50), nullable=True),
        sa.Column('subject', sa.String(length=200), nullable=True),
        sa.Column('body', sa.Text(), nullable=True),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('was_successful', sa.Boolean(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for better performance
    op.create_index('idx_tasks_status', 'tasks', ['status'])
    op.create_index('idx_tasks_assigned_to', 'tasks', ['assigned_to_id'])
    op.create_index('idx_tasks_due_date', 'tasks', ['due_date'])
    op.create_index('idx_tasks_category', 'tasks', ['category'])
    op.create_index('idx_task_templates_frequency', 'task_templates', ['frequency'])
    op.create_index('idx_task_templates_is_active', 'task_templates', ['is_active'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_task_templates_is_active', table_name='task_templates')
    op.drop_index('idx_task_templates_frequency', table_name='task_templates')
    op.drop_index('idx_tasks_category', table_name='tasks')
    op.drop_index('idx_tasks_due_date', table_name='tasks')
    op.drop_index('idx_tasks_assigned_to', table_name='tasks')
    op.drop_index('idx_tasks_status', table_name='tasks')

    # Drop tables
    op.drop_table('task_notification_logs')
    op.drop_table('task_history')
    op.drop_table('task_comments')
    op.drop_table('task_evidences')
    op.drop_table('tasks')
    op.drop_table('task_templates')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS taskstatus CASCADE')
    op.execute('DROP TYPE IF EXISTS taskpriority CASCADE')
    op.execute('DROP TYPE IF EXISTS taskfrequency CASCADE')
    op.execute('DROP TYPE IF EXISTS taskcategory CASCADE')
