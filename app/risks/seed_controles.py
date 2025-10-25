"""
Script de Precarga de Controles ISO/IEC 27002:2022
Catálogo de 93 controles organizados en 4 categorías
"""

from models import db
from app.risks.models import ControlISO27002


# Catálogo de controles ISO/IEC 27002:2022
# 93 controles organizados en 4 categorías principales
CONTROLES_ISO27002 = [
    # ========== CATEGORÍA 1: CONTROLES ORGANIZACIONALES (37 controles) ==========
    {'codigo': '5.1', 'nombre': 'Políticas de seguridad de la información', 'categoria': 'ORGANIZACIONALES', 'descripcion': 'Conjunto de políticas de seguridad definidas, aprobadas por la dirección, publicadas y comunicadas.'},
    {'codigo': '5.2', 'nombre': 'Roles y responsabilidades de seguridad de la información', 'categoria': 'ORGANIZACIONALES', 'descripcion': 'Roles y responsabilidades de seguridad de la información definidos y asignados.'},
    {'codigo': '5.3', 'nombre': 'Segregación de funciones', 'categoria': 'ORGANIZACIONALES', 'descripcion': 'Funciones conflictivas y áreas de responsabilidad segregadas.'},
    {'codigo': '5.4', 'nombre': 'Responsabilidades de la dirección', 'categoria': 'ORGANIZACIONALES', 'descripcion': 'La dirección requiere que todo el personal aplique la seguridad de la información.'},
    {'codigo': '5.5', 'nombre': 'Contacto con las autoridades', 'categoria': 'ORGANIZACIONALES', 'descripcion': 'Contactos apropiados con autoridades relevantes mantenidos.'},
    {'codigo': '5.6', 'nombre': 'Contacto con grupos de interés especial', 'categoria': 'ORGANIZACIONALES', 'descripcion': 'Contactos con grupos de seguridad y asociaciones profesionales mantenidos.'},
    {'codigo': '5.7', 'nombre': 'Inteligencia de amenazas', 'categoria': 'ORGANIZACIONALES', 'descripcion': 'Información sobre amenazas de seguridad recopilada y analizada.'},
    {'codigo': '5.8', 'nombre': 'Seguridad de la información en la gestión de proyectos', 'categoria': 'ORGANIZACIONALES', 'descripcion': 'Seguridad de la información integrada en la gestión de proyectos.'},
    {'codigo': '5.9', 'nombre': 'Inventario de activos de información', 'categoria': 'ORGANIZACIONALES', 'descripcion': 'Inventario de activos asociados con información e instalaciones de procesamiento desarrollado y mantenido.'},
    {'codigo': '5.10', 'nombre': 'Uso aceptable de la información y otros activos asociados', 'categoria': 'ORGANIZACIONALES', 'descripcion': 'Reglas de uso aceptable de información y activos identificadas, documentadas e implementadas.'},
    {'codigo': '5.11', 'nombre': 'Devolución de activos', 'categoria': 'ORGANIZACIONALES', 'descripcion': 'Personal y partes externas devuelven todos los activos de la organización en su posesión.'},
    {'codigo': '5.12', 'nombre': 'Clasificación de la información', 'categoria': 'ORGANIZACIONALES', 'descripcion': 'Información clasificada según necesidades de seguridad de la organización.'},
    {'codigo': '5.13', 'nombre': 'Etiquetado de la información', 'categoria': 'ORGANIZACIONALES', 'descripcion': 'Conjunto apropiado de etiquetas desarrollado e implementado según esquema de clasificación.'},
    {'codigo': '5.14', 'nombre': 'Transferencia de información', 'categoria': 'ORGANIZACIONALES', 'descripcion': 'Reglas de transferencia de información implementadas.'},
    {'codigo': '5.15', 'nombre': 'Control de acceso', 'categoria': 'ORGANIZACIONALES', 'descripcion': 'Reglas de control de acceso físico y lógico establecidas e implementadas.'},
    {'codigo': '5.16', 'nombre': 'Gestión de identidades', 'categoria': 'ORGANIZACIONALES', 'descripcion': 'Ciclo de vida completo de identidades gestionado.'},
    {'codigo': '5.17', 'nombre': 'Información de autenticación', 'categoria': 'ORGANIZACIONALES', 'descripcion': 'Asignación y gestión de información de autenticación controlada.'},
    {'codigo': '5.18', 'nombre': 'Derechos de acceso', 'categoria': 'ORGANIZACIONALES', 'descripcion': 'Derechos de acceso a información y otros activos asignados y gestionados.'},
    {'codigo': '5.19', 'nombre': 'Seguridad de la información en las relaciones con proveedores', 'categoria': 'ORGANIZACIONALES', 'descripcion': 'Procesos y procedimientos para gestionar seguridad en relaciones con proveedores.'},
    {'codigo': '5.20', 'nombre': 'Abordar la seguridad de la información en los acuerdos con proveedores', 'categoria': 'ORGANIZACIONALES', 'descripcion': 'Requisitos de seguridad relevantes establecidos y acordados con cada proveedor.'},
    {'codigo': '5.21', 'nombre': 'Gestión de la seguridad de la información en la cadena de suministro de TIC', 'categoria': 'ORGANIZACIONALES', 'descripcion': 'Procesos y procedimientos para gestionar riesgos de seguridad en cadena de suministro.'},
    {'codigo': '5.22', 'nombre': 'Supervisión, revisión y gestión del cambio de servicios de proveedores', 'categoria': 'ORGANIZACIONALES', 'descripcion': 'Servicios de proveedores supervisados, revisados y gestionados regularmente.'},
    {'codigo': '5.23', 'nombre': 'Seguridad de la información para el uso de servicios en la nube', 'categoria': 'ORGANIZACIONALES', 'descripcion': 'Procesos de adquisición, uso, gestión y salida de servicios en la nube establecidos.'},
    {'codigo': '5.24', 'nombre': 'Planificación y preparación de la gestión de incidentes de seguridad de la información', 'categoria': 'ORGANIZACIONALES', 'descripcion': 'Organización planifica y prepara gestión de incidentes de seguridad.'},
    {'codigo': '5.25', 'nombre': 'Evaluación y decisión sobre eventos de seguridad de la información', 'categoria': 'ORGANIZACIONALES', 'descripcion': 'Eventos de seguridad evaluados y decididos si clasificarlos como incidentes.'},
    {'codigo': '5.26', 'nombre': 'Respuesta a incidentes de seguridad de la información', 'categoria': 'ORGANIZACIONALES', 'descripcion': 'Respuesta a incidentes según procedimientos documentados.'},
    {'codigo': '5.27', 'nombre': 'Aprender de los incidentes de seguridad de la información', 'categoria': 'ORGANIZACIONALES', 'descripcion': 'Conocimiento de incidentes usado para fortalecer y mejorar controles.'},
    {'codigo': '5.28', 'nombre': 'Recopilación de evidencia', 'categoria': 'ORGANIZACIONALES', 'descripcion': 'Procedimientos para identificación, recopilación, adquisición y preservación de evidencia.'},
    {'codigo': '5.29', 'nombre': 'Seguridad de la información durante disrupciones', 'categoria': 'ORGANIZACIONALES', 'descripcion': 'Disponibilidad de seguridad de la información planificada y mantenida durante disrupciones.'},
    {'codigo': '5.30', 'nombre': 'Preparación de las TIC para la continuidad del negocio', 'categoria': 'ORGANIZACIONALES', 'descripcion': 'Preparación de TIC planificada, implementada, mantenida y probada.'},
    {'codigo': '5.31', 'nombre': 'Requisitos legales, estatutarios, reglamentarios y contractuales', 'categoria': 'ORGANIZACIONALES', 'descripcion': 'Requisitos legales, estatutarios, reglamentarios y contractuales identificados, documentados y mantenidos.'},
    {'codigo': '5.32', 'nombre': 'Derechos de propiedad intelectual', 'categoria': 'ORGANIZACIONALES', 'descripcion': 'Procedimientos implementados para proteger derechos de propiedad intelectual.'},
    {'codigo': '5.33', 'nombre': 'Protección de registros', 'categoria': 'ORGANIZACIONALES', 'descripcion': 'Registros protegidos contra pérdida, destrucción, falsificación y acceso no autorizado.'},
    {'codigo': '5.34', 'nombre': 'Privacidad y protección de información personal identificable', 'categoria': 'ORGANIZACIONALES', 'descripcion': 'Privacidad y protección de PII aseguradas según requisitos legales.'},
    {'codigo': '5.35', 'nombre': 'Revisión independiente de la seguridad de la información', 'categoria': 'ORGANIZACIONALES', 'descripcion': 'Enfoque de gestión de seguridad y su implementación revisado independientemente.'},
    {'codigo': '5.36', 'nombre': 'Cumplimiento de políticas, reglas y normas de seguridad de la información', 'categoria': 'ORGANIZACIONALES', 'descripcion': 'Cumplimiento de políticas, reglas y normas revisado regularmente.'},
    {'codigo': '5.37', 'nombre': 'Procedimientos operativos documentados', 'categoria': 'ORGANIZACIONALES', 'descripcion': 'Procedimientos operativos documentados y disponibles para el personal.'},

    # ========== CATEGORÍA 2: CONTROLES DE PERSONAS (8 controles) ==========
    {'codigo': '6.1', 'nombre': 'Selección', 'categoria': 'PERSONAS', 'descripcion': 'Verificación de antecedentes de candidatos realizada según leyes, regulaciones y ética.'},
    {'codigo': '6.2', 'nombre': 'Términos y condiciones de empleo', 'categoria': 'PERSONAS', 'descripcion': 'Acuerdos contractuales establecen responsabilidades de seguridad del empleado y organización.'},
    {'codigo': '6.3', 'nombre': 'Concienciación, educación y capacitación en seguridad de la información', 'categoria': 'PERSONAS', 'descripcion': 'Personal recibe concienciación, educación y capacitación apropiada.'},
    {'codigo': '6.4', 'nombre': 'Proceso disciplinario', 'categoria': 'PERSONAS', 'descripcion': 'Proceso disciplinario formal comunicado para empleados que violan seguridad.'},
    {'codigo': '6.5', 'nombre': 'Responsabilidades después de la terminación o cambio de empleo', 'categoria': 'PERSONAS', 'descripcion': 'Responsabilidades de seguridad que permanecen válidas después del cambio o terminación.'},
    {'codigo': '6.6', 'nombre': 'Acuerdos de confidencialidad o no divulgación', 'categoria': 'PERSONAS', 'descripcion': 'Acuerdos de confidencialidad o no divulgación reflejan necesidades de protección de información.'},
    {'codigo': '6.7', 'nombre': 'Trabajo remoto', 'categoria': 'PERSONAS', 'descripcion': 'Medidas de seguridad implementadas cuando el personal trabaja remotamente.'},
    {'codigo': '6.8', 'nombre': 'Informes de eventos de seguridad de la información', 'categoria': 'PERSONAS', 'descripcion': 'Personal informa eventos de seguridad observados o sospechados.'},

    # ========== CATEGORÍA 3: CONTROLES FÍSICOS (14 controles) ==========
    {'codigo': '7.1', 'nombre': 'Perímetros de seguridad física', 'categoria': 'FISICOS', 'descripcion': 'Perímetros de seguridad física definidos y usados para proteger áreas con información sensible.'},
    {'codigo': '7.2', 'nombre': 'Entrada física', 'categoria': 'FISICOS', 'descripcion': 'Áreas seguras protegidas por controles de entrada apropiados.'},
    {'codigo': '7.3', 'nombre': 'Seguridad de oficinas, despachos e instalaciones', 'categoria': 'FISICOS', 'descripcion': 'Seguridad física para oficinas, despachos e instalaciones diseñada e implementada.'},
    {'codigo': '7.4', 'nombre': 'Supervisión de la seguridad física', 'categoria': 'FISICOS', 'descripcion': 'Instalaciones supervisadas continuamente contra acceso físico no autorizado.'},
    {'codigo': '7.5', 'nombre': 'Protección contra amenazas físicas y ambientales', 'categoria': 'FISICOS', 'descripcion': 'Protección contra amenazas físicas y ambientales diseñada e implementada.'},
    {'codigo': '7.6', 'nombre': 'Trabajo en áreas seguras', 'categoria': 'FISICOS', 'descripcion': 'Medidas de seguridad para trabajar en áreas seguras diseñadas e implementadas.'},
    {'codigo': '7.7', 'nombre': 'Escritorio y pantalla limpios', 'categoria': 'FISICOS', 'descripcion': 'Reglas de escritorio y pantalla limpios para documentos y medios de almacenamiento definidas.'},
    {'codigo': '7.8', 'nombre': 'Ubicación y protección del equipamiento', 'categoria': 'FISICOS', 'descripcion': 'Equipamiento ubicado y protegido para reducir riesgos de amenazas ambientales.'},
    {'codigo': '7.9', 'nombre': 'Seguridad de los activos fuera de las instalaciones', 'categoria': 'FISICOS', 'descripcion': 'Activos fuera de instalaciones protegidos.'},
    {'codigo': '7.10', 'nombre': 'Medios de almacenamiento', 'categoria': 'FISICOS', 'descripcion': 'Medios de almacenamiento gestionados según esquema de clasificación.'},
    {'codigo': '7.11', 'nombre': 'Servicios de soporte', 'categoria': 'FISICOS', 'descripcion': 'Instalaciones de procesamiento de información protegidas contra fallos de servicios de soporte.'},
    {'codigo': '7.12', 'nombre': 'Seguridad del cableado', 'categoria': 'FISICOS', 'descripcion': 'Cables protegidos contra interceptación, interferencia o daño.'},
    {'codigo': '7.13', 'nombre': 'Mantenimiento de equipos', 'categoria': 'FISICOS', 'descripcion': 'Equipamiento mantenido para asegurar disponibilidad, integridad y confidencialidad.'},
    {'codigo': '7.14', 'nombre': 'Eliminación o reutilización segura del equipamiento', 'categoria': 'FISICOS', 'descripcion': 'Elementos de equipamiento eliminados o reutilizados de forma segura.'},

    # ========== CATEGORÍA 4: CONTROLES TECNOLÓGICOS (34 controles) ==========
    {'codigo': '8.1', 'nombre': 'Dispositivos de punto final de usuario', 'categoria': 'TECNOLOGICOS', 'descripcion': 'Información en dispositivos de punto final de usuario protegida.'},
    {'codigo': '8.2', 'nombre': 'Derechos de acceso privilegiados', 'categoria': 'TECNOLOGICOS', 'descripcion': 'Asignación y uso de derechos de acceso privilegiados restringido y gestionado.'},
    {'codigo': '8.3', 'nombre': 'Restricción de acceso a la información', 'categoria': 'TECNOLOGICOS', 'descripcion': 'Acceso a información y otros activos restringido según política de control de acceso.'},
    {'codigo': '8.4', 'nombre': 'Acceso al código fuente', 'categoria': 'TECNOLOGICOS', 'descripcion': 'Acceso de lectura y escritura a código fuente gestionado apropiadamente.'},
    {'codigo': '8.5', 'nombre': 'Autenticación segura', 'categoria': 'TECNOLOGICOS', 'descripcion': 'Tecnologías y procedimientos de autenticación segura implementados.'},
    {'codigo': '8.6', 'nombre': 'Gestión de capacidad', 'categoria': 'TECNOLOGICOS', 'descripcion': 'Uso de recursos supervisado y ajustado según requisitos de capacidad actual y proyectada.'},
    {'codigo': '8.7', 'nombre': 'Protección contra malware', 'categoria': 'TECNOLOGICOS', 'descripcion': 'Protección contra malware implementada y soportada por concienciación de usuario.'},
    {'codigo': '8.8', 'nombre': 'Gestión de vulnerabilidades técnicas', 'categoria': 'TECNOLOGICOS', 'descripcion': 'Información sobre vulnerabilidades técnicas evaluada y acción apropiada tomada.'},
    {'codigo': '8.9', 'nombre': 'Gestión de configuración', 'categoria': 'TECNOLOGICOS', 'descripcion': 'Configuraciones de hardware, software, servicios y redes establecidas y gestionadas.'},
    {'codigo': '8.10', 'nombre': 'Eliminación de información', 'categoria': 'TECNOLOGICOS', 'descripcion': 'Información en sistemas, dispositivos o medios eliminada cuando ya no es requerida.'},
    {'codigo': '8.11', 'nombre': 'Enmascaramiento de datos', 'categoria': 'TECNOLOGICOS', 'descripcion': 'Enmascaramiento de datos usado según política de control de acceso y requisitos de negocio.'},
    {'codigo': '8.12', 'nombre': 'Prevención de fuga de datos', 'categoria': 'TECNOLOGICOS', 'descripcion': 'Medidas de prevención de fuga de datos aplicadas a sistemas, redes y dispositivos.'},
    {'codigo': '8.13', 'nombre': 'Respaldo de información', 'categoria': 'TECNOLOGICOS', 'descripcion': 'Copias de respaldo de información, software y sistemas mantenidas y probadas regularmente.'},
    {'codigo': '8.14', 'nombre': 'Redundancia de instalaciones de procesamiento de información', 'categoria': 'TECNOLOGICOS', 'descripcion': 'Instalaciones de procesamiento implementadas con redundancia suficiente para cumplir requisitos.'},
    {'codigo': '8.15', 'nombre': 'Registro', 'categoria': 'TECNOLOGICOS', 'descripcion': 'Registros que capturan actividades, excepciones, fallos y eventos producidos, mantenidos y revisados.'},
    {'codigo': '8.16', 'nombre': 'Actividades de supervisión', 'categoria': 'TECNOLOGICOS', 'descripcion': 'Redes, sistemas y aplicaciones supervisados para comportamiento anómalo.'},
    {'codigo': '8.17', 'nombre': 'Sincronización de relojes', 'categoria': 'TECNOLOGICOS', 'descripcion': 'Relojes de sistemas sincronizados con fuentes de tiempo aprobadas.'},
    {'codigo': '8.18', 'nombre': 'Uso de programas de utilidad privilegiados', 'categoria': 'TECNOLOGICOS', 'descripcion': 'Uso de programas de utilidad que pueden anular controles restringido y controlado.'},
    {'codigo': '8.19', 'nombre': 'Instalación de software en sistemas operativos', 'categoria': 'TECNOLOGICOS', 'descripcion': 'Procedimientos e implementación de controles para instalación de software en sistemas.'},
    {'codigo': '8.20', 'nombre': 'Seguridad de redes', 'categoria': 'TECNOLOGICOS', 'descripcion': 'Redes, dispositivos y servicios de red gestionados y controlados para proteger información.'},
    {'codigo': '8.21', 'nombre': 'Seguridad de servicios de red', 'categoria': 'TECNOLOGICOS', 'descripcion': 'Mecanismos de seguridad, niveles de servicio y requisitos de servicios de red identificados.'},
    {'codigo': '8.22', 'nombre': 'Segregación de redes', 'categoria': 'TECNOLOGICOS', 'descripcion': 'Grupos de servicios, usuarios y sistemas segregados en redes.'},
    {'codigo': '8.23', 'nombre': 'Filtrado web', 'categoria': 'TECNOLOGICOS', 'descripcion': 'Acceso a sitios web externos gestionado para reducir exposición a contenido malicioso.'},
    {'codigo': '8.24', 'nombre': 'Uso de criptografía', 'categoria': 'TECNOLOGICOS', 'descripcion': 'Reglas de uso efectivo de criptografía definidas e implementadas.'},
    {'codigo': '8.25', 'nombre': 'Ciclo de vida de desarrollo seguro', 'categoria': 'TECNOLOGICOS', 'descripcion': 'Reglas de desarrollo seguro de software y sistemas establecidas y aplicadas.'},
    {'codigo': '8.26', 'nombre': 'Requisitos de seguridad de las aplicaciones', 'categoria': 'TECNOLOGICOS', 'descripcion': 'Requisitos de seguridad identificados, especificados y aprobados en desarrollo de aplicaciones.'},
    {'codigo': '8.27', 'nombre': 'Arquitectura del sistema seguro y principios de ingeniería', 'categoria': 'TECNOLOGICOS', 'descripcion': 'Principios de ingeniería de sistemas seguros establecidos, documentados y mantenidos.'},
    {'codigo': '8.28', 'nombre': 'Codificación segura', 'categoria': 'TECNOLOGICOS', 'descripcion': 'Principios de codificación segura aplicados al desarrollo de software.'},
    {'codigo': '8.29', 'nombre': 'Pruebas de seguridad en desarrollo y aceptación', 'categoria': 'TECNOLOGICOS', 'descripcion': 'Procesos de pruebas de seguridad definidos y ejecutados en ciclo de desarrollo.'},
    {'codigo': '8.30', 'nombre': 'Desarrollo externalizado', 'categoria': 'TECNOLOGICOS', 'descripcion': 'Organización supervisa, monitoriza y revisa actividades de desarrollo externalizado.'},
    {'codigo': '8.31', 'nombre': 'Separación de entornos de desarrollo, pruebas y producción', 'categoria': 'TECNOLOGICOS', 'descripcion': 'Entornos de desarrollo, pruebas y producción separados y asegurados.'},
    {'codigo': '8.32', 'nombre': 'Gestión de cambios', 'categoria': 'TECNOLOGICOS', 'descripcion': 'Cambios en instalaciones y sistemas de procesamiento sujetos a procedimientos de gestión de cambios.'},
    {'codigo': '8.33', 'nombre': 'Información de prueba', 'categoria': 'TECNOLOGICOS', 'descripcion': 'Datos de prueba seleccionados, protegidos y controlados apropiadamente.'},
    {'codigo': '8.34', 'nombre': 'Protección de sistemas de información durante pruebas de auditoría', 'categoria': 'TECNOLOGICOS', 'descripcion': 'Pruebas de auditoría en sistemas operativos planificadas y acordadas entre probador y gestión.'},
]


def seed_controles():
    """
    Precarga el catálogo de controles ISO/IEC 27002:2022
    """
    print("\n" + "="*80)
    print("📋 PRECARGA DE CONTROLES ISO/IEC 27002:2022")
    print("="*80)

    # Verificar si ya existen controles
    count_existing = ControlISO27002.query.count()
    if count_existing > 0:
        print(f"\n⚠️  Ya existen {count_existing} controles en la base de datos.")
        respuesta = input("¿Desea eliminarlos y recargar el catálogo? (s/N): ")
        if respuesta.lower() != 's':
            print("❌ Operación cancelada.")
            return

        # Eliminar controles existentes
        ControlISO27002.query.delete()
        db.session.commit()
        print("🗑️  Controles existentes eliminados.")

    # Insertar controles
    print(f"\n📥 Insertando {len(CONTROLES_ISO27002)} controles...")

    stats = {
        'ORGANIZACIONALES': 0,
        'PERSONAS': 0,
        'FISICOS': 0,
        'TECNOLOGICOS': 0
    }

    for control_data in CONTROLES_ISO27002:
        control = ControlISO27002(
            codigo=control_data['codigo'],
            nombre=control_data['nombre'],
            categoria=control_data['categoria'],
            tipo_control='PREVENTIVO',  # Por defecto preventivo, se puede personalizar después
            descripcion=control_data['descripcion']
        )
        db.session.add(control)
        stats[control_data['categoria']] += 1

    try:
        db.session.commit()
        print("✅ Controles insertados correctamente!")

        # Mostrar estadísticas
        print("\n📊 ESTADÍSTICAS DE CARGA:")
        print(f"   • Controles Organizacionales: {stats['ORGANIZACIONALES']} controles")
        print(f"   • Controles de Personas: {stats['PERSONAS']} controles")
        print(f"   • Controles Físicos: {stats['FISICOS']} controles")
        print(f"   • Controles Tecnológicos: {stats['TECNOLOGICOS']} controles")
        print(f"\n   TOTAL: {sum(stats.values())} controles")
        print("="*80 + "\n")

    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Error al insertar controles: {str(e)}")
        raise


if __name__ == '__main__':
    from application import create_app

    app = create_app()
    with app.app_context():
        seed_controles()
