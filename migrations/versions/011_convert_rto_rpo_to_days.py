"""Convert RTO and RPO from minutes to days

Revision ID: 011_convert_rto_rpo_to_days
Revises: 010_add_task_soa_controls_relationship
Create Date: 2025-11-01

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '011_convert_rto_rpo_to_days'
down_revision = '010_add_task_soa_controls_relationship'
branch_labels = None
depends_on = None


def upgrade():
    """
    Convierte RTO y RPO de INTEGER (minutos) a FLOAT (días)
    y actualiza los valores existentes dividiendo por 1440 (minutos en un día)
    """

    # Primero, crear columnas temporales para almacenar los valores convertidos
    op.add_column('services', sa.Column('rto_days', sa.Float(), nullable=True))
    op.add_column('services', sa.Column('rpo_days', sa.Float(), nullable=True))

    # Convertir valores existentes de minutos a días (dividir por 1440)
    # RTO: minutos / 1440 = días
    # RPO: minutos / 1440 = días
    op.execute("""
        UPDATE services
        SET rto_days = CASE
            WHEN rto IS NOT NULL THEN rto::float / 1440.0
            ELSE NULL
        END
    """)

    op.execute("""
        UPDATE services
        SET rpo_days = CASE
            WHEN rpo IS NOT NULL THEN rpo::float / 1440.0
            ELSE NULL
        END
    """)

    # Eliminar las columnas antiguas
    op.drop_column('services', 'rto')
    op.drop_column('services', 'rpo')

    # Renombrar las columnas nuevas
    op.alter_column('services', 'rto_days', new_column_name='rto')
    op.alter_column('services', 'rpo_days', new_column_name='rpo')

    # Actualizar comentarios en las columnas
    op.execute("""
        COMMENT ON COLUMN services.rto IS 'Recovery Time Objective - Tiempo máximo de recuperación (días, ej: 0.5 = 12 horas)'
    """)

    op.execute("""
        COMMENT ON COLUMN services.rpo IS 'Recovery Point Objective - Máxima pérdida de datos aceptable (días, ej: 0.25 = 6 horas)'
    """)


def downgrade():
    """
    Revierte los cambios: convierte RTO y RPO de FLOAT (días) a INTEGER (minutos)
    """

    # Crear columnas temporales para almacenar los valores convertidos
    op.add_column('services', sa.Column('rto_minutes', sa.Integer(), nullable=True))
    op.add_column('services', sa.Column('rpo_minutes', sa.Integer(), nullable=True))

    # Convertir valores de días a minutos (multiplicar por 1440 y redondear)
    op.execute("""
        UPDATE services
        SET rto_minutes = CASE
            WHEN rto IS NOT NULL THEN ROUND(rto * 1440.0)::integer
            ELSE NULL
        END
    """)

    op.execute("""
        UPDATE services
        SET rpo_minutes = CASE
            WHEN rpo IS NOT NULL THEN ROUND(rpo * 1440.0)::integer
            ELSE NULL
        END
    """)

    # Eliminar las columnas en días
    op.drop_column('services', 'rto')
    op.drop_column('services', 'rpo')

    # Renombrar las columnas de vuelta
    op.alter_column('services', 'rto_minutes', new_column_name='rto')
    op.alter_column('services', 'rpo_minutes', new_column_name='rpo')

    # Restaurar comentarios originales
    op.execute("""
        COMMENT ON COLUMN services.rto IS 'Recovery Time Objective - Tiempo máximo de recuperación (minutos)'
    """)

    op.execute("""
        COMMENT ON COLUMN services.rpo IS 'Recovery Point Objective - Máxima pérdida de datos aceptable (minutos)'
    """)
