"""Add task_soa_controls relationship

Revision ID: 010_add_task_soa_controls
Revises: 009_add_comprehensive_task_management
Create Date: 2025-10-19 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '010_add_task_soa_controls'
down_revision = '009_add_comprehensive_task_management'
branch_labels = None
depends_on = None


def upgrade():
    # Crear tabla de asociación task_soa_controls
    op.create_table('task_soa_controls',
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('soa_control_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ),
        sa.ForeignKeyConstraint(['soa_control_id'], ['soa_controls.id'], ),
        sa.PrimaryKeyConstraint('task_id', 'soa_control_id')
    )

    # Crear índices para mejorar performance
    op.create_index('idx_task_soa_task_id', 'task_soa_controls', ['task_id'])
    op.create_index('idx_task_soa_control_id', 'task_soa_controls', ['soa_control_id'])


def downgrade():
    # Eliminar índices
    op.drop_index('idx_task_soa_control_id', table_name='task_soa_controls')
    op.drop_index('idx_task_soa_task_id', table_name='task_soa_controls')

    # Eliminar tabla
    op.drop_table('task_soa_controls')
