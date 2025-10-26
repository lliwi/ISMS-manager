"""
Script de Precarga de Relaciones Control-Amenaza
Mapeo entre controles ISO 27002:2022 y amenazas MAGERIT 3.2
Basado en análisis de cobertura y mejores prácticas de seguridad
"""

from models import db
from app.risks.models import ControlAmenaza, Amenaza


# Mapeo de controles ISO 27002:2022 a amenazas MAGERIT 3.2
# Estructura: {
#     'control_codigo': [
#         ('codigo_amenaza', 'TIPO_CONTROL', efectividad),
#         ...
#     ]
# }

RELACIONES_CONTROL_AMENAZA = {
    # ========== CONTROLES ORGANIZACIONALES (A.5) ==========

    'A.5.1': [  # Políticas de seguridad de la información
        ('E.1', 'PREVENTIVO', 0.60),  # Errores de usuarios
        ('E.2', 'PREVENTIVO', 0.70),  # Errores del administrador
        ('A.7', 'PREVENTIVO', 0.50),  # Uso no previsto
    ],

    'A.5.2': [  # Roles y responsabilidades
        ('E.2', 'PREVENTIVO', 0.65),  # Errores del administrador
        ('A.6', 'PREVENTIVO', 0.60),  # Abuso de privilegios
        ('E.8', 'PREVENTIVO', 0.55),  # Errores de configuración
    ],

    'A.5.7': [  # Inteligencia de amenazas
        ('A.8', 'DETECTIVE', 0.70),  # Difusión de software dañino
        ('A.11', 'DETECTIVE', 0.65),  # Acceso no autorizado
        ('A.30', 'PREVENTIVO', 0.60),  # Ingeniería social
    ],

    'A.5.8': [  # Seguridad de la información en la gestión de proyectos
        ('E.8', 'PREVENTIVO', 0.60),  # Errores de configuración
        ('E.23', 'PREVENTIVO', 0.55),  # Errores de mantenimiento
    ],

    'A.5.9': [  # Inventario de información y otros activos
        ('A.25', 'DETECTIVE', 0.50),  # Robo
        ('E.19', 'PREVENTIVO', 0.45),  # Fugas de información
    ],

    'A.5.10': [  # Uso aceptable de la información
        ('E.1', 'PREVENTIVO', 0.65),  # Errores de usuarios
        ('A.7', 'PREVENTIVO', 0.70),  # Uso no previsto
        ('E.19', 'PREVENTIVO', 0.55),  # Fugas de información
    ],

    'A.5.12': [  # Clasificación de la información
        ('A.19', 'PREVENTIVO', 0.60),  # Divulgación de información
        ('E.19', 'PREVENTIVO', 0.65),  # Fugas de información
    ],

    'A.5.13': [  # Etiquetado de la información
        ('A.19', 'PREVENTIVO', 0.55),  # Divulgación de información
        ('E.19', 'PREVENTIVO', 0.60),  # Fugas de información
    ],

    'A.5.14': [  # Transferencia de información
        ('A.14', 'PREVENTIVO', 0.70),  # Interceptación de información
        ('A.19', 'PREVENTIVO', 0.65),  # Divulgación de información
        ('E.19', 'PREVENTIVO', 0.60),  # Fugas de información
        ('A.12', 'PREVENTIVO', 0.55),  # Análisis de tráfico
    ],

    'A.5.15': [  # Control de acceso
        ('A.11', 'PREVENTIVO', 0.80),  # Acceso no autorizado
        ('A.6', 'PREVENTIVO', 0.75),  # Abuso de privilegios
        ('A.5', 'PREVENTIVO', 0.70),  # Suplantación de identidad
    ],

    'A.5.16': [  # Gestión de identidades
        ('A.5', 'PREVENTIVO', 0.75),  # Suplantación de identidad
        ('A.11', 'PREVENTIVO', 0.70),  # Acceso no autorizado
    ],

    'A.5.17': [  # Información de autenticación
        ('A.5', 'PREVENTIVO', 0.80),  # Suplantación de identidad
        ('A.11', 'PREVENTIVO', 0.75),  # Acceso no autorizado
        ('A.30', 'PREVENTIVO', 0.65),  # Ingeniería social
    ],

    'A.5.18': [  # Derechos de acceso
        ('A.6', 'PREVENTIVO', 0.80),  # Abuso de privilegios
        ('A.11', 'PREVENTIVO', 0.75),  # Acceso no autorizado
        ('E.2', 'PREVENTIVO', 0.60),  # Errores del administrador
    ],

    'A.5.23': [  # Seguridad en servicios cloud
        ('A.11', 'PREVENTIVO', 0.60),  # Acceso no autorizado
        ('A.19', 'PREVENTIVO', 0.55),  # Divulgación de información
        ('I.8', 'REACTIVO', 0.50),  # Fallo de comunicaciones
    ],

    'A.5.24': [  # Planificación gestión de incidentes
        ('A.24', 'REACTIVO', 0.60),  # Denegación de servicio
        ('A.8', 'REACTIVO', 0.65),  # Software dañino
        ('A.26', 'REACTIVO', 0.70),  # Ataque destructivo
    ],

    'A.5.25': [  # Evaluación de eventos de seguridad
        ('A.11', 'DETECTIVE', 0.70),  # Acceso no autorizado
        ('A.8', 'DETECTIVE', 0.75),  # Software dañino
        ('A.24', 'DETECTIVE', 0.65),  # Denegación de servicio
    ],

    'A.5.26': [  # Respuesta a incidentes
        ('A.8', 'REACTIVO', 0.70),  # Software dañino
        ('A.24', 'REACTIVO', 0.65),  # Denegación de servicio
        ('A.26', 'REACTIVO', 0.75),  # Ataque destructivo
    ],

    'A.5.27': [  # Aprender de incidentes
        ('A.8', 'REACTIVO', 0.50),  # Software dañino
        ('E.1', 'PREVENTIVO', 0.55),  # Errores de usuarios
        ('E.2', 'PREVENTIVO', 0.55),  # Errores del administrador
    ],

    'A.5.28': [  # Recopilación de evidencias
        ('A.3', 'DETECTIVE', 0.75),  # Manipulación de logs
        ('A.13', 'DETECTIVE', 0.70),  # Repudio
    ],

    'A.5.30': [  # Preparación para la continuidad
        ('N.1', 'REACTIVO', 0.70),  # Fuego
        ('N.2', 'REACTIVO', 0.70),  # Daños por agua
        ('I.6', 'REACTIVO', 0.75),  # Corte suministro eléctrico
        ('A.24', 'REACTIVO', 0.65),  # Denegación de servicio
    ],

    # ========== CONTROLES DE PERSONAS (A.6) ==========

    'A.6.1': [  # Selección
        ('A.28', 'PREVENTIVO', 0.50),  # Indisponibilidad del personal
        ('A.30', 'PREVENTIVO', 0.45),  # Ingeniería social
    ],

    'A.6.2': [  # Términos y condiciones de empleo
        ('E.1', 'PREVENTIVO', 0.60),  # Errores de usuarios
        ('A.7', 'PREVENTIVO', 0.65),  # Uso no previsto
        ('E.19', 'PREVENTIVO', 0.55),  # Fugas de información
    ],

    'A.6.3': [  # Concienciación, educación y formación
        ('E.1', 'PREVENTIVO', 0.75),  # Errores de usuarios
        ('A.30', 'PREVENTIVO', 0.80),  # Ingeniería social
        ('E.19', 'PREVENTIVO', 0.65),  # Fugas de información
        ('A.7', 'PREVENTIVO', 0.60),  # Uso no previsto
    ],

    'A.6.4': [  # Proceso disciplinario
        ('A.6', 'DISUASORIO', 0.55),  # Abuso de privilegios
        ('A.7', 'DISUASORIO', 0.50),  # Uso no previsto
    ],

    'A.6.5': [  # Responsabilidades después del cese
        ('A.19', 'PREVENTIVO', 0.60),  # Divulgación de información
        ('E.19', 'PREVENTIVO', 0.65),  # Fugas de información
    ],

    'A.6.6': [  # Acuerdos de confidencialidad
        ('A.19', 'PREVENTIVO', 0.65),  # Divulgación de información
        ('E.19', 'PREVENTIVO', 0.70),  # Fugas de información
    ],

    'A.6.7': [  # Trabajo remoto
        ('A.11', 'PREVENTIVO', 0.60),  # Acceso no autorizado
        ('A.14', 'PREVENTIVO', 0.55),  # Interceptación
        ('E.1', 'PREVENTIVO', 0.50),  # Errores de usuarios
    ],

    'A.6.8': [  # Reporte de eventos
        ('A.8', 'DETECTIVE', 0.65),  # Software dañino
        ('A.11', 'DETECTIVE', 0.60),  # Acceso no autorizado
        ('E.23', 'DETECTIVE', 0.55),  # Errores de mantenimiento
    ],

    # ========== CONTROLES FÍSICOS (A.7) ==========

    'A.7.1': [  # Perímetros de seguridad física
        ('A.25', 'PREVENTIVO', 0.75),  # Robo
        ('A.27', 'PREVENTIVO', 0.70),  # Ocupación enemiga
        ('A.23', 'PREVENTIVO', 0.65),  # Manipulación de equipos
    ],

    'A.7.2': [  # Entrada física
        ('A.25', 'PREVENTIVO', 0.80),  # Robo
        ('A.11', 'PREVENTIVO', 0.70),  # Acceso no autorizado
        ('A.23', 'PREVENTIVO', 0.65),  # Manipulación de equipos
    ],

    'A.7.3': [  # Seguridad de oficinas, despachos e instalaciones
        ('A.25', 'PREVENTIVO', 0.70),  # Robo
        ('E.19', 'PREVENTIVO', 0.60),  # Fugas de información
    ],

    'A.7.4': [  # Monitorización de seguridad física
        ('A.25', 'DETECTIVE', 0.75),  # Robo
        ('A.23', 'DETECTIVE', 0.70),  # Manipulación de equipos
        ('A.27', 'DETECTIVE', 0.65),  # Ocupación enemiga
    ],

    'A.7.5': [  # Protección contra amenazas físicas y ambientales
        ('N.1', 'PREVENTIVO', 0.80),  # Fuego
        ('N.2', 'PREVENTIVO', 0.80),  # Daños por agua
        ('I.1', 'PREVENTIVO', 0.75),  # Fuego industrial
        ('I.2', 'PREVENTIVO', 0.75),  # Daños por agua industrial
        ('I.7', 'PREVENTIVO', 0.70),  # Condiciones inadecuadas temp/humedad
    ],

    'A.7.6': [  # Trabajo en áreas seguras
        ('E.19', 'PREVENTIVO', 0.65),  # Fugas de información
        ('A.25', 'PREVENTIVO', 0.60),  # Robo
    ],

    'A.7.7': [  # Escritorio y pantalla limpios
        ('E.19', 'PREVENTIVO', 0.70),  # Fugas de información
        ('A.19', 'PREVENTIVO', 0.65),  # Divulgación de información
    ],

    'A.7.8': [  # Ubicación y protección de equipos
        ('A.25', 'PREVENTIVO', 0.65),  # Robo
        ('N.1', 'PREVENTIVO', 0.60),  # Fuego
        ('N.2', 'PREVENTIVO', 0.60),  # Daños por agua
    ],

    'A.7.9': [  # Seguridad de activos fuera de las instalaciones
        ('A.25', 'PREVENTIVO', 0.70),  # Robo
        ('E.19', 'PREVENTIVO', 0.60),  # Fugas de información
    ],

    'A.7.10': [  # Medios de almacenamiento
        ('A.25', 'PREVENTIVO', 0.65),  # Robo
        ('E.18', 'REACTIVO', 0.60),  # Destrucción de información
        ('A.19', 'PREVENTIVO', 0.70),  # Divulgación de información
    ],

    'A.7.11': [  # Servicios de suministro
        ('I.6', 'REACTIVO', 0.80),  # Corte suministro eléctrico
        ('I.8', 'REACTIVO', 0.75),  # Fallo de comunicaciones
    ],

    'A.7.12': [  # Seguridad del cableado
        ('A.14', 'PREVENTIVO', 0.70),  # Interceptación
        ('A.23', 'PREVENTIVO', 0.65),  # Manipulación de equipos
        ('I.4', 'PREVENTIVO', 0.60),  # Contaminación electromagnética
    ],

    'A.7.13': [  # Mantenimiento de equipos
        ('I.5', 'PREVENTIVO', 0.75),  # Avería física o lógica
        ('E.23', 'PREVENTIVO', 0.70),  # Errores de mantenimiento
    ],

    'A.7.14': [  # Eliminación o reutilización segura de equipos
        ('A.19', 'PREVENTIVO', 0.80),  # Divulgación de información
        ('E.19', 'PREVENTIVO', 0.75),  # Fugas de información
    ],

    # ========== CONTROLES TECNOLÓGICOS (A.8) ==========

    'A.8.1': [  # Dispositivos de punto final de usuario
        ('A.8', 'PREVENTIVO', 0.75),  # Software dañino
        ('A.11', 'PREVENTIVO', 0.70),  # Acceso no autorizado
        ('E.1', 'PREVENTIVO', 0.60),  # Errores de usuarios
    ],

    'A.8.2': [  # Derechos de acceso privilegiados
        ('A.6', 'PREVENTIVO', 0.85),  # Abuso de privilegios
        ('A.4', 'PREVENTIVO', 0.75),  # Manipulación de configuración
        ('E.2', 'PREVENTIVO', 0.70),  # Errores del administrador
    ],

    'A.8.3': [  # Restricción de acceso a la información
        ('A.11', 'PREVENTIVO', 0.80),  # Acceso no autorizado
        ('A.19', 'PREVENTIVO', 0.75),  # Divulgación de información
    ],

    'A.8.4': [  # Acceso al código fuente
        ('A.22', 'PREVENTIVO', 0.75),  # Manipulación de programas
        ('A.11', 'PREVENTIVO', 0.70),  # Acceso no autorizado
    ],

    'A.8.5': [  # Autenticación segura
        ('A.5', 'PREVENTIVO', 0.85),  # Suplantación de identidad
        ('A.11', 'PREVENTIVO', 0.80),  # Acceso no autorizado
        ('A.30', 'PREVENTIVO', 0.70),  # Ingeniería social
    ],

    'A.8.6': [  # Gestión de capacidad
        ('A.24', 'PREVENTIVO', 0.70),  # Denegación de servicio
        ('I.5', 'PREVENTIVO', 0.60),  # Avería
    ],

    'A.8.7': [  # Protección contra malware
        ('A.8', 'PREVENTIVO', 0.90),  # Software dañino
        ('A.22', 'PREVENTIVO', 0.75),  # Manipulación de programas
    ],

    'A.8.8': [  # Gestión de vulnerabilidades técnicas
        ('A.11', 'PREVENTIVO', 0.80),  # Acceso no autorizado
        ('A.8', 'PREVENTIVO', 0.75),  # Software dañino
        ('A.24', 'PREVENTIVO', 0.70),  # Denegación de servicio
    ],

    'A.8.9': [  # Gestión de configuración
        ('E.8', 'PREVENTIVO', 0.80),  # Errores de configuración
        ('A.4', 'PREVENTIVO', 0.75),  # Manipulación de configuración
        ('E.2', 'PREVENTIVO', 0.65),  # Errores del administrador
    ],

    'A.8.10': [  # Eliminación de información
        ('E.18', 'PREVENTIVO', 0.70),  # Destrucción de información
        ('A.18', 'REACTIVO', 0.65),  # Destrucción deliberada
    ],

    'A.8.11': [  # Enmascaramiento de datos
        ('A.19', 'PREVENTIVO', 0.75),  # Divulgación de información
        ('E.19', 'PREVENTIVO', 0.70),  # Fugas de información
    ],

    'A.8.12': [  # Prevención de fuga de datos
        ('A.19', 'PREVENTIVO', 0.80),  # Divulgación de información
        ('E.19', 'PREVENTIVO', 0.85),  # Fugas de información
    ],

    'A.8.13': [  # Respaldo de información
        ('E.18', 'REACTIVO', 0.85),  # Destrucción de información
        ('A.18', 'REACTIVO', 0.80),  # Destrucción deliberada
        ('I.5', 'REACTIVO', 0.75),  # Avería
        ('N.1', 'REACTIVO', 0.70),  # Fuego
    ],

    'A.8.14': [  # Redundancia de instalaciones de procesamiento
        ('I.5', 'REACTIVO', 0.80),  # Avería
        ('I.6', 'REACTIVO', 0.75),  # Corte suministro
        ('A.24', 'REACTIVO', 0.70),  # Denegación de servicio
    ],

    'A.8.15': [  # Registro de actividades
        ('A.3', 'DETECTIVE', 0.80),  # Manipulación de logs
        ('A.11', 'DETECTIVE', 0.75),  # Acceso no autorizado
        ('A.13', 'DETECTIVE', 0.70),  # Repudio
    ],

    'A.8.16': [  # Actividades de monitorización
        ('A.11', 'DETECTIVE', 0.80),  # Acceso no autorizado
        ('A.8', 'DETECTIVE', 0.75),  # Software dañino
        ('A.24', 'DETECTIVE', 0.70),  # Denegación de servicio
        ('A.6', 'DETECTIVE', 0.65),  # Abuso de privilegios
    ],

    'A.8.17': [  # Sincronización de relojes
        ('A.10', 'PREVENTIVO', 0.70),  # Alteración de secuencia
        ('A.3', 'DETECTIVE', 0.65),  # Manipulación de logs
    ],

    'A.8.18': [  # Uso de programas de utilidad privilegiados
        ('A.6', 'PREVENTIVO', 0.75),  # Abuso de privilegios
        ('A.4', 'PREVENTIVO', 0.70),  # Manipulación de configuración
        ('E.2', 'PREVENTIVO', 0.65),  # Errores del administrador
    ],

    'A.8.19': [  # Instalación de software en sistemas operativos
        ('A.22', 'PREVENTIVO', 0.80),  # Manipulación de programas
        ('A.8', 'PREVENTIVO', 0.75),  # Software dañino
        ('E.20', 'PREVENTIVO', 0.60),  # Vulnerabilidades de software
    ],

    'A.8.20': [  # Seguridad de redes
        ('A.14', 'PREVENTIVO', 0.75),  # Interceptación
        ('A.11', 'PREVENTIVO', 0.70),  # Acceso no autorizado
        ('A.24', 'PREVENTIVO', 0.65),  # Denegación de servicio
    ],

    'A.8.21': [  # Seguridad de servicios de red
        ('A.14', 'PREVENTIVO', 0.70),  # Interceptación
        ('A.24', 'PREVENTIVO', 0.65),  # Denegación de servicio
        ('I.8', 'REACTIVO', 0.60),  # Fallo de comunicaciones
    ],

    'A.8.22': [  # Segregación de redes
        ('A.14', 'PREVENTIVO', 0.75),  # Interceptación
        ('A.11', 'PREVENTIVO', 0.70),  # Acceso no autorizado
        ('A.24', 'PREVENTIVO', 0.65),  # Denegación de servicio
    ],

    'A.8.23': [  # Filtrado web
        ('A.8', 'PREVENTIVO', 0.70),  # Software dañino
        ('A.30', 'PREVENTIVO', 0.65),  # Ingeniería social
        ('E.7', 'PREVENTIVO', 0.60),  # Deficiencia en organización
    ],

    'A.8.24': [  # Uso de criptografía
        ('A.14', 'PREVENTIVO', 0.90),  # Interceptación
        ('A.19', 'PREVENTIVO', 0.85),  # Divulgación de información
        ('A.15', 'PREVENTIVO', 0.80),  # Modificación deliberada
        ('A.12', 'PREVENTIVO', 0.75),  # Análisis de tráfico
    ],

    'A.8.25': [  # Ciclo de vida de desarrollo seguro
        ('A.22', 'PREVENTIVO', 0.80),  # Manipulación de programas
        ('E.20', 'PREVENTIVO', 0.75),  # Vulnerabilidades de software
        ('E.21', 'PREVENTIVO', 0.70),  # Errores de mantenimiento
    ],

    'A.8.26': [  # Requisitos de seguridad de aplicaciones
        ('E.20', 'PREVENTIVO', 0.75),  # Vulnerabilidades de software
        ('A.11', 'PREVENTIVO', 0.70),  # Acceso no autorizado
    ],

    'A.8.27': [  # Arquitectura de sistemas seguros y principios de ingeniería
        ('E.20', 'PREVENTIVO', 0.80),  # Vulnerabilidades de software
        ('A.11', 'PREVENTIVO', 0.75),  # Acceso no autorizado
        ('E.8', 'PREVENTIVO', 0.70),  # Errores de configuración
    ],

    'A.8.28': [  # Codificación segura
        ('E.20', 'PREVENTIVO', 0.85),  # Vulnerabilidades de software
        ('A.22', 'PREVENTIVO', 0.75),  # Manipulación de programas
    ],

    'A.8.29': [  # Pruebas de seguridad en desarrollo y aceptación
        ('E.20', 'DETECTIVE', 0.80),  # Vulnerabilidades de software
        ('A.22', 'DETECTIVE', 0.70),  # Manipulación de programas
    ],

    'A.8.30': [  # Desarrollo externalizado
        ('A.22', 'PREVENTIVO', 0.65),  # Manipulación de programas
        ('E.20', 'PREVENTIVO', 0.60),  # Vulnerabilidades de software
    ],

    'A.8.31': [  # Separación de entornos de desarrollo, prueba y producción
        ('E.23', 'PREVENTIVO', 0.75),  # Errores de mantenimiento
        ('E.8', 'PREVENTIVO', 0.70),  # Errores de configuración
        ('A.4', 'PREVENTIVO', 0.65),  # Manipulación de configuración
    ],

    'A.8.32': [  # Gestión de cambios
        ('E.8', 'PREVENTIVO', 0.80),  # Errores de configuración
        ('E.21', 'PREVENTIVO', 0.75),  # Errores de mantenimiento
        ('A.4', 'PREVENTIVO', 0.70),  # Manipulación de configuración
    ],

    'A.8.33': [  # Información de prueba
        ('A.19', 'PREVENTIVO', 0.75),  # Divulgación de información
        ('E.19', 'PREVENTIVO', 0.70),  # Fugas de información
    ],

    'A.8.34': [  # Protección de sistemas de información durante pruebas de auditoría
        ('E.23', 'PREVENTIVO', 0.70),  # Errores de mantenimiento
        ('A.24', 'PREVENTIVO', 0.65),  # Denegación de servicio
    ],
}


def seed_control_amenaza(force_reload=False, interactive=True):
    """
    Precarga las relaciones control-amenaza basadas en mejores prácticas

    Args:
        force_reload: Si True, elimina y recarga las relaciones existentes
        interactive: Si False, no solicita confirmación (para inicialización automática)
    """
    if interactive:
        print("\n" + "="*80)
        print("📋 PRECARGA DE RELACIONES CONTROL-AMENAZA")
        print("="*80)

    # Verificar si ya existen relaciones
    count_existing = ControlAmenaza.query.count()
    if count_existing > 0:
        if interactive:
            print(f"\n⚠️  Ya existen {count_existing} relaciones en la base de datos.")
            respuesta = input("¿Desea eliminarlas y recargar el catálogo? (s/N): ")
            if respuesta.lower() != 's':
                print("❌ Operación cancelada.")
                return
        elif not force_reload:
            # En modo no interactivo, si ya existen relaciones, no hacer nada
            return

        # Eliminar relaciones existentes
        ControlAmenaza.query.delete()
        db.session.commit()
        if interactive:
            print("🗑️  Relaciones existentes eliminadas.")

    # Contador de relaciones creadas
    total_creadas = 0
    errores = []

    if interactive:
        print(f"\n📥 Insertando relaciones control-amenaza...")

    for control_codigo, amenazas_list in RELACIONES_CONTROL_AMENAZA.items():
        for amenaza_codigo, tipo_control, efectividad in amenazas_list:
            try:
                # Buscar la amenaza por código
                amenaza = Amenaza.query.filter_by(codigo=amenaza_codigo).first()

                if not amenaza:
                    errores.append(f"Amenaza {amenaza_codigo} no encontrada")
                    continue

                # Verificar que no exista ya la relación
                existing = ControlAmenaza.query.filter_by(
                    control_codigo=control_codigo,
                    amenaza_id=amenaza.id
                ).first()

                if existing:
                    continue  # Ya existe, saltar

                # Crear la relación
                relacion = ControlAmenaza(
                    control_codigo=control_codigo,
                    amenaza_id=amenaza.id,
                    tipo_control=tipo_control,
                    efectividad=efectividad
                )

                db.session.add(relacion)
                total_creadas += 1

            except Exception as e:
                errores.append(f"Error con {control_codigo}-{amenaza_codigo}: {str(e)}")

    try:
        db.session.commit()
        if interactive:
            print(f"✅ {total_creadas} relaciones control-amenaza creadas correctamente!")

            if errores:
                print(f"\n⚠️  Se encontraron {len(errores)} errores:")
                for error in errores[:10]:  # Mostrar solo los primeros 10
                    print(f"   • {error}")

            print("\n📊 ESTADÍSTICAS:")
            from sqlalchemy import func
            stats = db.session.query(
                ControlAmenaza.tipo_control,
                func.count(ControlAmenaza.id).label('count')
            ).group_by(ControlAmenaza.tipo_control).all()

            for tipo, count in stats:
                print(f"   • {tipo}: {count} relaciones")

            print(f"\n   TOTAL: {total_creadas} relaciones")
            print("="*80 + "\n")

    except Exception as e:
        db.session.rollback()
        if interactive:
            print(f"\n❌ Error al insertar relaciones: {str(e)}")
        raise


if __name__ == '__main__':
    from application import create_app

    app = create_app()
    with app.app_context():
        seed_control_amenaza()
