"""Migración 007: Agregar tablas de Servicios

Revision ID: 007
Revises: 006
Create Date: 2025-10-12 17:12:34

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None

def upgrade():
    """Ejecutar migración"""
    # Crear tipos ENUM
    servicetype_enum = postgresql.ENUM(
        'BUSINESS', 'TECHNICAL', 'INFRASTRUCTURE', 'APPLICATION', 'SUPPORT',
        name='servicetype'
    )
    servicetype_enum.create(op.get_bind(), checkfirst=True)

    servicestatus_enum = postgresql.ENUM(
        'ACTIVE', 'INACTIVE', 'DEPRECATED', 'PLANNED',
        name='servicestatus'
    )
    servicestatus_enum.create(op.get_bind(), checkfirst=True)

    # Crear tabla services
    op.create_table(
        'services',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('service_code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('service_type', servicetype_enum, nullable=False),
        sa.Column('status', servicestatus_enum, server_default='ACTIVE', nullable=True),
        sa.Column('service_owner_id', sa.Integer(), nullable=False),
        sa.Column('technical_manager_id', sa.Integer(), nullable=True),
        sa.Column('criticality', sa.Integer(), server_default='5', nullable=True),
        sa.Column('required_availability', sa.Float(), nullable=True),
        sa.Column('rto', sa.Integer(), nullable=True),
        sa.Column('rpo', sa.Integer(), nullable=True),
        sa.Column('operating_hours', sa.String(length=100), nullable=True),
        sa.Column('max_users', sa.Integer(), nullable=True),
        sa.Column('department', sa.String(length=100), nullable=True),
        sa.Column('annual_cost', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('created_by_id', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_by_id', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.CheckConstraint('criticality >= 1 AND criticality <= 10', name='services_criticality_check'),
        sa.CheckConstraint('required_availability >= 0 AND required_availability <= 100', name='services_required_availability_check'),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['service_owner_id'], ['users.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['technical_manager_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['updated_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('service_code')
    )

    # Índices para services
    op.create_index('idx_services_code', 'services', ['service_code'])
    op.create_index('idx_services_type', 'services', ['service_type'])
    op.create_index('idx_services_status', 'services', ['status'])
    op.create_index('idx_services_owner', 'services', ['service_owner_id'])
    op.create_index('idx_services_department', 'services', ['department'])

    # Crear tabla service_asset_association
    op.create_table(
        'service_asset_association',
        sa.Column('service_id', sa.Integer(), nullable=False),
        sa.Column('asset_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['service_id'], ['services.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('service_id', 'asset_id')
    )

    # Índices para service_asset_association
    op.create_index('idx_service_asset_service', 'service_asset_association', ['service_id'])
    op.create_index('idx_service_asset_asset', 'service_asset_association', ['asset_id'])

    # Crear tabla service_dependencies
    op.create_table(
        'service_dependencies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('service_id', sa.Integer(), nullable=False),
        sa.Column('depends_on_service_id', sa.Integer(), nullable=False),
        sa.Column('dependency_type', sa.String(length=50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.CheckConstraint('service_id != depends_on_service_id', name='no_self_dependency'),
        sa.ForeignKeyConstraint(['depends_on_service_id'], ['services.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['service_id'], ['services.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('service_id', 'depends_on_service_id', name='unique_dependency')
    )

    # Índices para service_dependencies
    op.create_index('idx_service_deps_service', 'service_dependencies', ['service_id'])
    op.create_index('idx_service_deps_depends_on', 'service_dependencies', ['depends_on_service_id'])


def downgrade():
    """Revertir migración"""
    # Eliminar tablas en orden inverso
    op.drop_index('idx_service_deps_depends_on', table_name='service_dependencies')
    op.drop_index('idx_service_deps_service', table_name='service_dependencies')
    op.drop_table('service_dependencies')

    op.drop_index('idx_service_asset_asset', table_name='service_asset_association')
    op.drop_index('idx_service_asset_service', table_name='service_asset_association')
    op.drop_table('service_asset_association')

    op.drop_index('idx_services_department', table_name='services')
    op.drop_index('idx_services_owner', table_name='services')
    op.drop_index('idx_services_status', table_name='services')
    op.drop_index('idx_services_type', table_name='services')
    op.drop_index('idx_services_code', table_name='services')
    op.drop_table('services')

    # Eliminar tipos ENUM
    servicestatus_enum = postgresql.ENUM(name='servicestatus')
    servicestatus_enum.drop(op.get_bind(), checkfirst=True)

    servicetype_enum = postgresql.ENUM(name='servicetype')
    servicetype_enum.drop(op.get_bind(), checkfirst=True)
