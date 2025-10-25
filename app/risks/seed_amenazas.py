"""
Script de Precarga de Amenazas MAGERIT 3.2
Catálogo de amenazas según metodología MAGERIT v3.2 del CCN-CERT
"""

from models import db
from app.risks.models import Amenaza


# Catálogo de amenazas MAGERIT 3.2
# Organizado en 4 grupos principales
AMENAZAS_MAGERIT = [
    # ========== GRUPO 1: NATURALES ==========
    {
        'codigo': 'N.1',
        'nombre': 'Fuego',
        'descripcion': 'Incendio que destruye o daña el equipamiento, las instalaciones o los soportes de información.',
        'grupo': 'NATURALES',
        'frecuencia_base': 1,  # Muy baja (1-5)
        'facilidad_base': 3    # Media
    },
    {
        'codigo': 'N.2',
        'nombre': 'Daños por agua',
        'descripcion': 'Inundación, humedad, filtración que afecta equipamiento, instalaciones o soportes de información.',
        'grupo': 'NATURALES',
        'frecuencia_base': 2,
        'facilidad_base': 3
    },
    {
        'codigo': 'N.*',
        'nombre': 'Desastres naturales',
        'descripcion': 'Otros fenómenos naturales como terremotos, tormentas, rayos, etc.',
        'grupo': 'NATURALES',
        'frecuencia_base': 1,
        'facilidad_base': 2
    },

    # ========== GRUPO 2: INDUSTRIALES ==========
    {
        'codigo': 'I.1',
        'nombre': 'Fuego',
        'descripcion': 'Incendio de origen industrial que afecta instalaciones o equipamiento.',
        'grupo': 'INDUSTRIALES',
        'frecuencia_base': 1,
        'facilidad_base': 3
    },
    {
        'codigo': 'I.2',
        'nombre': 'Daños por agua',
        'descripcion': 'Daños por agua de origen industrial (tuberías, sistemas de refrigeración, etc.).',
        'grupo': 'INDUSTRIALES',
        'frecuencia_base': 2,
        'facilidad_base': 3
    },
    {
        'codigo': 'I.3',
        'nombre': 'Desastres industriales',
        'descripcion': 'Contaminación química, mecánica, electromagnética u otros daños de origen industrial.',
        'grupo': 'INDUSTRIALES',
        'frecuencia_base': 1,
        'facilidad_base': 2
    },
    {
        'codigo': 'I.4',
        'nombre': 'Contaminación electromagnética',
        'descripcion': 'Interferencias electromagnéticas que afectan equipos electrónicos.',
        'grupo': 'INDUSTRIALES',
        'frecuencia_base': 2,
        'facilidad_base': 3
    },
    {
        'codigo': 'I.5',
        'nombre': 'Avería de origen físico o lógico',
        'descripcion': 'Fallos en equipamiento o software por desgaste, envejecimiento o defecto de fabricación.',
        'grupo': 'INDUSTRIALES',
        'frecuencia_base': 3,
        'facilidad_base': 4
    },
    {
        'codigo': 'I.6',
        'nombre': 'Corte del suministro eléctrico',
        'descripcion': 'Interrupción del suministro eléctrico que afecta el funcionamiento de sistemas.',
        'grupo': 'INDUSTRIALES',
        'frecuencia_base': 3,
        'facilidad_base': 4
    },
    {
        'codigo': 'I.7',
        'nombre': 'Condiciones inadecuadas de temperatura o humedad',
        'descripcion': 'Fallo de sistemas de climatización que afecta el funcionamiento de equipos.',
        'grupo': 'INDUSTRIALES',
        'frecuencia_base': 2,
        'facilidad_base': 3
    },
    {
        'codigo': 'I.8',
        'nombre': 'Fallo de servicios de comunicaciones',
        'descripcion': 'Interrupción de enlaces de comunicaciones (Internet, WAN, telefonía).',
        'grupo': 'INDUSTRIALES',
        'frecuencia_base': 3,
        'facilidad_base': 4
    },
    {
        'codigo': 'I.9',
        'nombre': 'Interrupción de otros servicios y suministros esenciales',
        'descripcion': 'Fallo de servicios auxiliares necesarios para el funcionamiento de sistemas.',
        'grupo': 'INDUSTRIALES',
        'frecuencia_base': 2,
        'facilidad_base': 3
    },
    {
        'codigo': 'I.10',
        'nombre': 'Degradación de los soportes de almacenamiento de la información',
        'descripcion': 'Deterioro de medios de almacenamiento por envejecimiento o desgaste.',
        'grupo': 'INDUSTRIALES',
        'frecuencia_base': 2,
        'facilidad_base': 3
    },
    {
        'codigo': 'I.11',
        'nombre': 'Emanaciones electromagnéticas',
        'descripcion': 'Fuga de información mediante interceptación de emanaciones electromagnéticas.',
        'grupo': 'INDUSTRIALES',
        'frecuencia_base': 1,
        'facilidad_base': 2
    },

    # ========== GRUPO 3: ERRORES ==========
    {
        'codigo': 'E.1',
        'nombre': 'Errores de los usuarios',
        'descripcion': 'Errores humanos no intencionados durante el uso de sistemas o manejo de información.',
        'grupo': 'ERRORES',
        'frecuencia_base': 4,
        'facilidad_base': 5
    },
    {
        'codigo': 'E.2',
        'nombre': 'Errores del administrador',
        'descripcion': 'Errores durante la administración, configuración o mantenimiento de sistemas.',
        'grupo': 'ERRORES',
        'frecuencia_base': 3,
        'facilidad_base': 4
    },
    {
        'codigo': 'E.3',
        'nombre': 'Errores de monitorización (log)',
        'descripcion': 'Fallo en la captura o análisis de registros de auditoría.',
        'grupo': 'ERRORES',
        'frecuencia_base': 3,
        'facilidad_base': 4
    },
    {
        'codigo': 'E.4',
        'nombre': 'Errores de configuración',
        'descripcion': 'Configuración inadecuada de sistemas, equipos o aplicaciones.',
        'grupo': 'ERRORES',
        'frecuencia_base': 4,
        'facilidad_base': 4
    },
    {
        'codigo': 'E.7',
        'nombre': 'Deficiencias en la organización',
        'descripcion': 'Falta de procedimientos, procesos inadecuados o mala asignación de responsabilidades.',
        'grupo': 'ERRORES',
        'frecuencia_base': 3,
        'facilidad_base': 4
    },
    {
        'codigo': 'E.8',
        'nombre': 'Difusión de software dañino',
        'descripcion': 'Propagación no intencionada de malware por parte de usuarios o sistemas.',
        'grupo': 'ERRORES',
        'frecuencia_base': 4,
        'facilidad_base': 4
    },
    {
        'codigo': 'E.9',
        'nombre': 'Errores de [re-]encaminamiento',
        'descripcion': 'Fallo en el enrutamiento de comunicaciones que afecta disponibilidad o confidencialidad.',
        'grupo': 'ERRORES',
        'frecuencia_base': 2,
        'facilidad_base': 3
    },
    {
        'codigo': 'E.10',
        'nombre': 'Errores de secuencia',
        'descripcion': 'Alteración no intencionada del orden de mensajes o transacciones.',
        'grupo': 'ERRORES',
        'frecuencia_base': 2,
        'facilidad_base': 3
    },
    {
        'codigo': 'E.15',
        'nombre': 'Alteración accidental de la información',
        'descripcion': 'Modificación no intencionada de datos por error humano o de sistema.',
        'grupo': 'ERRORES',
        'frecuencia_base': 3,
        'facilidad_base': 4
    },
    {
        'codigo': 'E.18',
        'nombre': 'Destrucción de información',
        'descripcion': 'Pérdida o eliminación no intencionada de información.',
        'grupo': 'ERRORES',
        'frecuencia_base': 3,
        'facilidad_base': 4
    },
    {
        'codigo': 'E.19',
        'nombre': 'Fugas de información',
        'descripcion': 'Divulgación no intencionada de información confidencial.',
        'grupo': 'ERRORES',
        'frecuencia_base': 3,
        'facilidad_base': 4
    },
    {
        'codigo': 'E.20',
        'nombre': 'Vulnerabilidades de los programas (software)',
        'descripcion': 'Fallos de seguridad en el código de aplicaciones o sistemas operativos.',
        'grupo': 'ERRORES',
        'frecuencia_base': 4,
        'facilidad_base': 4
    },
    {
        'codigo': 'E.21',
        'nombre': 'Errores de mantenimiento / actualización de programas (software)',
        'descripcion': 'Problemas durante el proceso de mantenimiento o actualización de software.',
        'grupo': 'ERRORES',
        'frecuencia_base': 3,
        'facilidad_base': 4
    },
    {
        'codigo': 'E.23',
        'nombre': 'Errores de mantenimiento / actualización de equipos (hardware)',
        'descripcion': 'Problemas durante el mantenimiento o actualización de equipamiento físico.',
        'grupo': 'ERRORES',
        'frecuencia_base': 2,
        'facilidad_base': 3
    },
    {
        'codigo': 'E.24',
        'nombre': 'Caída del sistema por agotamiento de recursos',
        'descripcion': 'Fallo del sistema por consumo excesivo de CPU, memoria, disco o red.',
        'grupo': 'ERRORES',
        'frecuencia_base': 3,
        'facilidad_base': 4
    },
    {
        'codigo': 'E.25',
        'nombre': 'Pérdida de equipos',
        'descripcion': 'Extravío no intencionado de dispositivos portátiles o equipamiento.',
        'grupo': 'ERRORES',
        'frecuencia_base': 3,
        'facilidad_base': 4
    },
    {
        'codigo': 'E.28',
        'nombre': 'Indisponibilidad del personal',
        'descripcion': 'Ausencia de personal clave por enfermedad, accidente o abandono.',
        'grupo': 'ERRORES',
        'frecuencia_base': 3,
        'facilidad_base': 4
    },

    # ========== GRUPO 4: ATAQUES ==========
    {
        'codigo': 'A.3',
        'nombre': 'Manipulación de los registros de actividad (log)',
        'descripcion': 'Alteración o borrado intencionado de registros de auditoría para ocultar actividad maliciosa.',
        'grupo': 'ATAQUES',
        'frecuencia_base': 3,
        'facilidad_base': 3
    },
    {
        'codigo': 'A.4',
        'nombre': 'Manipulación de la configuración',
        'descripcion': 'Modificación no autorizada de configuraciones de sistemas para comprometer seguridad.',
        'grupo': 'ATAQUES',
        'frecuencia_base': 3,
        'facilidad_base': 3
    },
    {
        'codigo': 'A.5',
        'nombre': 'Suplantación de la identidad del usuario',
        'descripcion': 'Uso no autorizado de credenciales de usuario legítimo.',
        'grupo': 'ATAQUES',
        'frecuencia_base': 4,
        'facilidad_base': 4
    },
    {
        'codigo': 'A.6',
        'nombre': 'Abuso de privilegios de acceso',
        'descripcion': 'Uso inadecuado de privilegios legítimos para fines no autorizados.',
        'grupo': 'ATAQUES',
        'frecuencia_base': 3,
        'facilidad_base': 4
    },
    {
        'codigo': 'A.7',
        'nombre': 'Uso no previsto',
        'descripcion': 'Utilización de recursos de la organización para fines no autorizados.',
        'grupo': 'ATAQUES',
        'frecuencia_base': 4,
        'facilidad_base': 4
    },
    {
        'codigo': 'A.8',
        'nombre': 'Difusión de software dañino',
        'descripcion': 'Instalación intencionada de malware, virus, troyanos, ransomware, etc.',
        'grupo': 'ATAQUES',
        'frecuencia_base': 5,
        'facilidad_base': 4
    },
    {
        'codigo': 'A.9',
        'nombre': '[Re-]encaminamiento de mensajes',
        'descripcion': 'Modificación intencionada del enrutamiento para interceptar o redirigir comunicaciones.',
        'grupo': 'ATAQUES',
        'frecuencia_base': 2,
        'facilidad_base': 2
    },
    {
        'codigo': 'A.10',
        'nombre': 'Alteración de secuencia',
        'descripcion': 'Manipulación del orden de mensajes o transacciones para comprometer integridad.',
        'grupo': 'ATAQUES',
        'frecuencia_base': 2,
        'facilidad_base': 2
    },
    {
        'codigo': 'A.11',
        'nombre': 'Acceso no autorizado',
        'descripcion': 'Acceso ilegítimo a sistemas, aplicaciones o información sin autorización.',
        'grupo': 'ATAQUES',
        'frecuencia_base': 4,
        'facilidad_base': 4
    },
    {
        'codigo': 'A.12',
        'nombre': 'Análisis de tráfico',
        'descripcion': 'Análisis de patrones de comunicación para obtener información confidencial.',
        'grupo': 'ATAQUES',
        'frecuencia_base': 2,
        'facilidad_base': 3
    },
    {
        'codigo': 'A.13',
        'nombre': 'Repudio',
        'descripcion': 'Negación de participación en transacción o comunicación realizada.',
        'grupo': 'ATAQUES',
        'frecuencia_base': 2,
        'facilidad_base': 3
    },
    {
        'codigo': 'A.14',
        'nombre': 'Interceptación de información (escucha)',
        'descripcion': 'Captura no autorizada de comunicaciones o información en tránsito.',
        'grupo': 'ATAQUES',
        'frecuencia_base': 3,
        'facilidad_base': 3
    },
    {
        'codigo': 'A.15',
        'nombre': 'Modificación deliberada de la información',
        'descripcion': 'Alteración intencionada de datos para comprometer su integridad.',
        'grupo': 'ATAQUES',
        'frecuencia_base': 3,
        'facilidad_base': 3
    },
    {
        'codigo': 'A.18',
        'nombre': 'Destrucción de información',
        'descripcion': 'Eliminación intencionada de información para causar daño.',
        'grupo': 'ATAQUES',
        'frecuencia_base': 3,
        'facilidad_base': 3
    },
    {
        'codigo': 'A.19',
        'nombre': 'Divulgación de información',
        'descripcion': 'Revelación deliberada de información confidencial a terceros no autorizados.',
        'grupo': 'ATAQUES',
        'frecuencia_base': 3,
        'facilidad_base': 4
    },
    {
        'codigo': 'A.22',
        'nombre': 'Manipulación de programas',
        'descripcion': 'Modificación no autorizada de código fuente o ejecutables.',
        'grupo': 'ATAQUES',
        'frecuencia_base': 2,
        'facilidad_base': 2
    },
    {
        'codigo': 'A.23',
        'nombre': 'Manipulación de los equipos',
        'descripcion': 'Modificación física de equipamiento para comprometer su funcionamiento.',
        'grupo': 'ATAQUES',
        'frecuencia_base': 2,
        'facilidad_base': 2
    },
    {
        'codigo': 'A.24',
        'nombre': 'Denegación de servicio',
        'descripcion': 'Ataque que impide el uso legítimo de sistemas o servicios (DoS/DDoS).',
        'grupo': 'ATAQUES',
        'frecuencia_base': 4,
        'facilidad_base': 4
    },
    {
        'codigo': 'A.25',
        'nombre': 'Robo de equipos o documentos',
        'descripcion': 'Sustracción física de dispositivos o documentación.',
        'grupo': 'ATAQUES',
        'frecuencia_base': 3,
        'facilidad_base': 4
    },
    {
        'codigo': 'A.26',
        'nombre': 'Ataque destructivo',
        'descripcion': 'Daño físico intencionado a instalaciones, equipos o soportes.',
        'grupo': 'ATAQUES',
        'frecuencia_base': 1,
        'facilidad_base': 3
    },
    {
        'codigo': 'A.27',
        'nombre': 'Ocupación enemiga',
        'descripcion': 'Toma de control de instalaciones por parte de atacantes.',
        'grupo': 'ATAQUES',
        'frecuencia_base': 1,
        'facilidad_base': 2
    },
    {
        'codigo': 'A.28',
        'nombre': 'Indisponibilidad del personal',
        'descripcion': 'Ausencia intencionada o coaccionada de personal clave.',
        'grupo': 'ATAQUES',
        'frecuencia_base': 2,
        'facilidad_base': 3
    },
    {
        'codigo': 'A.29',
        'nombre': 'Extorsión',
        'descripcion': 'Chantaje o amenazas para obtener información, dinero o acciones específicas.',
        'grupo': 'ATAQUES',
        'frecuencia_base': 2,
        'facilidad_base': 3
    },
    {
        'codigo': 'A.30',
        'nombre': 'Ingeniería social (piratería)',
        'descripcion': 'Manipulación psicológica para obtener información o acceso no autorizado.',
        'grupo': 'ATAQUES',
        'frecuencia_base': 4,
        'facilidad_base': 5
    },
]


def seed_amenazas():
    """
    Precarga el catálogo de amenazas MAGERIT 3.2
    """
    print("\n" + "="*80)
    print("📋 PRECARGA DE AMENAZAS MAGERIT 3.2")
    print("="*80)

    # Verificar si ya existen amenazas
    count_existing = Amenaza.query.count()
    if count_existing > 0:
        print(f"\n⚠️  Ya existen {count_existing} amenazas en la base de datos.")
        respuesta = input("¿Desea eliminarlas y recargar el catálogo? (s/N): ")
        if respuesta.lower() != 's':
            print("❌ Operación cancelada.")
            return

        # Eliminar amenazas existentes
        Amenaza.query.delete()
        db.session.commit()
        print("🗑️  Amenazas existentes eliminadas.")

    # Insertar amenazas
    print(f"\n📥 Insertando {len(AMENAZAS_MAGERIT)} amenazas...")

    stats = {
        'DESASTRES_NATURALES': 0,
        'ORIGEN_INDUSTRIAL': 0,
        'ERRORES_NO_INTENCIONADOS': 0,
        'ATAQUES_INTENCIONADOS': 0
    }

    for amenaza_data in AMENAZAS_MAGERIT:
        amenaza = Amenaza(
            codigo=amenaza_data['codigo'],
            nombre=amenaza_data['nombre'],
            descripcion=amenaza_data['descripcion'],
            grupo=amenaza_data['grupo'],
            afecta_confidencialidad=True,  # Por defecto todas afectan todas las dimensiones
            afecta_integridad=True,
            afecta_disponibilidad=True
        )
        db.session.add(amenaza)
        stats[amenaza_data['grupo']] += 1

    try:
        db.session.commit()
        print("✅ Amenazas insertadas correctamente!")

        # Mostrar estadísticas
        print("\n📊 ESTADÍSTICAS DE CARGA:")
        print(f"   • Desastres Naturales: {stats['DESASTRES_NATURALES']} amenazas")
        print(f"   • Origen Industrial: {stats['ORIGEN_INDUSTRIAL']} amenazas")
        print(f"   • Errores No Intencionados: {stats['ERRORES_NO_INTENCIONADOS']} amenazas")
        print(f"   • Ataques Intencionados: {stats['ATAQUES_INTENCIONADOS']} amenazas")
        print(f"\n   TOTAL: {sum(stats.values())} amenazas")
        print("="*80 + "\n")

    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Error al insertar amenazas: {str(e)}")
        raise


if __name__ == '__main__':
    from application import create_app

    app = create_app()
    with app.app_context():
        seed_amenazas()
