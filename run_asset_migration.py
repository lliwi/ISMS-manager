"""
Script para crear tablas de gestión de activos
Módulo de Inventario de Activos - Control 5.9 ISO 27001
"""
from app import create_app
from models import db
from sqlalchemy import text
import sys

app = create_app()

with app.app_context():
    print("Ejecutando migración: Crear tablas de gestión de activos...")

    try:
        # Crear tabla assets
        print("Creando tabla assets...")
        create_assets_table = """
        CREATE TABLE IF NOT EXISTS assets (
            id SERIAL PRIMARY KEY,
            asset_code VARCHAR(50) UNIQUE NOT NULL,
            name VARCHAR(200) NOT NULL,
            description TEXT,
            category VARCHAR(20) NOT NULL,
            subcategory VARCHAR(100),
            owner_id INTEGER NOT NULL REFERENCES users(id),
            custodian_id INTEGER REFERENCES users(id),
            physical_location VARCHAR(200),
            logical_location VARCHAR(200),
            department VARCHAR(100),
            classification VARCHAR(20) NOT NULL DEFAULT 'INTERNAL',
            confidentiality_level VARCHAR(20) NOT NULL DEFAULT 'MEDIUM',
            integrity_level VARCHAR(20) NOT NULL DEFAULT 'MEDIUM',
            availability_level VARCHAR(20) NOT NULL DEFAULT 'MEDIUM',
            business_value INTEGER DEFAULT 5,
            criticality INTEGER DEFAULT 5,
            manufacturer VARCHAR(100),
            model VARCHAR(100),
            serial_number VARCHAR(100),
            version VARCHAR(50),
            acquisition_date DATE,
            installation_date DATE,
            warranty_expiry DATE,
            planned_retirement DATE,
            status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
            purchase_cost FLOAT,
            current_value FLOAT,
            tags TEXT,
            acceptable_use_policy TEXT,
            handling_requirements TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by_id INTEGER REFERENCES users(id),
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_by_id INTEGER REFERENCES users(id),
            notes TEXT
        )
        """
        db.session.execute(text(create_assets_table))
        print("✅ Tabla assets creada")

        # Crear tabla asset_relationships
        print("Creando tabla asset_relationships...")
        create_relationships_table = """
        CREATE TABLE IF NOT EXISTS asset_relationships (
            id SERIAL PRIMARY KEY,
            source_asset_id INTEGER NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
            target_asset_id INTEGER NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
            relationship_type VARCHAR(50) NOT NULL,
            description TEXT,
            criticality INTEGER DEFAULT 5,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by_id INTEGER REFERENCES users(id),
            UNIQUE(source_asset_id, target_asset_id, relationship_type)
        )
        """
        db.session.execute(text(create_relationships_table))
        print("✅ Tabla asset_relationships creada")

        # Crear tabla asset_lifecycle_events
        print("Creando tabla asset_lifecycle_events...")
        create_events_table = """
        CREATE TABLE IF NOT EXISTS asset_lifecycle_events (
            id SERIAL PRIMARY KEY,
            asset_id INTEGER NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
            event_type VARCHAR(50) NOT NULL,
            event_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            description TEXT NOT NULL,
            details TEXT,
            performed_by_id INTEGER REFERENCES users(id),
            related_risk_id INTEGER,
            related_incident_id INTEGER,
            related_control_id INTEGER
        )
        """
        db.session.execute(text(create_events_table))
        print("✅ Tabla asset_lifecycle_events creada")

        # Crear tabla asset_controls
        print("Creando tabla asset_controls...")
        create_controls_table = """
        CREATE TABLE IF NOT EXISTS asset_controls (
            id SERIAL PRIMARY KEY,
            asset_id INTEGER NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
            control_code VARCHAR(10) NOT NULL,
            control_name VARCHAR(200) NOT NULL,
            implementation_status VARCHAR(50),
            effectiveness INTEGER,
            implementation_description TEXT,
            evidence TEXT,
            implemented_date DATE,
            last_review_date DATE,
            next_review_date DATE,
            responsible_id INTEGER REFERENCES users(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(asset_id, control_code)
        )
        """
        db.session.execute(text(create_controls_table))
        print("✅ Tabla asset_controls creada")

        # Crear índices para mejorar el rendimiento
        print("Creando índices...")
        indices = [
            "CREATE INDEX IF NOT EXISTS idx_assets_owner ON assets(owner_id)",
            "CREATE INDEX IF NOT EXISTS idx_assets_category ON assets(category)",
            "CREATE INDEX IF NOT EXISTS idx_assets_status ON assets(status)",
            "CREATE INDEX IF NOT EXISTS idx_assets_classification ON assets(classification)",
            "CREATE INDEX IF NOT EXISTS idx_assets_created_at ON assets(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_asset_relationships_source ON asset_relationships(source_asset_id)",
            "CREATE INDEX IF NOT EXISTS idx_asset_relationships_target ON asset_relationships(target_asset_id)",
            "CREATE INDEX IF NOT EXISTS idx_asset_events_asset ON asset_lifecycle_events(asset_id)",
            "CREATE INDEX IF NOT EXISTS idx_asset_events_date ON asset_lifecycle_events(event_date DESC)",
            "CREATE INDEX IF NOT EXISTS idx_asset_controls_asset ON asset_controls(asset_id)",
        ]

        for index in indices:
            db.session.execute(text(index))

        print("✅ Índices creados")

        db.session.commit()
        print("\n✅ Migración de activos completada exitosamente!")
        print("\nTablas creadas:")
        print("  - assets (Inventario principal)")
        print("  - asset_relationships (Dependencias entre activos)")
        print("  - asset_lifecycle_events (Historial de eventos)")
        print("  - asset_controls (Controles aplicados)")

    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Error durante la migración: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
