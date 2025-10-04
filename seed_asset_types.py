"""
Script para poblar tipos de activos iniciales en el sistema
Ejecutar: python seed_asset_types.py
"""

from app import create_app
from models import db, AssetType, AssetCategory

app = create_app()

def seed_asset_types():
    """Crea tipos de activos iniciales basados en las categorías ISO 27001"""

    asset_types_data = [
        # Hardware
        {
            'code': 'SERVIDOR',
            'name': 'Servidor',
            'description': 'Servidores físicos o virtuales que hospedan aplicaciones y servicios',
            'category': AssetCategory.HARDWARE,
            'icon': 'fa-server',
            'color': 'primary',
            'order': 1
        },
        {
            'code': 'WORKSTATION',
            'name': 'Estación de Trabajo',
            'description': 'PCs de escritorio y laptops utilizados por los empleados',
            'category': AssetCategory.HARDWARE,
            'icon': 'fa-desktop',
            'color': 'primary',
            'order': 2
        },
        {
            'code': 'LAPTOP',
            'name': 'Laptop',
            'description': 'Computadoras portátiles',
            'category': AssetCategory.HARDWARE,
            'icon': 'fa-laptop',
            'color': 'info',
            'order': 3
        },
        {
            'code': 'MOVIL',
            'name': 'Dispositivo Móvil',
            'description': 'Smartphones y tablets corporativos',
            'category': AssetCategory.HARDWARE,
            'icon': 'fa-mobile-alt',
            'color': 'info',
            'order': 4
        },
        {
            'code': 'RED_EQUIPO',
            'name': 'Equipo de Red',
            'description': 'Routers, switches, firewalls y otros dispositivos de red',
            'category': AssetCategory.HARDWARE,
            'icon': 'fa-network-wired',
            'color': 'warning',
            'order': 5
        },
        {
            'code': 'ALMACENAMIENTO',
            'name': 'Almacenamiento',
            'description': 'Dispositivos de almacenamiento (SAN, NAS, discos externos)',
            'category': AssetCategory.HARDWARE,
            'icon': 'fa-hdd',
            'color': 'dark',
            'order': 6
        },
        {
            'code': 'IMPRESORA',
            'name': 'Impresora/Multifunción',
            'description': 'Impresoras y equipos multifunción',
            'category': AssetCategory.HARDWARE,
            'icon': 'fa-print',
            'color': 'secondary',
            'order': 7
        },

        # Software
        {
            'code': 'SISTEMA_OPERATIVO',
            'name': 'Sistema Operativo',
            'description': 'Software base del sistema (Windows, Linux, etc.)',
            'category': AssetCategory.SOFTWARE,
            'icon': 'fa-cogs',
            'color': 'success',
            'order': 10
        },
        {
            'code': 'APLICACION_NEGOCIO',
            'name': 'Aplicación de Negocio',
            'description': 'Aplicaciones críticas para el negocio (ERP, CRM, etc.)',
            'category': AssetCategory.SOFTWARE,
            'icon': 'fa-briefcase',
            'color': 'primary',
            'order': 11
        },
        {
            'code': 'BASE_DATOS',
            'name': 'Sistema de Base de Datos',
            'description': 'Motores de bases de datos (MySQL, PostgreSQL, SQL Server, etc.)',
            'category': AssetCategory.SOFTWARE,
            'icon': 'fa-database',
            'color': 'danger',
            'order': 12
        },
        {
            'code': 'APLICACION_WEB',
            'name': 'Aplicación Web',
            'description': 'Aplicaciones web y portales',
            'category': AssetCategory.SOFTWARE,
            'icon': 'fa-globe',
            'color': 'info',
            'order': 13
        },
        {
            'code': 'SEGURIDAD_SOFTWARE',
            'name': 'Software de Seguridad',
            'description': 'Antivirus, EDR, firewalls de aplicación, etc.',
            'category': AssetCategory.SOFTWARE,
            'icon': 'fa-shield-alt',
            'color': 'warning',
            'order': 14
        },
        {
            'code': 'BACKUP_SOFTWARE',
            'name': 'Software de Respaldo',
            'description': 'Soluciones de backup y recuperación',
            'category': AssetCategory.SOFTWARE,
            'icon': 'fa-save',
            'color': 'success',
            'order': 15
        },
        {
            'code': 'LICENCIA_SOFTWARE',
            'name': 'Licencia de Software',
            'description': 'Licencias de software comercial',
            'category': AssetCategory.SOFTWARE,
            'icon': 'fa-key',
            'color': 'dark',
            'order': 16
        },

        # Información
        {
            'code': 'BASE_DATOS_INFO',
            'name': 'Base de Datos',
            'description': 'Bases de datos con información corporativa',
            'category': AssetCategory.INFORMATION,
            'icon': 'fa-table',
            'color': 'danger',
            'order': 20
        },
        {
            'code': 'ARCHIVO_DIGITAL',
            'name': 'Archivo Digital',
            'description': 'Archivos y documentos digitales',
            'category': AssetCategory.INFORMATION,
            'icon': 'fa-file-alt',
            'color': 'info',
            'order': 21
        },
        {
            'code': 'BACKUP_DATOS',
            'name': 'Respaldo de Información',
            'description': 'Copias de seguridad de datos críticos',
            'category': AssetCategory.INFORMATION,
            'icon': 'fa-clone',
            'color': 'success',
            'order': 22
        },
        {
            'code': 'DOCUMENTO_FISICO',
            'name': 'Documento Físico',
            'description': 'Documentos en papel y archivos físicos',
            'category': AssetCategory.INFORMATION,
            'icon': 'fa-file',
            'color': 'secondary',
            'order': 23
        },
        {
            'code': 'PROPIEDAD_INTELECTUAL',
            'name': 'Propiedad Intelectual',
            'description': 'Código fuente, diseños, patentes, información confidencial',
            'category': AssetCategory.INFORMATION,
            'icon': 'fa-copyright',
            'color': 'warning',
            'order': 24
        },

        # Servicios
        {
            'code': 'CLOUD_SERVICE',
            'name': 'Servicio Cloud',
            'description': 'Servicios en la nube (SaaS, PaaS, IaaS)',
            'category': AssetCategory.SERVICES,
            'icon': 'fa-cloud',
            'color': 'info',
            'order': 30
        },
        {
            'code': 'HOSTING',
            'name': 'Servicio de Hosting',
            'description': 'Servicios de hospedaje web y aplicaciones',
            'category': AssetCategory.SERVICES,
            'icon': 'fa-server',
            'color': 'primary',
            'order': 31
        },
        {
            'code': 'INTERNET',
            'name': 'Conexión a Internet',
            'description': 'Enlaces de internet y conectividad',
            'category': AssetCategory.SERVICES,
            'icon': 'fa-wifi',
            'color': 'success',
            'order': 32
        },
        {
            'code': 'TELEFONIA',
            'name': 'Servicio de Telefonía',
            'description': 'Servicios de telefonía fija y móvil',
            'category': AssetCategory.SERVICES,
            'icon': 'fa-phone',
            'color': 'dark',
            'order': 33
        },
        {
            'code': 'OUTSOURCING',
            'name': 'Servicio Externalizado',
            'description': 'Servicios tercerizados o de outsourcing',
            'category': AssetCategory.SERVICES,
            'icon': 'fa-handshake',
            'color': 'warning',
            'order': 34
        },
        {
            'code': 'EMAIL',
            'name': 'Servicio de Email',
            'description': 'Servicios de correo electrónico',
            'category': AssetCategory.SERVICES,
            'icon': 'fa-envelope',
            'color': 'secondary',
            'order': 35
        },

        # Personas
        {
            'code': 'PERSONAL_CLAVE',
            'name': 'Personal Clave',
            'description': 'Personas con conocimientos o habilidades críticas',
            'category': AssetCategory.PEOPLE,
            'icon': 'fa-user-tie',
            'color': 'primary',
            'order': 40
        },
        {
            'code': 'ADMINISTRADOR_SISTEMA',
            'name': 'Administrador de Sistemas',
            'description': 'Personal con privilegios administrativos',
            'category': AssetCategory.PEOPLE,
            'icon': 'fa-user-cog',
            'color': 'danger',
            'order': 41
        },
        {
            'code': 'DESARROLLADOR',
            'name': 'Desarrollador',
            'description': 'Personal de desarrollo de software',
            'category': AssetCategory.PEOPLE,
            'icon': 'fa-code',
            'color': 'info',
            'order': 42
        },
        {
            'code': 'CONTRATISTA',
            'name': 'Contratista/Consultor',
            'description': 'Personal externo con acceso a sistemas',
            'category': AssetCategory.PEOPLE,
            'icon': 'fa-user-friends',
            'color': 'warning',
            'order': 43
        },

        # Instalaciones
        {
            'code': 'CENTRO_DATOS',
            'name': 'Centro de Datos',
            'description': 'Data center o sala de servidores',
            'category': AssetCategory.FACILITIES,
            'icon': 'fa-building',
            'color': 'primary',
            'order': 50
        },
        {
            'code': 'OFICINA',
            'name': 'Oficina',
            'description': 'Espacios de oficina y trabajo',
            'category': AssetCategory.FACILITIES,
            'icon': 'fa-city',
            'color': 'info',
            'order': 51
        },
        {
            'code': 'SALA_REUNIONES',
            'name': 'Sala de Reuniones',
            'description': 'Salas de conferencias y reuniones',
            'category': AssetCategory.FACILITIES,
            'icon': 'fa-users',
            'color': 'secondary',
            'order': 52
        },
        {
            'code': 'ALMACEN',
            'name': 'Almacén',
            'description': 'Áreas de almacenamiento físico',
            'category': AssetCategory.FACILITIES,
            'icon': 'fa-warehouse',
            'color': 'dark',
            'order': 53
        },
    ]

    with app.app_context():
        print("Iniciando carga de tipos de activos...")

        created_count = 0
        skipped_count = 0

        for type_data in asset_types_data:
            # Verificar si ya existe
            existing = AssetType.query.filter_by(code=type_data['code']).first()

            if existing:
                print(f"  ⚠️  Tipo '{type_data['code']}' ya existe, omitiendo...")
                skipped_count += 1
                continue

            # Crear nuevo tipo
            new_type = AssetType(
                code=type_data['code'],
                name=type_data['name'],
                description=type_data['description'],
                category=type_data['category'],
                icon=type_data['icon'],
                color=type_data['color'],
                is_active=True,
                order=type_data['order']
            )

            db.session.add(new_type)
            created_count += 1
            print(f"  ✓ Creado: {type_data['name']} ({type_data['code']})")

        # Confirmar cambios
        db.session.commit()

        print(f"\n✅ Proceso completado:")
        print(f"   - Tipos creados: {created_count}")
        print(f"   - Tipos omitidos (ya existían): {skipped_count}")
        print(f"   - Total de tipos en DB: {AssetType.query.count()}")


if __name__ == '__main__':
    print("=" * 60)
    print("CARGA DE TIPOS DE ACTIVOS INICIALES - ISO 27001")
    print("=" * 60)
    print()

    seed_asset_types()

    print()
    print("=" * 60)
