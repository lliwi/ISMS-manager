"""Add document_types table

Revision ID: 001_add_document_types
Revises:
Create Date: 2025-10-02

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '001_add_document_types'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Crear tabla document_types
    op.create_table(
        'document_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('review_period_months', sa.Integer(), nullable=True, server_default='12'),
        sa.Column('requires_approval', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('approval_workflow', sa.String(length=100), nullable=True),
        sa.Column('icon', sa.String(length=50), nullable=True, server_default='fa-file'),
        sa.Column('color', sa.String(length=20), nullable=True, server_default='primary'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('order', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )

    # Insertar tipos de documento por defecto
    op.execute("""
        INSERT INTO document_types (code, name, description, review_period_months, requires_approval, icon, color, "order")
        VALUES
            ('policy', 'Política', 'Documentos de nivel estratégico que establecen las directrices generales de la organización', 24, true, 'fa-gavel', 'danger', 1),
            ('procedure', 'Procedimiento', 'Descripciones detalladas de los procesos operativos de la organización', 12, true, 'fa-list-ol', 'primary', 2),
            ('instruction', 'Instrucción', 'Guías específicas para la realización de tareas concretas', 12, false, 'fa-book', 'info', 3),
            ('record', 'Registro', 'Documentos que evidencian la ejecución de actividades', 6, false, 'fa-folder-open', 'success', 4),
            ('minutes', 'Acta', 'Registros de reuniones y decisiones tomadas', 3, false, 'fa-clipboard', 'warning', 5),
            ('form', 'Formulario', 'Plantillas para la recopilación de información', 12, false, 'fa-file-alt', 'secondary', 6),
            ('manual', 'Manual', 'Documentos de referencia y consulta', 24, true, 'fa-book-open', 'dark', 7),
            ('report', 'Informe', 'Documentos de análisis y resultados', 6, false, 'fa-chart-bar', 'info', 8)
    """)


def downgrade():
    op.drop_table('document_types')
