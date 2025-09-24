#!/usr/bin/env python3
"""
Migración: Añadir campo evidence a SOAControl y tabla de relación document_control_association
Fecha: 2025-09-24
"""

import sys
import os

# Añadir el directorio raíz del proyecto al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from models import db

def run_migration():
    """Ejecutar migración para añadir evidence field y relación document-control"""
    app = create_app()

    with app.app_context():
        print("🔄 Iniciando migración: evidence field y document-control relationship...")

        try:
            # Verificar si la migración ya fue aplicada
            with db.engine.connect() as conn:
                result = conn.execute(db.text("SELECT column_name FROM information_schema.columns WHERE table_name='soa_controls' AND column_name='evidence';"))
                evidence_exists = len(list(result)) > 0

            if evidence_exists:
                print("✅ La columna 'evidence' ya existe en soa_controls")
            else:
                # Añadir columna evidence a soa_controls
                print("📝 Añadiendo columna 'evidence' a soa_controls...")
                with db.engine.connect() as conn:
                    conn.execute(db.text("ALTER TABLE soa_controls ADD COLUMN evidence TEXT;"))
                    conn.commit()
                print("✅ Columna 'evidence' añadida exitosamente")

            # Verificar si la tabla de asociación ya existe
            with db.engine.connect() as conn:
                result = conn.execute(db.text("SELECT table_name FROM information_schema.tables WHERE table_name='document_control_association';"))
                association_exists = len(list(result)) > 0

            if association_exists:
                print("✅ La tabla 'document_control_association' ya existe")
            else:
                # Crear tabla de asociación document_control_association
                print("📝 Creando tabla 'document_control_association'...")
                with db.engine.connect() as conn:
                    conn.execute(db.text("""
                        CREATE TABLE document_control_association (
                            document_id INTEGER NOT NULL,
                            soa_control_id INTEGER NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            PRIMARY KEY (document_id, soa_control_id),
                            FOREIGN KEY(document_id) REFERENCES documents (id) ON DELETE CASCADE,
                            FOREIGN KEY(soa_control_id) REFERENCES soa_controls (id) ON DELETE CASCADE
                        );
                    """))
                    conn.commit()
                print("✅ Tabla 'document_control_association' creada exitosamente")

            print("\n🎉 Migración completada exitosamente!")

            # Mostrar estadísticas
            with db.engine.connect() as conn:
                controls_count = conn.execute(db.text("SELECT COUNT(*) FROM soa_controls;")).fetchone()[0]
                documents_count = conn.execute(db.text("SELECT COUNT(*) FROM documents;")).fetchone()[0]

            print(f"\n📊 Estado actual:")
            print(f"   • Controles SOA: {controls_count}")
            print(f"   • Documentos: {documents_count}")

        except Exception as e:
            print(f"❌ Error durante la migración: {e}")
            raise

if __name__ == '__main__':
    run_migration()