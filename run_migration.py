"""
Script para ejecutar las migraciones manualmente
"""
from app import create_app
from models import db
from sqlalchemy import text
import sys

app = create_app()

with app.app_context():
    print("Ejecutando migración 003: Agregar campos de seguridad a usuarios...")

    try:
        # Agregar campos de seguridad a users
        migrations = [
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR(20)",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS failed_login_attempts INTEGER DEFAULT 0",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS account_locked_until TIMESTAMP",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS password_changed_at TIMESTAMP",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS must_change_password BOOLEAN DEFAULT FALSE",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_password_change_notification TIMESTAMP",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login_ip VARCHAR(45)",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_activity TIMESTAMP",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS created_by_id INTEGER",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_by_id INTEGER",
        ]

        for migration in migrations:
            print(f"Ejecutando: {migration}")
            db.session.execute(text(migration))

        # Agregar foreign keys (con manejo de existencia)
        print("Agregando foreign keys...")
        fk_migrations = [
            ("fk_users_created_by", "ALTER TABLE users ADD CONSTRAINT fk_users_created_by FOREIGN KEY (created_by_id) REFERENCES users(id)"),
            ("fk_users_updated_by", "ALTER TABLE users ADD CONSTRAINT fk_users_updated_by FOREIGN KEY (updated_by_id) REFERENCES users(id)"),
        ]

        for fk_name, fk_sql in fk_migrations:
            try:
                # Verificar si el FK ya existe
                check_fk = text("""
                    SELECT COUNT(*) FROM information_schema.table_constraints
                    WHERE constraint_name = :fk_name AND table_name = 'users'
                """)
                result = db.session.execute(check_fk, {'fk_name': fk_name}).scalar()

                if result == 0:
                    print(f"  - Creando FK: {fk_name}")
                    db.session.execute(text(fk_sql))
                else:
                    print(f"  - FK {fk_name} ya existe, omitiendo")
            except Exception as e:
                print(f"  - Error con FK {fk_name}: {e}")
                # Continuar sin hacer rollback todavía

        # Crear tabla audit_logs
        print("Creando tabla audit_logs...")
        create_audit_table = """
        CREATE TABLE IF NOT EXISTS audit_logs (
            id SERIAL PRIMARY KEY,
            action VARCHAR(50) NOT NULL,
            entity_type VARCHAR(50),
            entity_id INTEGER,
            description TEXT,
            old_values JSONB,
            new_values JSONB,
            user_id INTEGER REFERENCES users(id),
            username VARCHAR(80),
            ip_address VARCHAR(45),
            user_agent VARCHAR(255),
            session_id VARCHAR(255),
            status VARCHAR(20) DEFAULT 'success',
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        db.session.execute(text(create_audit_table))

        # Crear índices
        print("Creando índices...")
        indices = [
            "CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action)",
            "CREATE INDEX IF NOT EXISTS idx_audit_logs_entity ON audit_logs(entity_type, entity_id)",
        ]

        for index in indices:
            db.session.execute(text(index))

        # Inicializar password_changed_at para usuarios existentes
        print("Inicializando password_changed_at para usuarios existentes...")
        db.session.execute(text(
            "UPDATE users SET password_changed_at = created_at WHERE password_changed_at IS NULL"
        ))

        db.session.commit()
        print("✅ Migración completada exitosamente!")

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error durante la migración: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
