#!/usr/bin/env python3
"""
Script para crear plantillas de tareas ISO 27001 predefinidas
Ejecutar: python seed_tasks.py
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from application import app
from models import db, Role, User
from app.models.task import TaskTemplate, TaskFrequency, TaskPriority, TaskCategory


def create_task_templates():
    """Crea plantillas de tareas predefinidas basadas en ISO 27001"""

    with app.app_context():
        print("🚀 Iniciando creación de plantillas de tareas ISO 27001...")

        # Obtener roles
        role_ciso = Role.query.filter_by(name='ciso').first()
        role_admin = Role.query.filter_by(name='admin').first()
        role_auditor = Role.query.filter_by(name='auditor').first()

        if not role_ciso:
            print("⚠️  Advertencia: Rol 'CISO' no encontrado. Algunas plantillas no tendrán rol asignado.")

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
                'requires_evidence': True,
                'requires_approval': True,
                'checklist_template': [
                    {'item': 'Revisar controles de acceso físico y lógico', 'completed': False},
                    {'item': 'Verificar registros de auditoría', 'completed': False},
                    {'item': 'Comprobar actualizaciones de seguridad aplicadas', 'completed': False},
                    {'item': 'Revisar incidentes de seguridad del trimestre', 'completed': False},
                    {'item': 'Evaluar eficacia de controles críticos', 'completed': False},
                    {'item': 'Documentar hallazgos y recomendaciones', 'completed': False},
                    {'item': 'Presentar informe a la dirección', 'completed': False}
                ]
            },

            # 2. AUDITORÍA INTERNA (9.2)
            {
                'title': 'Auditoría Interna del SGSI - Semestral',
                'description': '''Realizar auditoría interna del Sistema de Gestión de Seguridad de la Información según requisito 9.2 de ISO 27001.

Alcance:
- Revisar conformidad con ISO 27001
- Evaluar implementación de controles del Anexo A
- Verificar eficacia del SGSI
- Identificar oportunidades de mejora

La auditoría debe ser objetiva e imparcial.''',
                'category': TaskCategory.AUDITORIA_INTERNA,
                'frequency': TaskFrequency.SEMESTRAL,
                'priority': TaskPriority.CRITICA,
                'iso_control': '9.2',
                'estimated_hours': 24.0,
                'default_role_id': role_auditor.id if role_auditor else None,
                'notify_days_before': 14,
                'requires_evidence': True,
                'requires_approval': True,
                'checklist_template': [
                    {'item': 'Preparar plan de auditoría', 'completed': False},
                    {'item': 'Comunicar programa de auditoría', 'completed': False},
                    {'item': 'Realizar entrevistas con responsables', 'completed': False},
                    {'item': 'Revisar documentación del SGSI', 'completed': False},
                    {'item': 'Verificar controles in situ', 'completed': False},
                    {'item': 'Documentar hallazgos y no conformidades', 'completed': False},
                    {'item': 'Presentar informe de auditoría', 'completed': False},
                    {'item': 'Definir acciones correctivas', 'completed': False}
                ]
            },

            # 3. EVALUACIÓN DE RIESGOS (8.2)
            {
                'title': 'Evaluación Anual de Riesgos de Seguridad',
                'description': '''Evaluación anual de riesgos de seguridad de la información según requisito 8.2 de ISO 27001.

Incluye:
- Identificación de activos críticos
- Análisis de amenazas y vulnerabilidades
- Evaluación de impacto y probabilidad
- Actualización del registro de riesgos
- Revisión de tratamientos de riesgo

Debe considerar cambios en el contexto organizacional.''',
                'category': TaskCategory.EVALUACION_RIESGOS,
                'frequency': TaskFrequency.ANUAL,
                'priority': TaskPriority.CRITICA,
                'iso_control': '8.2',
                'estimated_hours': 40.0,
                'default_role_id': role_ciso.id if role_ciso else None,
                'notify_days_before': 30,
                'requires_evidence': True,
                'requires_approval': True
            },

            # 4. REVISIÓN DE POLÍTICAS (5.1)
            {
                'title': 'Revisión Anual de Políticas de Seguridad',
                'description': '''Revisión anual de todas las políticas de seguridad de la información según control 5.1.

Políticas a revisar:
- Política general de seguridad
- Política de control de acceso
- Política de uso aceptable
- Política de clasificación de información
- Otras políticas temáticas

Asegurar vigencia, adecuación y comunicación.''',
                'category': TaskCategory.REVISION_POLITICAS,
                'frequency': TaskFrequency.ANUAL,
                'priority': TaskPriority.ALTA,
                'iso_control': '5.1',
                'estimated_hours': 16.0,
                'default_role_id': role_ciso.id if role_ciso else None,
                'notify_days_before': 30,
                'requires_evidence': True,
                'requires_approval': True
            },

            # 5. FORMACIÓN Y CONCIENCIACIÓN (7.2, 7.3)
            {
                'title': 'Sesión Trimestral de Concienciación en Seguridad',
                'description': '''Sesión de formación y concienciación en seguridad de la información para todo el personal.

Temas a cubrir:
- Amenazas actuales (phishing, ransomware, etc.)
- Buenas prácticas de seguridad
- Políticas y procedimientos
- Responsabilidades del personal
- Casos de estudio

Cumple con requisitos 7.2 (Competencia) y 7.3 (Concienciación).''',
                'category': TaskCategory.FORMACION_CONCIENCIACION,
                'frequency': TaskFrequency.TRIMESTRAL,
                'priority': TaskPriority.ALTA,
                'iso_control': '7.3',
                'estimated_hours': 4.0,
                'default_role_id': role_ciso.id if role_ciso else None,
                'notify_days_before': 14,
                'requires_evidence': True,
                'requires_approval': False
            },

            # 6. COPIAS DE SEGURIDAD (8.13)
            {
                'title': 'Verificación Semanal de Copias de Seguridad',
                'description': '''Verificación semanal de las copias de seguridad de información crítica según control 8.13.

Verificar:
- Ejecución correcta de backups programados
- Integridad de los datos respaldados
- Disponibilidad de medios de respaldo
- Registros de ejecución
- Alertas o errores

Documentar cualquier incidencia.''',
                'category': TaskCategory.COPIAS_SEGURIDAD,
                'frequency': TaskFrequency.SEMANAL,
                'priority': TaskPriority.ALTA,
                'iso_control': '8.13',
                'estimated_hours': 1.0,
                'default_role_id': None,
                'notify_days_before': 1,
                'requires_evidence': False,
                'requires_approval': False
            },

            # 7. REVISIÓN DE ACCESOS (5.18)
            {
                'title': 'Revisión Trimestral de Derechos de Acceso',
                'description': '''Revisión trimestral de derechos de acceso de usuarios según control 5.18.

Objetivos:
- Verificar que los accesos son apropiados para cada rol
- Identificar cuentas inactivas o huérfanas
- Validar accesos privilegiados
- Revocar accesos innecesarios
- Actualizar matriz de accesos

Especial atención a cuentas de administrador.''',
                'category': TaskCategory.REVISION_ACCESOS,
                'frequency': TaskFrequency.TRIMESTRAL,
                'priority': TaskPriority.ALTA,
                'iso_control': '5.18',
                'estimated_hours': 6.0,
                'default_role_id': role_ciso.id if role_ciso else None,
                'notify_days_before': 7,
                'requires_evidence': True,
                'requires_approval': True
            },

            # 8. ACTUALIZACIÓN DE INVENTARIOS (5.9)
            {
                'title': 'Actualización Mensual del Inventario de Activos',
                'description': '''Actualización mensual del inventario de activos de información según control 5.9.

Actualizar:
- Nuevos activos de información
- Activos dados de baja
- Cambios en propietarios
- Cambios en clasificación
- Cambios en ubicación

Mantener el inventario completo y preciso.''',
                'category': TaskCategory.ACTUALIZACION_INVENTARIOS,
                'frequency': TaskFrequency.MENSUAL,
                'priority': TaskPriority.MEDIA,
                'iso_control': '5.9',
                'estimated_hours': 3.0,
                'default_role_id': None,
                'notify_days_before': 3,
                'requires_evidence': True,
                'requires_approval': False
            },

            # 9. REVISIÓN DE PROVEEDORES (5.22)
            {
                'title': 'Revisión Semestral de Servicios de Proveedores',
                'description': '''Revisión semestral de proveedores y servicios contratados según control 5.22.

Evaluar:
- Cumplimiento de acuerdos de nivel de servicio (SLA)
- Incidentes de seguridad reportados
- Cambios en servicios prestados
- Cumplimiento de políticas de seguridad
- Necesidad de renovación o terminación

Documentar resultados y acciones necesarias.''',
                'category': TaskCategory.REVISION_PROVEEDORES,
                'frequency': TaskFrequency.SEMESTRAL,
                'priority': TaskPriority.MEDIA,
                'iso_control': '5.22',
                'estimated_hours': 8.0,
                'default_role_id': role_ciso.id if role_ciso else None,
                'notify_days_before': 14,
                'requires_evidence': True,
                'requires_approval': True
            },

            # 10. GESTIÓN DE VULNERABILIDADES (8.8)
            {
                'title': 'Escaneo Mensual de Vulnerabilidades',
                'description': '''Escaneo mensual de vulnerabilidades en sistemas e infraestructura según control 8.8.

Incluye:
- Escaneo automatizado de vulnerabilidades
- Análisis de parches pendientes
- Evaluación de criticidad
- Planificación de remediación
- Seguimiento de vulnerabilidades críticas

Priorizar según nivel de riesgo.''',
                'category': TaskCategory.GESTION_VULNERABILIDADES,
                'frequency': TaskFrequency.MENSUAL,
                'priority': TaskPriority.ALTA,
                'iso_control': '8.8',
                'estimated_hours': 4.0,
                'default_role_id': None,
                'notify_days_before': 3,
                'requires_evidence': True,
                'requires_approval': False
            },

            # 11. REVISIÓN DE INCIDENTES (5.27)
            {
                'title': 'Análisis Trimestral de Incidentes de Seguridad',
                'description': '''Análisis trimestral de incidentes de seguridad para aprendizaje según control 5.27.

Analizar:
- Incidentes ocurridos en el trimestre
- Causas raíz identificadas
- Efectividad de la respuesta
- Lecciones aprendidas
- Mejoras a implementar

Fortalecer capacidades de respuesta.''',
                'category': TaskCategory.REVISION_INCIDENTES,
                'frequency': TaskFrequency.TRIMESTRAL,
                'priority': TaskPriority.MEDIA,
                'iso_control': '5.27',
                'estimated_hours': 4.0,
                'default_role_id': role_ciso.id if role_ciso else None,
                'notify_days_before': 7,
                'requires_evidence': True,
                'requires_approval': False
            },

            # 12. CONTINUIDAD DE NEGOCIO (5.30)
            {
                'title': 'Prueba Anual del Plan de Continuidad de Negocio',
                'description': '''Prueba anual del Plan de Continuidad de Negocio y Recuperación ante Desastres según control 5.30.

Incluye:
- Simulacro de escenario de desastre
- Verificación de procedimientos de recuperación
- Prueba de restauración de copias de seguridad
- Evaluación de tiempos de recuperación (RTO/RPO)
- Identificación de mejoras necesarias

Documentar resultados y actualizar plan según sea necesario.''',
                'category': TaskCategory.CONTINUIDAD_NEGOCIO,
                'frequency': TaskFrequency.ANUAL,
                'priority': TaskPriority.CRITICA,
                'iso_control': '5.30',
                'estimated_hours': 16.0,
                'default_role_id': role_ciso.id if role_ciso else None,
                'notify_days_before': 30,
                'requires_evidence': True,
                'requires_approval': True
            },

            # 13. REVISIÓN LEGAL (5.31)
            {
                'title': 'Revisión Anual de Requisitos Legales y Regulatorios',
                'description': '''Revisión anual de cumplimiento de requisitos legales y regulatorios según control 5.31.

Verificar cumplimiento de:
- Protección de datos (GDPR, LOPDGDD)
- Legislación sectorial aplicable
- Requisitos contractuales
- Normativas de ciberseguridad
- Propiedad intelectual

Identificar cambios legislativos y acciones necesarias.''',
                'category': TaskCategory.REVISION_LEGAL,
                'frequency': TaskFrequency.ANUAL,
                'priority': TaskPriority.ALTA,
                'iso_control': '5.31',
                'estimated_hours': 12.0,
                'default_role_id': role_ciso.id if role_ciso else None,
                'notify_days_before': 30,
                'requires_evidence': True,
                'requires_approval': True
            },

            # 14. REVISIÓN POR LA DIRECCIÓN (9.3)
            {
                'title': 'Revisión Semestral del SGSI por la Dirección',
                'description': '''Revisión del SGSI por la alta dirección según requisito 9.3 de ISO 27001.

Entradas a la revisión:
- Estado de acciones de revisiones previas
- Cambios en contexto interno/externo
- Retroalimentación sobre desempeño del SGSI
- Resultados de auditorías
- Cumplimiento de objetivos de seguridad
- Resultados de evaluación de riesgos
- Oportunidades de mejora continua

Resultados: Decisiones sobre mejoras y necesidad de cambios.''',
                'category': TaskCategory.REVISION_DIRECCION,
                'frequency': TaskFrequency.SEMESTRAL,
                'priority': TaskPriority.CRITICA,
                'iso_control': '9.3',
                'estimated_hours': 4.0,
                'default_role_id': role_ciso.id if role_ciso else None,
                'notify_days_before': 21,
                'requires_evidence': True,
                'requires_approval': True
            },

            # 15. PRUEBAS DE RECUPERACIÓN (8.14)
            {
                'title': 'Prueba Semestral de Restauración de Copias de Seguridad',
                'description': '''Prueba semestral de restauración de copias de seguridad según control 8.14.

Verificar:
- Restauración completa de sistema crítico
- Integridad de datos restaurados
- Tiempo de restauración (RTO)
- Procedimientos de recuperación
- Funcionamiento post-restauración

Esta prueba valida la eficacia de las copias de seguridad.''',
                'category': TaskCategory.PRUEBAS_RECUPERACION,
                'frequency': TaskFrequency.SEMESTRAL,
                'priority': TaskPriority.ALTA,
                'iso_control': '8.14',
                'estimated_hours': 6.0,
                'default_role_id': None,
                'notify_days_before': 14,
                'requires_evidence': True,
                'requires_approval': False
            }
        ]

        # Crear plantillas
        created_count = 0
        for template_data in templates_data:
            # Verificar si ya existe
            existing = TaskTemplate.query.filter_by(
                title=template_data['title']
            ).first()

            if existing:
                print(f"⏭️  Saltando: '{template_data['title']}' (ya existe)")
                continue

            # Crear plantilla
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
                created_by_id=1  # Usuario admin
            )

            db.session.add(template)
            created_count += 1
            print(f"✅ Creada: '{template.title}'")

        # Guardar cambios
        db.session.commit()

        print(f"\n🎉 Proceso completado!")
        print(f"📊 Plantillas creadas: {created_count}")
        print(f"📊 Total de plantillas: {TaskTemplate.query.count()}")
        print(f"\n💡 Ahora puedes generar tareas desde estas plantillas en /tasks/templates")


if __name__ == '__main__':
    create_task_templates()
