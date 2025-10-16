"""Add Change Management tables

Revision ID: 008_change_management
Revises: 007_add_services_tables
Create Date: 2025-10-15

Implementa gestión de cambios según ISO 27001:2023:
- Control 6.3: Planificación de cambios
- Control 8.32: Gestión de cambios
- Controles relacionados: 5.8, 8.1, 8.19, 8.31
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '008_change_management'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade():
    # Crear ENUM types
    change_type_enum = postgresql.ENUM(
        'INFRASTRUCTURE', 'APPLICATION', 'NETWORK', 'SECURITY', 'PROCESS',
        'POLICY', 'ORGANIZATIONAL', 'HARDWARE', 'SOFTWARE', 'CONFIGURATION', 'OTHER',
        name='changetype'
    )
    change_type_enum.create(op.get_bind())

    change_category_enum = postgresql.ENUM(
        'MINOR', 'STANDARD', 'MAJOR', 'EMERGENCY',
        name='changecategory'
    )
    change_category_enum.create(op.get_bind())

    change_priority_enum = postgresql.ENUM(
        'LOW', 'MEDIUM', 'HIGH', 'CRITICAL',
        name='changepriority'
    )
    change_priority_enum.create(op.get_bind())

    change_status_enum = postgresql.ENUM(
        'DRAFT', 'SUBMITTED', 'UNDER_REVIEW', 'PENDING_APPROVAL', 'APPROVED',
        'REJECTED', 'SCHEDULED', 'IN_PROGRESS', 'IMPLEMENTED', 'UNDER_VALIDATION',
        'CLOSED', 'CANCELLED', 'FAILED', 'ROLLED_BACK',
        name='changestatus'
    )
    change_status_enum.create(op.get_bind())

    risk_level_enum = postgresql.ENUM(
        'LOW', 'MEDIUM', 'HIGH', 'CRITICAL',
        name='risklevel'
    )
    risk_level_enum.create(op.get_bind())

    approval_level_enum = postgresql.ENUM(
        'TECHNICAL', 'SECURITY', 'MANAGEMENT', 'CAB', 'CISO',
        name='approvallevel'
    )
    approval_level_enum.create(op.get_bind())

    approval_status_enum = postgresql.ENUM(
        'PENDING', 'APPROVED', 'REJECTED', 'DELEGATED',
        name='approvalstatus'
    )
    approval_status_enum.create(op.get_bind())

    task_status_enum = postgresql.ENUM(
        'PENDING', 'IN_PROGRESS', 'COMPLETED', 'BLOCKED', 'SKIPPED',
        name='taskstatus'
    )
    task_status_enum.create(op.get_bind())

    document_type_enum = postgresql.ENUM(
        'IMPLEMENTATION_PLAN', 'ROLLBACK_PLAN', 'TEST_PLAN', 'RISK_ASSESSMENT',
        'APPROVAL_FORM', 'EVIDENCE', 'SCREENSHOT', 'LOG_FILE', 'DIAGRAM', 'OTHER',
        name='documenttype'
    )
    document_type_enum.create(op.get_bind())

    review_status_enum = postgresql.ENUM(
        'SUCCESSFUL', 'PARTIALLY_SUCCESSFUL', 'FAILED',
        name='reviewstatus'
    )
    review_status_enum.create(op.get_bind())

    # Tabla principal: changes
    op.create_table(
        'changes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('change_code', sa.String(length=50), nullable=False),

        # Información básica
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),

        # Clasificación
        sa.Column('change_type', change_type_enum, nullable=False),
        sa.Column('category', change_category_enum, nullable=False),
        sa.Column('priority', change_priority_enum, nullable=False),

        # Estado
        sa.Column('status', change_status_enum, nullable=False),

        # Fechas y tiempos
        sa.Column('requested_date', sa.DateTime(), nullable=False),
        sa.Column('scheduled_start_date', sa.DateTime()),
        sa.Column('scheduled_end_date', sa.DateTime()),
        sa.Column('actual_start_date', sa.DateTime()),
        sa.Column('actual_end_date', sa.DateTime()),
        sa.Column('estimated_duration', sa.Integer()),
        sa.Column('actual_duration', sa.Integer()),

        # Ventana de mantenimiento
        sa.Column('downtime_required', sa.Boolean(), default=False),
        sa.Column('downtime_window_start', sa.DateTime()),
        sa.Column('downtime_window_end', sa.DateTime()),
        sa.Column('estimated_downtime_minutes', sa.Integer()),

        # Personas involucradas
        sa.Column('requester_id', sa.Integer(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),

        # Justificación de negocio
        sa.Column('business_justification', sa.Text(), nullable=False),
        sa.Column('expected_benefits', sa.Text()),
        sa.Column('impact_if_not_implemented', sa.Text()),

        # Evaluación de riesgos
        sa.Column('risk_assessment', sa.Text()),
        sa.Column('risk_level', risk_level_enum),

        # Impacto en CIA
        sa.Column('impact_confidentiality', sa.Boolean(), default=False),
        sa.Column('impact_integrity', sa.Boolean(), default=False),
        sa.Column('impact_availability', sa.Boolean(), default=False),

        # Análisis de impacto
        sa.Column('impact_analysis', sa.Text()),
        sa.Column('affected_services', sa.JSON()),
        sa.Column('affected_users_count', sa.Integer()),
        sa.Column('affected_controls', sa.JSON()),

        # Planes
        sa.Column('implementation_plan', sa.Text(), nullable=False),
        sa.Column('rollback_plan', sa.Text(), nullable=False),
        sa.Column('test_plan', sa.Text()),
        sa.Column('communication_plan', sa.Text()),

        # Entornos afectados
        sa.Column('affects_development', sa.Boolean(), default=False),
        sa.Column('affects_testing', sa.Boolean(), default=False),
        sa.Column('affects_production', sa.Boolean(), default=True),

        # Aprobaciones CAB
        sa.Column('approval_required', sa.Boolean(), default=True),
        sa.Column('cab_date', sa.DateTime()),
        sa.Column('cab_decision', sa.Text()),
        sa.Column('cab_notes', sa.Text()),

        # Implementación
        sa.Column('implementation_notes', sa.Text()),
        sa.Column('issues_encountered', sa.Text()),

        # Post-Implementation Review
        sa.Column('pir_date', sa.DateTime()),
        sa.Column('success_criteria', sa.Text()),
        sa.Column('success_status', sa.String(length=50)),
        sa.Column('lessons_learned', sa.Text()),
        sa.Column('recommendations', sa.Text()),

        # Costos
        sa.Column('estimated_cost', sa.Float()),
        sa.Column('actual_cost', sa.Float()),

        # Relaciones con otros módulos
        sa.Column('related_incident_id', sa.Integer()),
        sa.Column('related_nc_id', sa.Integer()),
        sa.Column('depends_on_change_id', sa.Integer()),

        # Metadatos
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('created_by_id', sa.Integer()),
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('updated_by_id', sa.Integer()),
        sa.Column('notes', sa.Text()),

        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('change_code'),
        sa.ForeignKeyConstraint(['requester_id'], ['users.id']),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id']),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id']),
        sa.ForeignKeyConstraint(['updated_by_id'], ['users.id']),
        sa.ForeignKeyConstraint(['related_incident_id'], ['incidents.id']),
        sa.ForeignKeyConstraint(['related_nc_id'], ['nonconformities.id']),
        sa.ForeignKeyConstraint(['depends_on_change_id'], ['changes.id'])
    )

    # Índices para changes
    op.create_index('idx_changes_code', 'changes', ['change_code'])
    op.create_index('idx_changes_status', 'changes', ['status'])
    op.create_index('idx_changes_requester', 'changes', ['requester_id'])
    op.create_index('idx_changes_owner', 'changes', ['owner_id'])
    op.create_index('idx_changes_dates', 'changes', ['scheduled_start_date', 'scheduled_end_date'])

    # Tabla: change_approvals
    op.create_table(
        'change_approvals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('change_id', sa.Integer(), nullable=False),
        sa.Column('approval_level', approval_level_enum, nullable=False),
        sa.Column('approver_id', sa.Integer(), nullable=False),
        sa.Column('status', approval_status_enum, nullable=False),
        sa.Column('comments', sa.Text()),
        sa.Column('conditions', sa.Text()),
        sa.Column('approved_date', sa.DateTime()),
        sa.Column('delegated_to_id', sa.Integer()),
        sa.Column('delegation_reason', sa.Text()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime()),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['change_id'], ['changes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['approver_id'], ['users.id']),
        sa.ForeignKeyConstraint(['delegated_to_id'], ['users.id'])
    )
    op.create_index('idx_change_approvals_change', 'change_approvals', ['change_id'])
    op.create_index('idx_change_approvals_approver', 'change_approvals', ['approver_id'])

    # Tabla: change_tasks
    op.create_table(
        'change_tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('change_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('order', sa.Integer(), default=0),
        sa.Column('is_critical', sa.Boolean(), default=False),
        sa.Column('assigned_to_id', sa.Integer()),
        sa.Column('status', task_status_enum, nullable=False),
        sa.Column('estimated_duration', sa.Integer()),
        sa.Column('actual_duration', sa.Integer()),
        sa.Column('start_date', sa.DateTime()),
        sa.Column('completed_date', sa.DateTime()),
        sa.Column('notes', sa.Text()),
        sa.Column('blocking_reason', sa.Text()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime()),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['change_id'], ['changes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['assigned_to_id'], ['users.id'])
    )
    op.create_index('idx_change_tasks_change', 'change_tasks', ['change_id'])
    op.create_index('idx_change_tasks_assigned', 'change_tasks', ['assigned_to_id'])

    # Tabla: change_documents
    op.create_table(
        'change_documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('change_id', sa.Integer(), nullable=False),
        sa.Column('document_type', document_type_enum, nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_size', sa.Integer()),
        sa.Column('mime_type', sa.String(length=100)),
        sa.Column('description', sa.Text()),
        sa.Column('version', sa.String(length=20)),
        sa.Column('uploaded_by_id', sa.Integer(), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['change_id'], ['changes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by_id'], ['users.id'])
    )
    op.create_index('idx_change_documents_change', 'change_documents', ['change_id'])

    # Tabla: change_history
    op.create_table(
        'change_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('change_id', sa.Integer(), nullable=False),
        sa.Column('field_changed', sa.String(length=100), nullable=False),
        sa.Column('old_value', sa.Text()),
        sa.Column('new_value', sa.Text()),
        sa.Column('changed_by_id', sa.Integer(), nullable=False),
        sa.Column('changed_at', sa.DateTime(), nullable=False),
        sa.Column('comments', sa.Text()),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['change_id'], ['changes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['changed_by_id'], ['users.id'])
    )
    op.create_index('idx_change_history_change', 'change_history', ['change_id'])
    op.create_index('idx_change_history_date', 'change_history', ['changed_at'])

    # Tabla: change_reviews
    op.create_table(
        'change_reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('change_id', sa.Integer(), nullable=False),
        sa.Column('reviewer_id', sa.Integer(), nullable=False),
        sa.Column('review_date', sa.DateTime(), nullable=False),
        sa.Column('success_status', review_status_enum, nullable=False),
        sa.Column('objectives_met', sa.Boolean()),
        sa.Column('success_criteria_met', sa.Boolean()),
        sa.Column('lessons_learned', sa.Text()),
        sa.Column('what_went_well', sa.Text()),
        sa.Column('what_went_wrong', sa.Text()),
        sa.Column('issues_found', sa.Text()),
        sa.Column('recommendations', sa.Text()),
        sa.Column('downtime_occurred', sa.Integer()),
        sa.Column('incidents_caused', sa.Integer()),
        sa.Column('rollback_required', sa.Boolean(), default=False),
        sa.Column('notes', sa.Text()),
        sa.Column('created_at', sa.DateTime(), nullable=False),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['change_id'], ['changes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reviewer_id'], ['users.id'])
    )
    op.create_index('idx_change_reviews_change', 'change_reviews', ['change_id'])

    # Tabla: change_risk_assessments
    op.create_table(
        'change_risk_assessments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('change_id', sa.Integer(), nullable=False),
        sa.Column('risk_description', sa.Text(), nullable=False),
        sa.Column('probability', sa.Integer(), nullable=False),
        sa.Column('impact', sa.Integer(), nullable=False),
        sa.Column('risk_score', sa.Integer()),
        sa.Column('risk_level', risk_level_enum),
        sa.Column('mitigation_measures', sa.Text()),
        sa.Column('contingency_plan', sa.Text()),
        sa.Column('created_by_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime()),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['change_id'], ['changes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'])
    )
    op.create_index('idx_change_risks_change', 'change_risk_assessments', ['change_id'])

    # Tabla: change_assets (relación many-to-many con assets)
    op.create_table(
        'change_assets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('change_id', sa.Integer(), nullable=False),
        sa.Column('asset_id', sa.Integer(), nullable=False),
        sa.Column('impact_description', sa.Text()),
        sa.Column('created_at', sa.DateTime(), nullable=False),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['change_id'], ['changes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('change_id', 'asset_id', name='unique_change_asset')
    )
    op.create_index('idx_change_assets_change', 'change_assets', ['change_id'])
    op.create_index('idx_change_assets_asset', 'change_assets', ['asset_id'])


def downgrade():
    # Eliminar tablas
    op.drop_table('change_assets')
    op.drop_table('change_risk_assessments')
    op.drop_table('change_reviews')
    op.drop_table('change_history')
    op.drop_table('change_documents')
    op.drop_table('change_tasks')
    op.drop_table('change_approvals')
    op.drop_table('changes')

    # Eliminar ENUM types
    sa.Enum(name='changetype').drop(op.get_bind())
    sa.Enum(name='changecategory').drop(op.get_bind())
    sa.Enum(name='changepriority').drop(op.get_bind())
    sa.Enum(name='changestatus').drop(op.get_bind())
    sa.Enum(name='risklevel').drop(op.get_bind())
    sa.Enum(name='approvallevel').drop(op.get_bind())
    sa.Enum(name='approvalstatus').drop(op.get_bind())
    sa.Enum(name='taskstatus').drop(op.get_bind())
    sa.Enum(name='documenttype').drop(op.get_bind())
    sa.Enum(name='reviewstatus').drop(op.get_bind())
