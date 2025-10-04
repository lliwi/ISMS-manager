"""
Script de inicialización para nuevas instalaciones
Ejecutar después del primer docker-compose up
"""
from app import create_app
from models import db
import sys

app = create_app()

def init_database():
    """Inicializa la base de datos con las tablas y datos iniciales"""
    print("=" * 60)
    print("ISMS Manager - Inicialización de Nueva Instalación")
    print("=" * 60)

    with app.app_context():
        try:
            print("\n1. Creando tablas de base de datos...")
            db.create_all()
            print("   ✓ Tablas creadas exitosamente")

            print("\n2. Verificando roles...")
            from models import Role
            roles_count = Role.query.count()
            print(f"   ✓ {roles_count} roles encontrados")

            print("\n3. Verificando usuario administrador...")
            from models import User
            admin_user = User.query.filter_by(username='admin').first()
            if admin_user:
                print(f"   ✓ Usuario admin encontrado (ID: {admin_user.id})")
                print(f"   ✓ Email: {admin_user.email}")
                print(f"   ✓ Rol: {admin_user.role.name}")
                print(f"   ✓ Cambio de contraseña requerido: {admin_user.must_change_password}")
            else:
                print("   ⚠ Usuario admin no encontrado")

            print("\n4. Verificando tipos de documentos...")
            from models import DocumentType
            doc_types = DocumentType.query.count()
            print(f"   ✓ {doc_types} tipos de documento encontrados")

            print("\n5. Verificando tabla de auditoría...")
            from models import AuditLog
            audit_count = AuditLog.query.count()
            print(f"   ✓ Tabla audit_logs operativa ({audit_count} registros)")

            print("\n" + "=" * 60)
            print("✅ Instalación completada exitosamente!")
            print("=" * 60)
            print("\nCredenciales de acceso:")
            print("  URL: http://localhost")
            print("  Usuario: admin")
            print("  Contraseña: admin123")
            print("\n⚠️  IMPORTANTE:")
            print("  - Cambia la contraseña en el primer login")
            print("  - Configura SECRET_KEY en producción")
            print("  - Habilita HTTPS para producción")
            print("\n" + "=" * 60)

        except Exception as e:
            print(f"\n❌ Error durante la inicialización: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == '__main__':
    init_database()
