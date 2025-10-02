#!/usr/bin/env python3
"""
Migración: Actualizar campos de aplicabilidad SOA
- Agregar campo applicability_status
- Agregar campo transfer_details
- Migrar datos existentes de is_applicable a applicability_status
- Actualizar implementation_status values
"""

import psycopg2
import os
from datetime import datetime

def get_db_connection():
    """Crear conexión a la base de datos"""
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'isms_db'),
        user=os.getenv('DB_USER', 'isms_user'),
        password=os.getenv('DB_PASSWORD', 'isms_password'),
        port=os.getenv('DB_PORT', '5432')
    )

def run_migration():
    """Ejecutar la migración"""
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        print("Iniciando migración de aplicabilidad SOA...")

        # 1. Agregar nueva columna applicability_status
        print("1. Agregando columna applicability_status...")
        cur.execute("""
            ALTER TABLE soa_controls
            ADD COLUMN IF NOT EXISTS applicability_status VARCHAR(20) DEFAULT 'aplicable'
        """)

        # 2. Agregar nueva columna transfer_details
        print("2. Agregando columna transfer_details...")
        cur.execute("""
            ALTER TABLE soa_controls
            ADD COLUMN IF NOT EXISTS transfer_details TEXT
        """)

        # 3. Migrar datos existentes de is_applicable a applicability_status
        print("3. Migrando datos existentes...")
        cur.execute("""
            UPDATE soa_controls
            SET applicability_status = CASE
                WHEN is_applicable = true THEN 'aplicable'
                WHEN is_applicable = false THEN 'no_aplicable'
                ELSE 'aplicable'
            END
            WHERE applicability_status IS NULL OR applicability_status = 'aplicable'
        """)

        # 4. Actualizar implementation_status: 'pending' -> 'not_implemented'
        print("4. Actualizando estados de implementación...")
        cur.execute("""
            UPDATE soa_controls
            SET implementation_status = 'not_implemented'
            WHERE implementation_status = 'pending'
        """)

        # 5. Actualizar implementation_status: 'not_applicable' -> 'not_implemented'
        # y aplicability_status a 'no_aplicable'
        cur.execute("""
            UPDATE soa_controls
            SET implementation_status = 'not_implemented',
                applicability_status = 'no_aplicable'
            WHERE implementation_status = 'not_applicable'
        """)

        # Confirmar cambios
        conn.commit()
        print("✅ Migración completada exitosamente")

        # Mostrar estadísticas
        cur.execute("""
            SELECT
                applicability_status,
                COUNT(*) as count
            FROM soa_controls
            GROUP BY applicability_status
            ORDER BY applicability_status
        """)

        print("\nEstadísticas de aplicabilidad:")
        for row in cur.fetchall():
            print(f"  {row[0]}: {row[1]} controles")

        cur.execute("""
            SELECT
                implementation_status,
                COUNT(*) as count
            FROM soa_controls
            GROUP BY implementation_status
            ORDER BY implementation_status
        """)

        print("\nEstadísticas de implementación:")
        for row in cur.fetchall():
            print(f"  {row[0]}: {row[1]} controles")

    except Exception as e:
        conn.rollback()
        print(f"❌ Error durante la migración: {e}")
        raise
    finally:
        cur.close()
        conn.close()

def rollback_migration():
    """Revertir la migración (opcional)"""
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        print("Revirtiendo migración...")

        # Revertir implementation_status changes
        cur.execute("""
            UPDATE soa_controls
            SET implementation_status = 'pending'
            WHERE implementation_status = 'not_implemented' AND applicability_status = 'aplicable'
        """)

        cur.execute("""
            UPDATE soa_controls
            SET implementation_status = 'not_applicable'
            WHERE applicability_status = 'no_aplicable'
        """)

        # Eliminar las nuevas columnas
        cur.execute("ALTER TABLE soa_controls DROP COLUMN IF EXISTS transfer_details")
        cur.execute("ALTER TABLE soa_controls DROP COLUMN IF EXISTS applicability_status")

        conn.commit()
        print("✅ Rollback completado")

    except Exception as e:
        conn.rollback()
        print(f"❌ Error durante rollback: {e}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback_migration()
    else:
        run_migration()