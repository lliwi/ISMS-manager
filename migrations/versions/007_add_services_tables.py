"""
Migración 007: Agregar tablas de Servicios
- Tabla services
- Tabla service_asset_association
- Tabla service_dependencies
- Enums ServiceType y ServiceStatus
"""
from application import create_app
from models import db
import sys

def upgrade():
    """Ejecutar migración"""
    app = create_app()

    with app.app_context():
        # Ejecutar SQL directamente
        with open('migrations/versions/007_add_services_tables.sql', 'r') as f:
            sql = f.read()

        # Ejecutar cada comando SQL
        for statement in sql.split(';'):
            if statement.strip():
                try:
                    db.session.execute(db.text(statement))
                    db.session.commit()
                    print(f"✓ Ejecutado: {statement[:50]}...")
                except Exception as e:
                    print(f"✗ Error: {e}")
                    print(f"  SQL: {statement[:100]}")
                    db.session.rollback()
                    raise

        print("\n✓ Migración 007 completada exitosamente")

def downgrade():
    """Revertir migración"""
    app = create_app()

    with app.app_context():
        # Eliminar tablas en orden inverso
        db.session.execute(db.text("DROP TABLE IF EXISTS service_dependencies CASCADE"))
        db.session.execute(db.text("DROP TABLE IF EXISTS service_asset_association CASCADE"))
        db.session.execute(db.text("DROP TABLE IF EXISTS services CASCADE"))
        db.session.execute(db.text("DROP TYPE IF EXISTS servicetype CASCADE"))
        db.session.execute(db.text("DROP TYPE IF EXISTS servicestatus CASCADE"))
        db.session.commit()

        print("✓ Migración 007 revertida")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'downgrade':
        downgrade()
    else:
        upgrade()
