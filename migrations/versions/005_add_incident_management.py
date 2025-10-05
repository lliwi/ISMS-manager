"""Add incident management models

Revision ID: 005
Revises: 004
Create Date: 2025-10-05 06:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade():
    # Crear tipos ENUM para incidentes
    incidentcategory = postgresql.ENUM(
        'UNAUTHORIZED_ACCESS', 'MALWARE', 'PHISHING', 'DATA_LOSS', 'DATA_BREACH',
        'DENIAL_OF_SERVICE', 'MISUSE', 'SOCIAL_ENGINEERING', 'VULNERABILITY_EXPLOIT',
        'SYSTEM_FAILURE', 'HUMAN_ERROR', 'PHYSICAL_SECURITY', 'INSIDER_THREAT',
        'RANSOMWARE', 'OTHER',
        name='incidentcategory'
    )
    incidentcategory.create(op.get_bind(), checkfirst=True)

    incidentseverity = postgresql.ENUM(
        'CRITICAL', 'HIGH', 'MEDIUM', 'LOW',
        name='incidentseverity'
    )
    incidentseverity.create(op.get_bind(), checkfirst=True)

    incidentpriority = postgresql.ENUM(
        'URGENT', 'HIGH', 'NORMAL', 'LOW',
        name='incidentpriority'
    )
    incidentpriority.create(op.get_bind(), checkfirst=True)

    incidentstatus = postgresql.ENUM(
        'NEW', 'EVALUATING', 'CONFIRMED', 'IN_PROGRESS', 'CONTAINED',
        'RESOLVED', 'CLOSED', 'FALSE_POSITIVE',
        name='incidentstatus'
    )
    incidentstatus.create(op.get_bind(), checkfirst=True)

    incidentsource = postgresql.ENUM(
        'INTERNAL', 'EXTERNAL', 'UNKNOWN',
        name='incidentsource'
    )
    incidentsource.create(op.get_bind(), checkfirst=True)

    detectionmethod = postgresql.ENUM(
        'USER_REPORT', 'MONITORING', 'ANTIVIRUS', 'IDS_IPS', 'SIEM',
        'AUDIT', 'THIRD_PARTY', 'AUTOMATIC', 'OTHER',
        name='detectionmethod'
    )
    detectionmethod.create(op.get_bind(), checkfirst=True)

    actiontype = postgresql.ENUM(
        'CREATED', 'STATUS_CHANGE', 'ASSIGNED', 'COMMENT', 'EVIDENCE_ADDED',
        'ACTION_ADDED', 'NOTIFICATION_SENT', 'CONTAINMENT', 'ANALYSIS',
        'RESOLUTION', 'CLOSURE', 'REOPENED', 'ESCALATED',
        name='actiontype'
    )
    actiontype.create(op.get_bind(), checkfirst=True)

    actionstatus = postgresql.ENUM(
        'PENDING', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED',
        name='actionstatus'
    )
    actionstatus.create(op.get_bind(), checkfirst=True)

    evidencetype = postgresql.ENUM(
        'LOG_FILE', 'SCREENSHOT', 'NETWORK_CAPTURE', 'EMAIL', 'DOCUMENT',
        'PHOTO', 'VIDEO', 'MEMORY_DUMP', 'DISK_IMAGE', 'OTHER',
        name='evidencetype'
    )
    evidencetype.create(op.get_bind(), checkfirst=True)

    notificationtype = postgresql.ENUM(
        'INTERNAL_TEAM', 'MANAGEMENT', 'DPO', 'AUTHORITY', 'AFFECTED_USERS',
        'THIRD_PARTY', 'CUSTOMER', 'PROVIDER',
        name='notificationtype'
    )
    notificationtype.create(op.get_bind(), checkfirst=True)

    # Crear tabla principal de incidentes
    op.create_table('incidents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('incident_number', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', incidentcategory, nullable=False),
        sa.Column('severity', incidentseverity, nullable=False),
        sa.Column('priority', incidentpriority, nullable=False),
        sa.Column('status', incidentstatus, nullable=False),
        sa.Column('discovery_date', sa.DateTime(), nullable=False),
        sa.Column('reported_date', sa.DateTime(), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('containment_date', sa.DateTime(), nullable=True),
        sa.Column('resolution_date', sa.DateTime(), nullable=True),
        sa.Column('closure_date', sa.DateTime(), nullable=True),
        sa.Column('reported_by_id', sa.Integer(), nullable=False),
        sa.Column('assigned_to_id', sa.Integer(), nullable=True),
        sa.Column('source', incidentsource, nullable=True),
        sa.Column('detection_method', detectionmethod, nullable=False),
        sa.Column('detection_details', sa.Text(), nullable=True),
        sa.Column('impact_confidentiality', sa.Boolean(), nullable=True, default=False),
        sa.Column('impact_integrity', sa.Boolean(), nullable=True, default=False),
        sa.Column('impact_availability', sa.Boolean(), nullable=True, default=False),
        sa.Column('affected_controls', sa.Text(), nullable=True),
        sa.Column('root_cause', sa.Text(), nullable=True),
        sa.Column('contributing_factors', sa.Text(), nullable=True),
        sa.Column('resolution', sa.Text(), nullable=True),
        sa.Column('lessons_learned', sa.Text(), nullable=True),
        sa.Column('is_data_breach', sa.Boolean(), nullable=True, default=False),
        sa.Column('requires_notification', sa.Boolean(), nullable=True, default=False),
        sa.Column('notification_date', sa.DateTime(), nullable=True),
        sa.Column('estimated_cost', sa.Float(), nullable=True),
        sa.Column('affected_users_count', sa.Integer(), nullable=True),
        sa.Column('downtime_minutes', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('created_by_id', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('updated_by_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['assigned_to_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['reported_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('incident_number')
    )

    # Crear tabla de activos afectados por incidentes
    op.create_table('incident_assets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('incident_id', sa.Integer(), nullable=False),
        sa.Column('asset_id', sa.Integer(), nullable=False),
        sa.Column('impact_description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.id'], ),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('incident_id', 'asset_id', name='unique_incident_asset')
    )

    # Crear tabla de timeline de incidentes
    op.create_table('incident_timeline',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('incident_id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('action_type', actiontype, nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('attachments', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Crear tabla de acciones correctivas
    op.create_table('incident_actions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('incident_id', sa.Integer(), nullable=False),
        sa.Column('action_type', sa.String(length=50), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('responsible_id', sa.Integer(), nullable=True),
        sa.Column('status', actionstatus, nullable=True),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('completion_date', sa.Date(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ),
        sa.ForeignKeyConstraint(['responsible_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Crear tabla de evidencias
    op.create_table('incident_evidences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('incident_id', sa.Integer(), nullable=False),
        sa.Column('evidence_type', evidencetype, nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('file_name', sa.String(length=255), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('hash_value', sa.String(length=128), nullable=True),
        sa.Column('collected_by_id', sa.Integer(), nullable=False),
        sa.Column('collection_date', sa.DateTime(), nullable=False),
        sa.Column('chain_of_custody', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['collected_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Crear tabla de notificaciones
    op.create_table('incident_notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('incident_id', sa.Integer(), nullable=False),
        sa.Column('notification_type', notificationtype, nullable=False),
        sa.Column('recipient', sa.String(length=200), nullable=False),
        sa.Column('recipient_email', sa.String(length=200), nullable=True),
        sa.Column('notification_date', sa.DateTime(), nullable=False),
        sa.Column('method', sa.String(length=50), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('sent_by_id', sa.Integer(), nullable=True),
        sa.Column('acknowledgement_received', sa.Boolean(), nullable=True, default=False),
        sa.Column('acknowledgement_date', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ),
        sa.ForeignKeyConstraint(['sent_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Crear índices para optimizar consultas
    op.create_index('idx_incidents_status', 'incidents', ['status'])
    op.create_index('idx_incidents_category', 'incidents', ['category'])
    op.create_index('idx_incidents_severity', 'incidents', ['severity'])
    op.create_index('idx_incidents_reported_date', 'incidents', ['reported_date'])
    op.create_index('idx_incidents_assigned_to', 'incidents', ['assigned_to_id'])
    op.create_index('idx_incident_timeline_incident', 'incident_timeline', ['incident_id'])
    op.create_index('idx_incident_timeline_timestamp', 'incident_timeline', ['timestamp'])


def downgrade():
    # Eliminar índices
    op.drop_index('idx_incident_timeline_timestamp', table_name='incident_timeline')
    op.drop_index('idx_incident_timeline_incident', table_name='incident_timeline')
    op.drop_index('idx_incidents_assigned_to', table_name='incidents')
    op.drop_index('idx_incidents_reported_date', table_name='incidents')
    op.drop_index('idx_incidents_severity', table_name='incidents')
    op.drop_index('idx_incidents_category', table_name='incidents')
    op.drop_index('idx_incidents_status', table_name='incidents')

    # Eliminar tablas
    op.drop_table('incident_notifications')
    op.drop_table('incident_evidences')
    op.drop_table('incident_actions')
    op.drop_table('incident_timeline')
    op.drop_table('incident_assets')
    op.drop_table('incidents')

    # Eliminar tipos ENUM
    sa.Enum(name='notificationtype').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='evidencetype').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='actionstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='actiontype').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='detectionmethod').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='incidentsource').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='incidentstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='incidentpriority').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='incidentseverity').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='incidentcategory').drop(op.get_bind(), checkfirst=True)
