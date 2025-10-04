"""Add asset_types table and asset_type_id to assets

Revision ID: 004
Revises: 003
Create Date: 2025-10-04

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    """Add asset_types table and asset_type_id column to assets table"""

    # Create asset_types table
    op.create_table('asset_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.Enum('HARDWARE', 'SOFTWARE', 'INFORMATION', 'SERVICES', 'PEOPLE', 'FACILITIES', name='assetcategory'), nullable=False),
        sa.Column('icon', sa.String(length=50), nullable=True),
        sa.Column('color', sa.String(length=20), nullable=True),
        sa.Column('custom_fields', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('order', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )

    # Add asset_type_id column to assets table
    op.add_column('assets', sa.Column('asset_type_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_assets_asset_type_id', 'assets', 'asset_types', ['asset_type_id'], ['id'])


def downgrade():
    """Remove asset_types table and asset_type_id column from assets table"""

    # Remove foreign key and column from assets
    op.drop_constraint('fk_assets_asset_type_id', 'assets', type_='foreignkey')
    op.drop_column('assets', 'asset_type_id')

    # Drop asset_types table
    op.drop_table('asset_types')
