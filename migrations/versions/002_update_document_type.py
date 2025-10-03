"""Update document_type to use foreign key

Revision ID: 002_update_document_type
Revises: 001_add_document_types
Create Date: 2025-10-03

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_update_document_type'
down_revision = '001_add_document_types'
branch_labels = None
depends_on = None


def upgrade():
    # Agregar nueva columna document_type_id (nullable temporalmente)
    op.add_column('documents', sa.Column('document_type_id', sa.Integer(), nullable=True))

    # Migrar datos existentes: mapear valores string a IDs de la tabla document_types
    op.execute("""
        UPDATE documents d
        SET document_type_id = dt.id
        FROM document_types dt
        WHERE d.document_type = dt.code
    """)

    # Hacer la columna NOT NULL después de migrar los datos
    op.alter_column('documents', 'document_type_id', nullable=False)

    # Agregar clave foránea
    op.create_foreign_key(
        'fk_documents_document_type_id',
        'documents', 'document_types',
        ['document_type_id'], ['id']
    )

    # Eliminar la columna antigua document_type
    op.drop_column('documents', 'document_type')


def downgrade():
    # Recrear la columna document_type
    op.add_column('documents', sa.Column('document_type', sa.String(length=50), nullable=True))

    # Migrar datos de vuelta
    op.execute("""
        UPDATE documents d
        SET document_type = dt.code
        FROM document_types dt
        WHERE d.document_type_id = dt.id
    """)

    # Hacer la columna NOT NULL
    op.alter_column('documents', 'document_type', nullable=False)

    # Eliminar clave foránea y columna document_type_id
    op.drop_constraint('fk_documents_document_type_id', 'documents', type_='foreignkey')
    op.drop_column('documents', 'document_type_id')
