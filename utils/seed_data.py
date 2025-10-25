"""
Seed initial data for the ISMS Manager application.
This module creates essential data like admin user, roles, and reference data.
"""
from models import db, User, Role, DocumentType, AssetType, AssetCategory, DepreciationPeriod
from werkzeug.security import generate_password_hash
from datetime import datetime
import traceback


def seed_initial_data():
    """
    Seed initial data for the application.
    This function is idempotent - it can be run multiple times safely.
    """
    try:
        # Seed roles
        seed_roles()

        # Seed admin user
        seed_admin_user()

        # Seed document types
        seed_document_types()

        # Seed asset types
        seed_asset_types()

        # Seed depreciation periods
        seed_depreciation_periods()

        # Seed ISO versions
        seed_iso_versions()

        # Seed MAGERIT threats catalog
        seed_amenazas()

        db.session.commit()
        print("✅ Initial data seeded successfully")

    except Exception as e:
        db.session.rollback()
        print(f"⚠️  Warning: Error seeding initial data: {str(e)}")
        traceback.print_exc()


def seed_roles():
    """Create default roles if they don't exist"""
    roles_data = [
        {
            'name': 'Administrador del Sistema',
            'description': 'Acceso completo al sistema'
        },
        {
            'name': 'Responsable de Seguridad (CISO)',
            'description': 'Gestión del SGSI'
        },
        {
            'name': 'Auditor Interno',
            'description': 'Realización de auditorías'
        },
        {
            'name': 'Responsable de Proceso',
            'description': 'Gestión de procesos específicos'
        },
        {
            'name': 'Usuario General',
            'description': 'Acceso básico al sistema'
        }
    ]

    for role_data in roles_data:
        role = Role.query.filter_by(name=role_data['name']).first()
        if not role:
            role = Role(
                name=role_data['name'],
                description=role_data['description']
            )
            db.session.add(role)
            print(f"  → Created role: {role_data['name']}")


def seed_admin_user():
    """Create default admin user if it doesn't exist"""
    admin = User.query.filter_by(username='admin').first()

    if not admin:
        admin_role = Role.query.filter_by(name='Administrador del Sistema').first()

        admin = User(
            username='admin',
            email='admin@empresa.com',
            first_name='Administrador',
            last_name='del Sistema',
            password_hash=generate_password_hash('admin123'),
            is_active=True,
            role_id=admin_role.id if admin_role else None,
            created_at=datetime.utcnow()
        )
        db.session.add(admin)
        print("  → Created admin user (username: admin, password: admin123)")
    else:
        print("  → Admin user already exists")


def seed_document_types():
    """Create default document types if they don't exist"""
    document_types = [
        {'code': 'POL', 'name': 'Política', 'description': 'Documentos de políticas organizacionales'},
        {'code': 'PROC', 'name': 'Procedimiento', 'description': 'Procedimientos operativos'},
        {'code': 'INST', 'name': 'Instrucción', 'description': 'Instrucciones técnicas'},
        {'code': 'REG', 'name': 'Registro', 'description': 'Registros de actividades'},
        {'code': 'ACTA', 'name': 'Acta', 'description': 'Actas de reuniones'},
    ]

    for doc_type_data in document_types:
        doc_type = DocumentType.query.filter_by(code=doc_type_data['code']).first()
        if not doc_type:
            doc_type = DocumentType(
                code=doc_type_data['code'],
                name=doc_type_data['name'],
                description=doc_type_data['description']
            )
            db.session.add(doc_type)
            print(f"  → Created document type: {doc_type_data['name']}")


def seed_asset_types():
    """Create default asset types if they don't exist"""
    asset_types_data = [
        # Hardware
        {'code': 'HW-SRV', 'name': 'Servidor', 'category': AssetCategory.HARDWARE, 'icon': 'fa-server', 'color': 'primary'},
        {'code': 'HW-PC', 'name': 'Ordenador de Escritorio', 'category': AssetCategory.HARDWARE, 'icon': 'fa-desktop', 'color': 'primary'},
        {'code': 'HW-LAPTOP', 'name': 'Portátil', 'category': AssetCategory.HARDWARE, 'icon': 'fa-laptop', 'color': 'primary'},
        {'code': 'HW-MOBILE', 'name': 'Dispositivo Móvil', 'category': AssetCategory.HARDWARE, 'icon': 'fa-mobile-alt', 'color': 'primary'},
        {'code': 'HW-PRINTER', 'name': 'Impresora', 'category': AssetCategory.HARDWARE, 'icon': 'fa-print', 'color': 'secondary'},
        {'code': 'HW-SCANNER', 'name': 'Escáner', 'category': AssetCategory.HARDWARE, 'icon': 'fa-scanner', 'color': 'secondary'},
        {'code': 'HW-NETWORK', 'name': 'Equipo de Red', 'category': AssetCategory.HARDWARE, 'icon': 'fa-network-wired', 'color': 'info'},
        {'code': 'HW-STORAGE', 'name': 'Almacenamiento', 'category': AssetCategory.HARDWARE, 'icon': 'fa-hdd', 'color': 'warning'},

        # Software
        {'code': 'SW-OS', 'name': 'Sistema Operativo', 'category': AssetCategory.SOFTWARE, 'icon': 'fa-windows', 'color': 'info'},
        {'code': 'SW-APP', 'name': 'Aplicación de Negocio', 'category': AssetCategory.SOFTWARE, 'icon': 'fa-briefcase', 'color': 'success'},
        {'code': 'SW-DB', 'name': 'Base de Datos', 'category': AssetCategory.SOFTWARE, 'icon': 'fa-database', 'color': 'danger'},
        {'code': 'SW-OFFICE', 'name': 'Suite Ofimática', 'category': AssetCategory.SOFTWARE, 'icon': 'fa-file-word', 'color': 'info'},
        {'code': 'SW-SECURITY', 'name': 'Software de Seguridad', 'category': AssetCategory.SOFTWARE, 'icon': 'fa-shield-alt', 'color': 'danger'},
        {'code': 'SW-BACKUP', 'name': 'Software de Backup', 'category': AssetCategory.SOFTWARE, 'icon': 'fa-save', 'color': 'warning'},

        # Information
        {'code': 'INFO-DB', 'name': 'Base de Datos Corporativa', 'category': AssetCategory.INFORMATION, 'icon': 'fa-database', 'color': 'danger'},
        {'code': 'INFO-FILES', 'name': 'Archivos y Documentos', 'category': AssetCategory.INFORMATION, 'icon': 'fa-folder', 'color': 'warning'},
        {'code': 'INFO-BACKUP', 'name': 'Copias de Seguridad', 'category': AssetCategory.INFORMATION, 'icon': 'fa-copy', 'color': 'secondary'},

        # Services
        {'code': 'SVC-CLOUD', 'name': 'Servicio Cloud', 'category': AssetCategory.SERVICES, 'icon': 'fa-cloud', 'color': 'info'},
        {'code': 'SVC-EMAIL', 'name': 'Servicio de Correo', 'category': AssetCategory.SERVICES, 'icon': 'fa-envelope', 'color': 'primary'},
        {'code': 'SVC-WEB', 'name': 'Servicio Web', 'category': AssetCategory.SERVICES, 'icon': 'fa-globe', 'color': 'success'},
        {'code': 'SVC-ISP', 'name': 'Proveedor Internet', 'category': AssetCategory.SERVICES, 'icon': 'fa-wifi', 'color': 'info'},

        # People
        {'code': 'PPL-ADMIN', 'name': 'Personal Administrativo', 'category': AssetCategory.PEOPLE, 'icon': 'fa-user-tie', 'color': 'primary'},
        {'code': 'PPL-IT', 'name': 'Personal IT', 'category': AssetCategory.PEOPLE, 'icon': 'fa-user-cog', 'color': 'info'},
        {'code': 'PPL-SECURITY', 'name': 'Personal de Seguridad', 'category': AssetCategory.PEOPLE, 'icon': 'fa-user-shield', 'color': 'danger'},

        # Facilities
        {'code': 'FAC-OFFICE', 'name': 'Oficina', 'category': AssetCategory.FACILITIES, 'icon': 'fa-building', 'color': 'secondary'},
        {'code': 'FAC-DATACENTER', 'name': 'Centro de Datos', 'category': AssetCategory.FACILITIES, 'icon': 'fa-server', 'color': 'danger'},
        {'code': 'FAC-COMMS', 'name': 'Sala de Comunicaciones', 'category': AssetCategory.FACILITIES, 'icon': 'fa-broadcast-tower', 'color': 'info'},
    ]

    for type_data in asset_types_data:
        asset_type = AssetType.query.filter_by(code=type_data['code']).first()
        if not asset_type:
            asset_type = AssetType(
                code=type_data['code'],
                name=type_data['name'],
                category=type_data['category'],
                icon=type_data['icon'],
                color=type_data['color'],
                is_active=True
            )
            db.session.add(asset_type)
            print(f"  → Created asset type: {type_data['name']} ({type_data['category'].value})")


def seed_depreciation_periods():
    """Create default depreciation periods if they don't exist"""
    depreciation_data = [
        {'category': AssetCategory.HARDWARE, 'years': 5, 'description': 'Equipos informáticos y hardware', 'residual_value_percentage': 10.0},
        {'category': AssetCategory.SOFTWARE, 'years': 3, 'description': 'Licencias de software', 'residual_value_percentage': 0.0},
        {'category': AssetCategory.INFORMATION, 'years': 0, 'description': 'Información (no deprecia)', 'residual_value_percentage': 100.0},
        {'category': AssetCategory.SERVICES, 'years': 0, 'description': 'Servicios (no deprecia)', 'residual_value_percentage': 100.0},
        {'category': AssetCategory.PEOPLE, 'years': 0, 'description': 'Recursos humanos (no deprecia)', 'residual_value_percentage': 100.0},
        {'category': AssetCategory.FACILITIES, 'years': 20, 'description': 'Instalaciones e infraestructura', 'residual_value_percentage': 20.0},
    ]

    for period_data in depreciation_data:
        period = DepreciationPeriod.query.filter_by(category=period_data['category']).first()
        if not period:
            period = DepreciationPeriod(
                category=period_data['category'],
                years=period_data['years'],
                description=period_data['description'],
                residual_value_percentage=period_data['residual_value_percentage'],
                method='linear',
                is_active=True
            )
            db.session.add(period)
            print(f"  → Created depreciation period: {period_data['category'].value} ({period_data['years']} años)")


def seed_iso_versions():
    """Create default ISO versions if they don't exist"""
    from models import ISOVersion

    iso_versions_data = [
        {
            'version': '2022',
            'year': 2022,
            'title': 'ISO/IEC 27001:2022',
            'description': 'Versión actual de ISO/IEC 27001 - Requisitos para un sistema de gestión de seguridad de la información',
            'number_of_controls': 93
        },
        {
            'version': '2013',
            'year': 2013,
            'title': 'ISO/IEC 27001:2013',
            'description': 'Versión anterior de ISO/IEC 27001 (reemplazada en 2022)',
            'number_of_controls': 114
        }
    ]

    for version_data in iso_versions_data:
        iso_version = ISOVersion.query.filter_by(version=version_data['version']).first()
        if not iso_version:
            iso_version = ISOVersion(
                version=version_data['version'],
                year=version_data['year'],
                title=version_data['title'],
                description=version_data['description'],
                number_of_controls=version_data['number_of_controls'],
                is_active=True
            )
            db.session.add(iso_version)
            print(f"  → Created ISO version: {version_data['title']}")


def seed_amenazas():
    """Create MAGERIT 3.2 threats catalog if it doesn't exist"""
    from app.risks.models import Amenaza

    # Check if threats already exist
    existing_count = Amenaza.query.count()
    if existing_count > 0:
        print(f"  → Amenazas catalog already exists ({existing_count} threats)")
        return

    # Import and run the seed function in non-interactive mode
    try:
        from app.risks.seed_amenazas import seed_amenazas as load_amenazas
        load_amenazas(force_reload=False, interactive=False)

        # Count loaded threats by group
        from sqlalchemy import func
        stats = db.session.query(
            Amenaza.grupo,
            func.count(Amenaza.id).label('count')
        ).group_by(Amenaza.grupo).order_by(Amenaza.grupo).all()

        print("  → Created MAGERIT 3.2 threats catalog:")
        for grupo, count in stats:
            print(f"    • {grupo}: {count} amenazas")

    except Exception as e:
        print(f"  ⚠️  Warning: Could not load threats catalog: {str(e)}")
        # Don't fail the entire seed process if threats can't be loaded
        pass
