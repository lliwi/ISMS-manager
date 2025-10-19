#!/usr/bin/env python3
"""
Script de inicialización del módulo de Gestión de Tareas
Se ejecuta automáticamente en nuevas instalaciones o cuando no existen plantillas de tareas

Uso:
    python init_tasks_module.py
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from application import app
from models import db, Role, User
from app.models.task import TaskTemplate, TaskFrequency, TaskPriority, TaskCategory


def check_tables_exist():
    """Verifica que las tablas de tareas existan"""
    with app.app_context():
        try:
            # Intentar consultar las tablas
            TaskTemplate.query.first()
            return True
        except Exception as e:
            print(f"❌ Error: Las tablas de tareas no existen.")
            print(f"   Por favor, ejecuta primero: flask db upgrade")
            print(f"   Error: {str(e)}")
            return False


def init_task_templates():
    """Inicializa las plantillas de tareas ISO 27001 si no existen"""

    with app.app_context():
        # Verificar si ya existen plantillas
        existing_count = TaskTemplate.query.count()
        if existing_count > 0:
            print(f"ℹ️  Ya existen {existing_count} plantillas de tareas.")
            print("   No se crearán nuevas plantillas.")
            return

        print("🚀 Iniciando creación de plantillas de tareas ISO 27001...")

        # Obtener roles
        role_ciso = Role.query.filter_by(name='ciso').first()
        role_admin = Role.query.filter_by(name='admin').first()
        role_auditor = Role.query.filter_by(name='auditor').first()

        # Plantillas de tareas
        templates_data = [
            # 1. REVISIÓN DE CONTROLES (9.1)
            {
                'title': 'Revisión Trimestral de Controles de Seguridad',
                'description': '''Realizar revisión trimestral de la eficacia de los controles de seguridad implementados.

Objetivos:
- Verificar que los controles están operando correctamente
- Identificar desviaciones o debilidades
- Proponer mejoras cuando sea necesario
- Documentar hallazgos y recomendaciones

Esta tarea cumple con el requisito 9.1 de ISO 27001 sobre seguimiento, medición, análisis y evaluación.''',
                'category': TaskCategory.REVISION_CONTROLES,
                'frequency': TaskFrequency.TRIMESTRAL,
                'priority': TaskPriority.ALTA,
                'iso_control': '9.1',
                'estimated_hours': 8.0,
                'default_role_id': role_ciso.id if role_ciso else None,
                'notify_days_before': 7,
                'checklist_template': [
                    {'description': 'Seleccionar muestra de controles a revisar', 'completed': False},
                    {'description': 'Verificar implementación de cada control', 'completed': False},
                    {'description': 'Evaluar eficacia mediante pruebas', 'completed': False},
                    {'description': 'Documentar hallazgos y no conformidades', 'completed': False},
                    {'description': 'Proponer acciones correctivas/mejoras', 'completed': False},
                    {'description': 'Generar informe de revisión', 'completed': False},
                ],
                'requires_evidence': True,
                'requires_approval': False,
            },

            # 2. AUDITORÍA INTERNA (9.2)
            {
                'title': 'Auditoría Interna del SGSI - Semestral',
                'description': '''Realizar auditoría interna completa del Sistema de Gestión de Seguridad de la Información.

Alcance:
- Todos los procesos del SGSI
- Cumplimiento de requisitos ISO 27001
- Eficacia de controles implementados
- Revisión de no conformidades anteriores

Control ISO 27001: 9.2 Auditoría interna''',
                'category': TaskCategory.AUDITORIA_INTERNA,
                'frequency': TaskFrequency.SEMESTRAL,
                'priority': TaskPriority.CRITICA,
                'iso_control': '9.2',
                'estimated_hours': 24.0,
                'default_role_id': role_auditor.id if role_auditor else None,
                'notify_days_before': 14,
                'checklist_template': [
                    {'description': 'Planificar alcance y programa de auditoría', 'completed': False},
                    {'description': 'Notificar a las áreas a auditar', 'completed': False},
                    {'description': 'Revisar documentación del SGSI', 'completed': False},
                    {'description': 'Realizar entrevistas y pruebas', 'completed': False},
                    {'description': 'Documentar hallazgos y no conformidades', 'completed': False},
                    {'description': 'Reunión de cierre con dirección', 'completed': False},
                    {'description': 'Emitir informe de auditoría', 'completed': False},
                    {'description': 'Hacer seguimiento de acciones correctivas', 'completed': False},
                ],
                'requires_evidence': True,
                'requires_approval': True,
            },

            # 3. EVALUACIÓN DE RIESGOS (8.2)
            {
                'title': 'Evaluación Anual de Riesgos de Seguridad',
                'description': '''Evaluación completa de riesgos de seguridad de la información.

Actividades:
- Identificación de nuevos riesgos
- Reevaluación de riesgos existentes
- Análisis de cambios en el contexto
- Actualización del registro de riesgos
- Revisión de tratamiento de riesgos

Control ISO 27001: 8.2 Evaluación de riesgos de seguridad de la información''',
                'category': TaskCategory.EVALUACION_RIESGOS,
                'frequency': TaskFrequency.ANUAL,
                'priority': TaskPriority.CRITICA,
                'iso_control': '8.2',
                'estimated_hours': 40.0,
                'default_role_id': role_ciso.id if role_ciso else None,
                'notify_days_before': 30,
                'checklist_template': [
                    {'description': 'Revisar metodología de evaluación de riesgos', 'completed': False},
                    {'description': 'Identificar activos críticos', 'completed': False},
                    {'description': 'Identificar amenazas y vulnerabilidades', 'completed': False},
                    {'description': 'Evaluar probabilidad e impacto', 'completed': False},
                    {'description': 'Calcular nivel de riesgo inherente', 'completed': False},
                    {'description': 'Definir tratamiento de riesgos', 'completed': False},
                    {'description': 'Actualizar registro de riesgos', 'completed': False},
                    {'description': 'Presentar resultados a la dirección', 'completed': False},
                ],
                'requires_evidence': True,
                'requires_approval': True,
            },

            # 4. REVISIÓN DE POLÍTICAS (5.1)
            {
                'title': 'Revisión Anual de Políticas de Seguridad',
                'description': '''Revisión anual de todas las políticas de seguridad de la información.

Incluye:
- Política general de seguridad
- Políticas específicas (uso aceptable, control de accesos, etc.)
- Verificación de vigencia y aplicabilidad
- Actualización según cambios normativos

Control ISO 27001: 5.1 Políticas de seguridad de la información''',
                'category': TaskCategory.REVISION_POLITICAS,
                'frequency': TaskFrequency.ANUAL,
                'priority': TaskPriority.ALTA,
                'iso_control': '5.1',
                'estimated_hours': 16.0,
                'default_role_id': role_ciso.id if role_ciso else None,
                'notify_days_before': 14,
                'checklist_template': [
                    {'description': 'Recopilar todas las políticas vigentes', 'completed': False},
                    {'description': 'Revisar aplicabilidad y vigencia', 'completed': False},
                    {'description': 'Verificar cumplimiento normativo', 'completed': False},
                    {'description': 'Identificar necesidad de actualizaciones', 'completed': False},
                    {'description': 'Actualizar políticas según sea necesario', 'completed': False},
                    {'description': 'Someter a aprobación de dirección', 'completed': False},
                    {'description': 'Comunicar cambios a usuarios', 'completed': False},
                ],
                'requires_evidence': True,
                'requires_approval': True,
            },

            # 5. FORMACIÓN (7.2/7.3)
            {
                'title': 'Sesión Trimestral de Concienciación en Seguridad',
                'description': '''Sesión de formación y concienciación en seguridad de la información para todo el personal.

Temas a cubrir:
- Amenazas actuales (phishing, malware, ingeniería social)
- Buenas prácticas de seguridad
- Responsabilidades del personal
- Procedimientos de reporte de incidentes

Controles ISO 27001: 7.2 Competencia, 7.3 Concienciación''',
                'category': TaskCategory.FORMACION_CONCIENCIACION,
                'frequency': TaskFrequency.TRIMESTRAL,
                'priority': TaskPriority.ALTA,
                'iso_control': '7.2/7.3',
                'estimated_hours': 4.0,
                'default_role_id': role_ciso.id if role_ciso else None,
                'notify_days_before': 14,
                'checklist_template': [
                    {'description': 'Preparar material de formación', 'completed': False},
                    {'description': 'Programar sesión con RR.HH.', 'completed': False},
                    {'description': 'Notificar a participantes', 'completed': False},
                    {'description': 'Impartir sesión de formación', 'completed': False},
                    {'description': 'Realizar evaluación/test', 'completed': False},
                    {'description': 'Registrar asistencia', 'completed': False},
                    {'description': 'Archivar evidencias', 'completed': False},
                ],
                'requires_evidence': True,
                'requires_approval': False,
            },

            # 6. COPIAS DE SEGURIDAD (8.13)
            {
                'title': 'Verificación Semanal de Copias de Seguridad',
                'description': '''Verificación semanal del correcto funcionamiento del sistema de copias de seguridad.

Actividades:
- Verificar ejecución de backups programados
- Comprobar integridad de copias
- Revisar logs de errores
- Verificar espacio disponible
- Documentar incidencias

Control ISO 27001: 8.13 Copias de seguridad de la información''',
                'category': TaskCategory.COPIAS_SEGURIDAD,
                'frequency': TaskFrequency.SEMANAL,
                'priority': TaskPriority.ALTA,
                'iso_control': '8.13',
                'estimated_hours': 1.0,
                'default_role_id': role_admin.id if role_admin else None,
                'notify_days_before': 1,
                'checklist_template': [
                    {'description': 'Verificar ejecución de backups diarios', 'completed': False},
                    {'description': 'Revisar logs del sistema de backup', 'completed': False},
                    {'description': 'Verificar integridad de copias', 'completed': False},
                    {'description': 'Comprobar espacio de almacenamiento', 'completed': False},
                    {'description': 'Documentar cualquier incidencia', 'completed': False},
                ],
                'requires_evidence': True,
                'requires_approval': False,
            },

            # 7. REVISIÓN DE ACCESOS (5.18)
            {
                'title': 'Revisión Trimestral de Derechos de Acceso',
                'description': '''Revisión trimestral de los derechos de acceso de usuarios a sistemas y aplicaciones.

Objetivos:
- Verificar que los accesos son apropiados
- Identificar accesos innecesarios o excesivos
- Detectar cuentas inactivas
- Revocar accesos no autorizados

Control ISO 27001: 5.18 Derechos de acceso''',
                'category': TaskCategory.REVISION_ACCESOS,
                'frequency': TaskFrequency.TRIMESTRAL,
                'priority': TaskPriority.ALTA,
                'iso_control': '5.18',
                'estimated_hours': 6.0,
                'default_role_id': role_admin.id if role_admin else None,
                'notify_days_before': 7,
                'checklist_template': [
                    {'description': 'Exportar listado de usuarios y permisos', 'completed': False},
                    {'description': 'Revisar con responsables de cada área', 'completed': False},
                    {'description': 'Identificar accesos no necesarios', 'completed': False},
                    {'description': 'Detectar cuentas inactivas', 'completed': False},
                    {'description': 'Revocar accesos identificados', 'completed': False},
                    {'description': 'Documentar cambios realizados', 'completed': False},
                ],
                'requires_evidence': True,
                'requires_approval': False,
            },

            # 8. INVENTARIO DE ACTIVOS (5.9)
            {
                'title': 'Actualización Mensual del Inventario de Activos',
                'description': '''Actualización mensual del inventario de activos de información.

Incluye:
- Hardware (servidores, equipos, dispositivos)
- Software (aplicaciones, licencias)
- Información (bases de datos, documentos)
- Servicios (cloud, proveedores)

Control ISO 27001: 5.9 Inventario de activos''',
                'category': TaskCategory.ACTUALIZACION_INVENTARIOS,
                'frequency': TaskFrequency.MENSUAL,
                'priority': TaskPriority.MEDIA,
                'iso_control': '5.9',
                'estimated_hours': 3.0,
                'default_role_id': role_admin.id if role_admin else None,
                'notify_days_before': 3,
                'checklist_template': [
                    {'description': 'Verificar altas de nuevos activos', 'completed': False},
                    {'description': 'Registrar bajas de activos', 'completed': False},
                    {'description': 'Actualizar valoración de activos', 'completed': False},
                    {'description': 'Verificar propietarios asignados', 'completed': False},
                    {'description': 'Actualizar clasificación de activos', 'completed': False},
                ],
                'requires_evidence': False,
                'requires_approval': False,
            },

            # 9. REVISIÓN DE PROVEEDORES (5.22)
            {
                'title': 'Revisión Semestral de Servicios de Proveedores',
                'description': '''Revisión semestral de servicios prestados por proveedores externos.

Evaluación:
- Cumplimiento de SLAs
- Seguridad de servicios cloud
- Gestión de accesos de terceros
- Cumplimiento de cláusulas de seguridad

Control ISO 27001: 5.22 Seguimiento, revisión y gestión del cambio de servicios de proveedores''',
                'category': TaskCategory.REVISION_PROVEEDORES,
                'frequency': TaskFrequency.SEMESTRAL,
                'priority': TaskPriority.MEDIA,
                'iso_control': '5.22',
                'estimated_hours': 8.0,
                'default_role_id': role_ciso.id if role_ciso else None,
                'notify_days_before': 14,
                'checklist_template': [
                    {'description': 'Listar todos los proveedores de servicios TI', 'completed': False},
                    {'description': 'Revisar cumplimiento de SLAs', 'completed': False},
                    {'description': 'Evaluar medidas de seguridad implementadas', 'completed': False},
                    {'description': 'Verificar gestión de incidentes', 'completed': False},
                    {'description': 'Revisar accesos de personal de proveedores', 'completed': False},
                    {'description': 'Documentar hallazgos y recomendaciones', 'completed': False},
                ],
                'requires_evidence': True,
                'requires_approval': False,
            },

            # 10. GESTIÓN DE VULNERABILIDADES (8.8)
            {
                'title': 'Escaneo Mensual de Vulnerabilidades',
                'description': '''Escaneo mensual de vulnerabilidades en sistemas y aplicaciones.

Alcance:
- Servidores y estaciones de trabajo
- Aplicaciones web
- Infraestructura de red
- Bases de datos

Control ISO 27001: 8.8 Gestión de vulnerabilidades técnicas''',
                'category': TaskCategory.GESTION_VULNERABILIDADES,
                'frequency': TaskFrequency.MENSUAL,
                'priority': TaskPriority.ALTA,
                'iso_control': '8.8',
                'estimated_hours': 6.0,
                'default_role_id': role_admin.id if role_admin else None,
                'notify_days_before': 3,
                'checklist_template': [
                    {'description': 'Ejecutar escaneo de vulnerabilidades', 'completed': False},
                    {'description': 'Analizar resultados del escaneo', 'completed': False},
                    {'description': 'Clasificar vulnerabilidades por criticidad', 'completed': False},
                    {'description': 'Planificar remediación de vulnerabilidades críticas', 'completed': False},
                    {'description': 'Aplicar parches y correcciones', 'completed': False},
                    {'description': 'Verificar remediación', 'completed': False},
                    {'description': 'Documentar acciones tomadas', 'completed': False},
                ],
                'requires_evidence': True,
                'requires_approval': False,
            },

            # 11. REVISIÓN DE INCIDENTES (5.27)
            {
                'title': 'Análisis Trimestral de Incidentes de Seguridad',
                'description': '''Análisis trimestral de incidentes de seguridad registrados.

Objetivos:
- Revisar incidentes del trimestre
- Identificar patrones y tendencias
- Evaluar eficacia de la respuesta
- Proponer mejoras en los procesos

Control ISO 27001: 5.27 Aprendizaje de los incidentes de seguridad de la información''',
                'category': TaskCategory.REVISION_INCIDENTES,
                'frequency': TaskFrequency.TRIMESTRAL,
                'priority': TaskPriority.MEDIA,
                'iso_control': '5.27',
                'estimated_hours': 4.0,
                'default_role_id': role_ciso.id if role_ciso else None,
                'notify_days_before': 7,
                'checklist_template': [
                    {'description': 'Recopilar incidentes del trimestre', 'completed': False},
                    {'description': 'Analizar causas raíz', 'completed': False},
                    {'description': 'Identificar patrones recurrentes', 'completed': False},
                    {'description': 'Evaluar tiempos de respuesta', 'completed': False},
                    {'description': 'Proponer mejoras en procesos', 'completed': False},
                    {'description': 'Generar informe de lecciones aprendidas', 'completed': False},
                ],
                'requires_evidence': True,
                'requires_approval': False,
            },

            # 12. CONTINUIDAD DE NEGOCIO (5.30)
            {
                'title': 'Prueba Anual del Plan de Continuidad de Negocio',
                'description': '''Prueba anual del Plan de Continuidad de Negocio y Recuperación ante Desastres.

Actividades:
- Simulación de escenarios de desastre
- Prueba de procedimientos de recuperación
- Verificación de backups y sistemas alternativos
- Evaluación de tiempos de recuperación

Control ISO 27001: 5.30 Preparación de las TIC para la continuidad del negocio''',
                'category': TaskCategory.CONTINUIDAD_NEGOCIO,
                'frequency': TaskFrequency.ANUAL,
                'priority': TaskPriority.CRITICA,
                'iso_control': '5.30',
                'estimated_hours': 16.0,
                'default_role_id': role_admin.id if role_admin else None,
                'notify_days_before': 30,
                'checklist_template': [
                    {'description': 'Revisar y actualizar plan de continuidad', 'completed': False},
                    {'description': 'Definir escenario de prueba', 'completed': False},
                    {'description': 'Notificar a participantes', 'completed': False},
                    {'description': 'Ejecutar simulacro', 'completed': False},
                    {'description': 'Documentar tiempos de recuperación', 'completed': False},
                    {'description': 'Identificar mejoras necesarias', 'completed': False},
                    {'description': 'Actualizar plan según hallazgos', 'completed': False},
                    {'description': 'Informar a dirección', 'completed': False},
                ],
                'requires_evidence': True,
                'requires_approval': True,
            },

            # 13. REQUISITOS LEGALES (5.31)
            {
                'title': 'Revisión Anual de Requisitos Legales y Regulatorios',
                'description': '''Revisión anual de requisitos legales y regulatorios aplicables a la seguridad de la información.

Incluye:
- GDPR/RGPD (protección de datos)
- Ley Orgánica de Protección de Datos
- Normativa sectorial aplicable
- Obligaciones contractuales

Control ISO 27001: 5.31 Requisitos legales, reglamentarios y contractuales''',
                'category': TaskCategory.REVISION_LEGAL,
                'frequency': TaskFrequency.ANUAL,
                'priority': TaskPriority.ALTA,
                'iso_control': '5.31',
                'estimated_hours': 12.0,
                'default_role_id': role_ciso.id if role_ciso else None,
                'notify_days_before': 30,
                'checklist_template': [
                    {'description': 'Identificar normativa aplicable', 'completed': False},
                    {'description': 'Verificar cambios normativos del año', 'completed': False},
                    {'description': 'Evaluar cumplimiento actual', 'completed': False},
                    {'description': 'Identificar gaps de cumplimiento', 'completed': False},
                    {'description': 'Planificar acciones correctivas', 'completed': False},
                    {'description': 'Actualizar matriz de cumplimiento legal', 'completed': False},
                ],
                'requires_evidence': True,
                'requires_approval': False,
            },

            # 14. REVISIÓN POR LA DIRECCIÓN (9.3)
            {
                'title': 'Revisión Semestral del SGSI por la Dirección',
                'description': '''Revisión semestral del desempeño del SGSI por parte de la alta dirección.

Agenda:
- Resultados de auditorías
- Estado de no conformidades
- Resultados de indicadores
- Cambios en contexto/riesgos
- Recursos necesarios
- Oportunidades de mejora

Control ISO 27001: 9.3 Revisión por la dirección''',
                'category': TaskCategory.REVISION_DIRECCION,
                'frequency': TaskFrequency.SEMESTRAL,
                'priority': TaskPriority.CRITICA,
                'iso_control': '9.3',
                'estimated_hours': 8.0,
                'default_role_id': role_ciso.id if role_ciso else None,
                'notify_days_before': 21,
                'checklist_template': [
                    {'description': 'Preparar informe de desempeño del SGSI', 'completed': False},
                    {'description': 'Recopilar resultados de auditorías', 'completed': False},
                    {'description': 'Analizar indicadores de desempeño', 'completed': False},
                    {'description': 'Evaluar cumplimiento de objetivos', 'completed': False},
                    {'description': 'Identificar necesidades de recursos', 'completed': False},
                    {'description': 'Convocar reunión con dirección', 'completed': False},
                    {'description': 'Presentar resultados', 'completed': False},
                    {'description': 'Documentar decisiones y acuerdos', 'completed': False},
                ],
                'requires_evidence': True,
                'requires_approval': True,
            },

            # 15. PRUEBAS DE RESTAURACIÓN (8.14)
            {
                'title': 'Prueba Semestral de Restauración de Copias de Seguridad',
                'description': '''Prueba semestral de restauración de copias de seguridad para verificar su viabilidad.

Objetivos:
- Verificar integridad de backups
- Comprobar procedimientos de restauración
- Medir tiempos de recuperación (RTO)
- Validar completitud de datos restaurados

Control ISO 27001: 8.14 Redundancia de instalaciones de procesamiento de información''',
                'category': TaskCategory.PRUEBAS_RECUPERACION,
                'frequency': TaskFrequency.SEMESTRAL,
                'priority': TaskPriority.ALTA,
                'iso_control': '8.14',
                'estimated_hours': 8.0,
                'default_role_id': role_admin.id if role_admin else None,
                'notify_days_before': 14,
                'checklist_template': [
                    {'description': 'Seleccionar sistemas/datos para prueba', 'completed': False},
                    {'description': 'Preparar entorno de pruebas', 'completed': False},
                    {'description': 'Ejecutar proceso de restauración', 'completed': False},
                    {'description': 'Verificar integridad de datos restaurados', 'completed': False},
                    {'description': 'Medir tiempos de recuperación', 'completed': False},
                    {'description': 'Documentar resultados y problemas', 'completed': False},
                    {'description': 'Actualizar procedimientos si es necesario', 'completed': False},
                ],
                'requires_evidence': True,
                'requires_approval': False,
            },
        ]

        # Crear plantillas
        created_count = 0
        for template_data in templates_data:
            try:
                template = TaskTemplate(**template_data)
                db.session.add(template)
                created_count += 1
                print(f"✅ Creada: '{template_data['title']}'")
            except Exception as e:
                print(f"❌ Error creando '{template_data['title']}': {str(e)}")

        db.session.commit()

        print(f"\n🎉 Proceso completado!")
        print(f"📊 Plantillas creadas: {created_count}")
        print(f"📊 Total de plantillas: {TaskTemplate.query.count()}")
        print(f"\n💡 Ahora puedes generar tareas desde estas plantillas en /tareas/templates")


def main():
    """Función principal"""
    print("=" * 70)
    print("  Inicialización del Módulo de Gestión de Tareas ISO 27001")
    print("=" * 70)
    print()

    # Verificar que las tablas existan
    if not check_tables_exist():
        return 1

    # Inicializar plantillas
    try:
        init_task_templates()
        print()
        print("✅ Inicialización completada correctamente")
        return 0
    except Exception as e:
        print(f"\n❌ Error durante la inicialización: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
