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

        # Seed control-threat relationships
        seed_control_amenaza_relations()

        # Seed threat-resource-type relationships
        seed_amenaza_recurso_relations()

        # Seed ISO 27001 task templates
        seed_iso27001_task_templates()

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


def seed_control_amenaza_relations():
    """Create control-threat relationships if they don't exist"""
    from app.risks.models import ControlAmenaza

    # Check if relationships already exist
    existing_count = ControlAmenaza.query.count()
    if existing_count > 0:
        print(f"  → Control-threat relationships already exist ({existing_count} relationships)")
        return

    # Import and run the seed function in non-interactive mode
    try:
        from app.risks.seed_control_amenaza import seed_control_amenaza
        seed_control_amenaza(force_reload=False, interactive=False)

        # Count loaded relationships by type
        from sqlalchemy import func
        stats = db.session.query(
            ControlAmenaza.tipo_control,
            func.count(ControlAmenaza.id).label('count')
        ).group_by(ControlAmenaza.tipo_control).order_by(ControlAmenaza.tipo_control).all()

        total = sum(count for _, count in stats)
        print(f"  → Created {total} control-threat relationships:")
        for tipo, count in stats:
            print(f"    • {tipo}: {count} relationships")

    except Exception as e:
        print(f"  ⚠️  Warning: Could not load control-threat relationships: {str(e)}")
        # Don't fail the entire seed process if relationships can't be loaded
        pass


def seed_amenaza_recurso_relations():
    """Create threat-resource-type relationships if they don't exist"""
    from app.risks.models import AmenazaRecursoTipo

    existing_count = AmenazaRecursoTipo.query.count()

    if existing_count > 0:
        print(f"  → Threat-resource relationships already exist ({existing_count} relationships)")
        return

    print("  → Loading threat-resource-type relationships...")

    try:
        from app.risks.seed_amenaza_recurso import seed_amenaza_recurso
        seed_amenaza_recurso(force_reload=False, interactive=False)

        # Show statistics
        total = AmenazaRecursoTipo.query.count()
        print(f"  ✅ Created {total} threat-resource-type relationships")

    except Exception as e:
        print(f"  ⚠️  Warning: Could not load threat-resource relationships: {str(e)}")
        # Don't fail the entire seed process if relationships can't be loaded
        pass


def seed_iso27001_task_templates():
    """
    Create ISO/IEC 27001:2023 periodic task templates for new installations.
    This function loads the complete catalog of recommended periodic tasks
    from the init_iso27001_tasks module.
    """
    from app.models.task import TaskTemplate

    # Check if task templates already exist
    existing_count = TaskTemplate.query.count()
    if existing_count > 0:
        print(f"  → Task templates already exist ({existing_count} templates)")
        return

    print("  → Loading ISO/IEC 27001:2023 task templates...")

    try:
        # Import the task templates generator
        import sys
        import os
        # Add project root to path to import the init script
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)

        from init_iso27001_tasks import get_task_templates_iso27001
        from models import Role

        # Get roles for assignment
        role_ciso = Role.query.filter_by(name='Responsable de Seguridad (CISO)').first()
        role_admin = Role.query.filter_by(name='Administrador del Sistema').first()
        role_auditor = Role.query.filter_by(name='Auditor Interno').first()

        # Get task templates
        templates_data = get_task_templates_iso27001()

        # Role mappings by category
        from app.models.task import TaskCategory
        role_mappings = {
            TaskCategory.AUDITORIA_INTERNA: role_auditor.id if role_auditor else None,
            TaskCategory.EVALUACION_RIESGOS: role_ciso.id if role_ciso else None,
            TaskCategory.REVISION_POLITICAS: role_ciso.id if role_ciso else None,
            TaskCategory.REVISION_DIRECCION: role_ciso.id if role_ciso else None,
            TaskCategory.FORMACION_CONCIENCIACION: role_ciso.id if role_ciso else None,
            TaskCategory.REVISION_PROVEEDORES: role_ciso.id if role_ciso else None,
            TaskCategory.REVISION_INCIDENTES: role_ciso.id if role_ciso else None,
            TaskCategory.CONTINUIDAD_NEGOCIO: role_ciso.id if role_ciso else None,
            TaskCategory.REVISION_LEGAL: role_ciso.id if role_ciso else None,
            TaskCategory.REVISION_CONTROLES: role_ciso.id if role_ciso else None,
            TaskCategory.MANTENIMIENTO_SEGURIDAD: role_admin.id if role_admin else None,
            TaskCategory.COPIAS_SEGURIDAD: role_admin.id if role_admin else None,
            TaskCategory.REVISION_ACCESOS: role_admin.id if role_admin else None,
            TaskCategory.ACTUALIZACION_INVENTARIOS: role_admin.id if role_admin else None,
            TaskCategory.GESTION_VULNERABILIDADES: role_admin.id if role_admin else None,
        }

        # Create templates
        created_count = 0
        for template_data in templates_data:
            # Assign default role if not specified
            if 'default_role_id' not in template_data or template_data['default_role_id'] is None:
                template_data['default_role_id'] = role_mappings.get(template_data['category'])

            template = TaskTemplate(
                title=template_data['title'],
                description=template_data['description'],
                category=template_data['category'],
                frequency=template_data['frequency'],
                priority=template_data['priority'],
                iso_control=template_data.get('iso_control'),
                estimated_hours=template_data.get('estimated_hours'),
                default_role_id=template_data.get('default_role_id'),
                notify_days_before=template_data.get('notify_days_before', 7),
                requires_evidence=template_data.get('requires_evidence', False),
                requires_approval=template_data.get('requires_approval', False),
                checklist_template=template_data.get('checklist_template'),
                is_active=True,
                created_by_id=1,  # Admin user
                created_at=datetime.utcnow()
            )

            db.session.add(template)
            created_count += 1

        # Count by frequency
        from app.models.task import TaskFrequency
        from sqlalchemy import func
        stats = db.session.query(
            TaskTemplate.frequency,
            func.count(TaskTemplate.id).label('count')
        ).group_by(TaskTemplate.frequency).all()

        print(f"  ✅ Created {created_count} ISO 27001 task templates:")
        for frequency, count in sorted(stats, key=lambda x: x[1], reverse=True):
            print(f"    • {frequency.value}: {count} templates")

    except Exception as e:
        print(f"  ⚠️  Warning: Could not load ISO 27001 task templates: {str(e)}")
        # Don't fail the entire seed process if task templates can't be loaded
        import traceback
        traceback.print_exc()
        pass
