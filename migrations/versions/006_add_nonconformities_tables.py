"""Add nonconformities tables - ISO 27001:2023 Chapter 10.2

Revision ID: 006
Revises: 005
Create Date: 2025-10-12 06:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade():
    # Create ENUM types for nonconformities (checkfirst to avoid duplicates)
    bind = op.get_bind()

    ncorigin_enum = postgresql.ENUM('INTERNAL_AUDIT', 'EXTERNAL_AUDIT', 'MANAGEMENT_REVIEW', 'INCIDENT',
                                     'CUSTOMER_COMPLAINT', 'SELF_ASSESSMENT', 'MONITORING', 'RISK_ASSESSMENT',
                                     'SUPPLIER_ISSUE', 'OTHER', name='ncorigin', create_type=False)
    ncorigin_enum.create(bind, checkfirst=True)

    ncseverity_enum = postgresql.ENUM('MINOR', 'MAJOR', 'CRITICAL', name='ncseverity', create_type=False)
    ncseverity_enum.create(bind, checkfirst=True)

    ncstatus_enum = postgresql.ENUM('NEW', 'ANALYZING', 'ACTION_PLAN', 'IMPLEMENTING',
                                     'VERIFYING', 'CLOSED', 'REOPENED', name='ncstatus', create_type=False)
    ncstatus_enum.create(bind, checkfirst=True)

    rcamethod_enum = postgresql.ENUM('FIVE_WHYS', 'ISHIKAWA', 'PARETO', 'FTA',
                                      'BRAINSTORMING', 'OTHER', name='rcamethod', create_type=False)
    rcamethod_enum.create(bind, checkfirst=True)

    actiontype_enum = postgresql.ENUM('CORRECTIVE', 'PREVENTIVE', 'IMPROVEMENT', name='actiontype', create_type=False)
    actiontype_enum.create(bind, checkfirst=True)

    actionstatus_enum = postgresql.ENUM('PENDING', 'IN_PROGRESS', 'COMPLETED',
                                         'VERIFIED', 'CANCELLED', name='actionstatus', create_type=False)
    actionstatus_enum.create(bind, checkfirst=True)

    nctimelineeventtype_enum = postgresql.ENUM('CREATED', 'STATUS_CHANGE', 'ASSIGNED', 'COMMENT',
                                                 'ACTION_ADDED', 'ACTION_COMPLETED', 'RCA_COMPLETED',
                                                 'VERIFICATION_STARTED', 'VERIFICATION_COMPLETED',
                                                 'CLOSURE', 'REOPENED', 'SGSI_CHANGE', 'ATTACHMENT_ADDED',
                                                 name='nctimelineeventtype', create_type=False)
    nctimelineeventtype_enum.create(bind, checkfirst=True)

    # Update nonconformities table (if exists, otherwise create)
    # First, try to update existing columns
    try:
        with op.batch_alter_table('nonconformities', schema=None) as batch_op:
            # Add new columns
            batch_op.add_column(sa.Column('nc_number', sa.String(length=50), nullable=False, unique=True))
            batch_op.add_column(sa.Column('origin', ncorigin_enum, nullable=False))
            batch_op.add_column(sa.Column('detection_date', sa.DateTime(), nullable=False))
            batch_op.add_column(sa.Column('reported_date', sa.DateTime(), nullable=False))
            batch_op.add_column(sa.Column('analysis_start_date', sa.DateTime(), nullable=True))
            batch_op.add_column(sa.Column('action_plan_date', sa.DateTime(), nullable=True))
            batch_op.add_column(sa.Column('implementation_start_date', sa.DateTime(), nullable=True))
            batch_op.add_column(sa.Column('verification_date', sa.DateTime(), nullable=True))
            batch_op.add_column(sa.Column('target_closure_date', sa.Date(), nullable=True))
            batch_op.add_column(sa.Column('reported_by_id', sa.Integer(), nullable=False))
            batch_op.add_column(sa.Column('affected_controls', sa.JSON(), nullable=True))
            batch_op.add_column(sa.Column('audit_id', sa.Integer(), nullable=True))
            batch_op.add_column(sa.Column('incident_id', sa.Integer(), nullable=True))
            batch_op.add_column(sa.Column('immediate_action', sa.Text(), nullable=True))
            batch_op.add_column(sa.Column('immediate_action_date', sa.DateTime(), nullable=True))
            batch_op.add_column(sa.Column('rca_method', rcamethod_enum, nullable=True))
            batch_op.add_column(sa.Column('root_causes', sa.JSON(), nullable=True))
            batch_op.add_column(sa.Column('contributing_factors', sa.JSON(), nullable=True))
            batch_op.add_column(sa.Column('is_recurrent', sa.Boolean(), default=False))
            batch_op.add_column(sa.Column('related_nc_id', sa.Integer(), nullable=True))
            batch_op.add_column(sa.Column('similar_nc_analysis', sa.Text(), nullable=True))
            batch_op.add_column(sa.Column('effectiveness_verification', sa.Text(), nullable=True))
            batch_op.add_column(sa.Column('effectiveness_criteria', sa.Text(), nullable=True))
            batch_op.add_column(sa.Column('is_effective', sa.Boolean(), nullable=True))
            batch_op.add_column(sa.Column('sgsi_changes_required', sa.Boolean(), default=False))
            batch_op.add_column(sa.Column('sgsi_changes_description', sa.Text(), nullable=True))
            batch_op.add_column(sa.Column('sgsi_changes_implemented', sa.Boolean(), default=False))
            batch_op.add_column(sa.Column('lessons_learned', sa.Text(), nullable=True))
            batch_op.add_column(sa.Column('preventive_measures', sa.JSON(), nullable=True))
            batch_op.add_column(sa.Column('estimated_cost', sa.Float(), nullable=True))
            batch_op.add_column(sa.Column('actual_cost', sa.Float(), nullable=True))
            batch_op.add_column(sa.Column('created_by_id', sa.Integer(), nullable=True))
            batch_op.add_column(sa.Column('updated_by_id', sa.Integer(), nullable=True))
            batch_op.add_column(sa.Column('notes', sa.Text(), nullable=True))

            # Modify existing columns
            batch_op.alter_column('severity',
                   existing_type=sa.VARCHAR(length=20),
                   type_=ncseverity_enum,
                   existing_nullable=False,
                   postgresql_using='severity::text::ncseverity')
            batch_op.alter_column('status',
                   existing_type=sa.VARCHAR(length=20),
                   type_=ncstatus_enum,
                   existing_nullable=False,
                   postgresql_using='status::text::ncstatus')
            batch_op.alter_column('closure_date',
                   existing_type=sa.DATE(),
                   type_=sa.DateTime(),
                   existing_nullable=True)

            # Create foreign keys
            batch_op.create_foreign_key('fk_nc_audit', 'audits', ['audit_id'], ['id'])
            batch_op.create_foreign_key('fk_nc_created_by', 'users', ['created_by_id'], ['id'])
            batch_op.create_foreign_key('fk_nc_updated_by', 'users', ['updated_by_id'], ['id'])
            batch_op.create_foreign_key('fk_nc_reported_by', 'users', ['reported_by_id'], ['id'])
            batch_op.create_foreign_key('fk_nc_incident', 'incidents', ['incident_id'], ['id'])
            batch_op.create_foreign_key('fk_nc_related_nc', 'nonconformities', ['related_nc_id'], ['id'])

            # Drop old columns
            batch_op.drop_column('source')
            batch_op.drop_column('root_cause_method')
            batch_op.drop_column('target_date')
            batch_op.drop_column('corrective_action')
    except:
        # If table doesn't exist, create it
        pass

    # Create corrective_actions table
    op.create_table('corrective_actions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nonconformity_id', sa.Integer(), nullable=False),
        sa.Column('action_type', actiontype_enum, nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('implementation_plan', sa.Text(), nullable=True),
        sa.Column('resources_required', sa.Text(), nullable=True),
        sa.Column('responsible_id', sa.Integer(), nullable=False),
        sa.Column('status', actionstatus_enum, nullable=False),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('completion_date', sa.Date(), nullable=True),
        sa.Column('verification_method', sa.Text(), nullable=True),
        sa.Column('verification_criteria', sa.Text(), nullable=True),
        sa.Column('verification_date', sa.Date(), nullable=True),
        sa.Column('verification_result', sa.Text(), nullable=True),
        sa.Column('is_effective', sa.Boolean(), nullable=True),
        sa.Column('verified_by_id', sa.Integer(), nullable=True),
        sa.Column('evidence_description', sa.Text(), nullable=True),
        sa.Column('evidence_path', sa.String(length=500), nullable=True),
        sa.Column('estimated_cost', sa.Float(), nullable=True),
        sa.Column('actual_cost', sa.Float(), nullable=True),
        sa.Column('priority', sa.Integer(), default=3),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['nonconformity_id'], ['nonconformities.id'], ),
        sa.ForeignKeyConstraint(['responsible_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['verified_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create nc_timeline table
    op.create_table('nc_timeline',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nonconformity_id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('event_type', nctimelineeventtype_enum, nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('old_value', sa.String(length=100), nullable=True),
        sa.Column('new_value', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['nonconformity_id'], ['nonconformities.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create nc_assets table
    op.create_table('nc_assets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nonconformity_id', sa.Integer(), nullable=False),
        sa.Column('asset_id', sa.Integer(), nullable=False),
        sa.Column('impact_description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.ForeignKeyConstraint(['nonconformity_id'], ['nonconformities.id'], ),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nonconformity_id', 'asset_id', name='unique_nc_asset')
    )

    # Create nc_attachments table
    op.create_table('nc_attachments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nonconformity_id', sa.Integer(), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('file_type', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('attachment_type', sa.String(length=50), nullable=True),
        sa.Column('uploaded_by_id', sa.Integer(), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.ForeignKeyConstraint(['nonconformity_id'], ['nonconformities.id'], ),
        sa.ForeignKeyConstraint(['uploaded_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    # Drop tables
    op.drop_table('nc_attachments')
    op.drop_table('nc_assets')
    op.drop_table('nc_timeline')
    op.drop_table('corrective_actions')

    # Drop ENUM types
    postgresql.ENUM(name='nctimelineeventtype').drop(op.get_bind())
    postgresql.ENUM(name='actionstatus').drop(op.get_bind())
    postgresql.ENUM(name='actiontype').drop(op.get_bind())
    postgresql.ENUM(name='rcamethod').drop(op.get_bind())
    postgresql.ENUM(name='ncstatus').drop(op.get_bind())
    postgresql.ENUM(name='ncseverity').drop(op.get_bind())
    postgresql.ENUM(name='ncorigin').drop(op.get_bind())

    # Revert nonconformities table changes
    with op.batch_alter_table('nonconformities', schema=None) as batch_op:
        # Re-add old columns
        batch_op.add_column(sa.Column('source', sa.VARCHAR(length=100), nullable=True))
        batch_op.add_column(sa.Column('root_cause_method', sa.VARCHAR(length=100), nullable=True))
        batch_op.add_column(sa.Column('target_date', sa.DATE(), nullable=True))
        batch_op.add_column(sa.Column('corrective_action', sa.Text(), nullable=True))

        # Drop foreign keys
        batch_op.drop_constraint('fk_nc_related_nc', type_='foreignkey')
        batch_op.drop_constraint('fk_nc_incident', type_='foreignkey')
        batch_op.drop_constraint('fk_nc_reported_by', type_='foreignkey')
        batch_op.drop_constraint('fk_nc_updated_by', type_='foreignkey')
        batch_op.drop_constraint('fk_nc_created_by', type_='foreignkey')
        batch_op.drop_constraint('fk_nc_audit', type_='foreignkey')

        # Revert column types
        batch_op.alter_column('closure_date',
               existing_type=sa.DateTime(),
               type_=sa.DATE(),
               existing_nullable=True)
        batch_op.alter_column('status',
               existing_type=ncstatus_enum,
               type_=sa.VARCHAR(length=20),
               existing_nullable=False)
        batch_op.alter_column('severity',
               existing_type=ncseverity_enum,
               type_=sa.VARCHAR(length=20),
               existing_nullable=False)

        # Drop new columns
        batch_op.drop_column('notes')
        batch_op.drop_column('updated_by_id')
        batch_op.drop_column('created_by_id')
        batch_op.drop_column('actual_cost')
        batch_op.drop_column('estimated_cost')
        batch_op.drop_column('preventive_measures')
        batch_op.drop_column('lessons_learned')
        batch_op.drop_column('sgsi_changes_implemented')
        batch_op.drop_column('sgsi_changes_description')
        batch_op.drop_column('sgsi_changes_required')
        batch_op.drop_column('is_effective')
        batch_op.drop_column('effectiveness_criteria')
        batch_op.drop_column('effectiveness_verification')
        batch_op.drop_column('similar_nc_analysis')
        batch_op.drop_column('related_nc_id')
        batch_op.drop_column('is_recurrent')
        batch_op.drop_column('contributing_factors')
        batch_op.drop_column('root_causes')
        batch_op.drop_column('rca_method')
        batch_op.drop_column('immediate_action_date')
        batch_op.drop_column('immediate_action')
        batch_op.drop_column('incident_id')
        batch_op.drop_column('audit_id')
        batch_op.drop_column('affected_controls')
        batch_op.drop_column('reported_by_id')
        batch_op.drop_column('target_closure_date')
        batch_op.drop_column('verification_date')
        batch_op.drop_column('implementation_start_date')
        batch_op.drop_column('action_plan_date')
        batch_op.drop_column('analysis_start_date')
        batch_op.drop_column('reported_date')
        batch_op.drop_column('detection_date')
        batch_op.drop_column('origin')
        batch_op.drop_column('nc_number')
