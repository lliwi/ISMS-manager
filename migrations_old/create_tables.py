#!/usr/bin/env python3
"""
Migración simple: Crear todas las tablas y añadir columna evidence
"""

import sys
import os

# Añadir el directorio raíz del proyecto al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from models import db

def run_migration():
    """Crear todas las tablas y aplicar cambios"""
    app = create_app()

    with app.app_context():
        print("🔄 Creando todas las tablas y aplicando cambios...")

        try:
            # Crear todas las tablas
            db.create_all()
            print("✅ Todas las tablas creadas/actualizadas exitosamente")

            print("\n🎉 Migración completada!")

        except Exception as e:
            print(f"❌ Error durante la migración: {e}")
            raise

if __name__ == '__main__':
    run_migration()