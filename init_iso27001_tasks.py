#!/usr/bin/env python3
"""
Script de inicialización completa de Tareas Periódicas ISO/IEC 27001:2023
Genera automáticamente todas las plantillas de tareas recomendadas por la norma

Este script se ejecuta automáticamente en nuevas instalaciones del SGSI
Basado en UNE-ISO/IEC 27001:2023 - Requisitos del SGSI

Uso:
    python init_iso27001_tasks.py

Autor: Sistema ISMS Manager
Fecha: 2025
"""
import sys
import os
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# NOTA: Las importaciones de Flask/SQLAlchemy están dentro de las funciones
# para evitar importaciones circulares cuando se llama desde seed_data.py
# Solo importamos los enums necesarios para get_task_templates_iso27001()


def get_task_templates_iso27001():
    """
    Retorna el catálogo completo de tareas periódicas recomendadas por ISO/IEC 27001:2023

    Organizado por capítulos de la norma:
    - Capítulo 5: Liderazgo
    - Capítulo 6: Planificación
    - Capítulo 7: Soporte
    - Capítulo 8: Operación
    - Capítulo 9: Evaluación del desempeño
    - Capítulo 10: Mejora
    - Anexo A: Controles de seguridad
    """
    # Importar enums dentro de la función para evitar importaciones circulares
    from app.models.task import TaskFrequency, TaskPriority, TaskCategory

    templates = []

    # =========================================================================
    # CAPÍTULO 5: LIDERAZGO
    # =========================================================================

    # 5.1 Políticas para la seguridad de la información (Control A.5.1)
    templates.append({
        'title': 'Revisión Anual de Política de Seguridad de la Información',
        'description': '''Revisión y actualización de la política general de seguridad y políticas temáticas específicas.

Alcance:
- Política general de seguridad de la información
- Políticas temáticas específicas (control de acceso, uso aceptable, clasificación, etc.)
- Verificar aprobación por la dirección
- Asegurar comunicación efectiva
- Revisar en intervalos planificados y ante cambios significativos

Requisito ISO 27001: Control A.5.1 - Políticas para la seguridad de la información
La política debe ser definida, aprobada, publicada, comunicada y revisada.''',
        'category': TaskCategory.REVISION_POLITICAS,
        'frequency': TaskFrequency.ANUAL,
        'priority': TaskPriority.CRITICA,
        'iso_control': '5.1',
        'estimated_hours': 16.0,
        'notify_days_before': 30,
        'checklist_template': [
            {'description': 'Recopilar todas las políticas vigentes del SGSI', 'completed': False},
            {'description': 'Revisar adecuación a requisitos de negocio actuales', 'completed': False},
            {'description': 'Verificar cumplimiento normativo y legal', 'completed': False},
            {'description': 'Actualizar políticas según cambios identificados', 'completed': False},
            {'description': 'Someter a aprobación de alta dirección', 'completed': False},
            {'description': 'Publicar y comunicar políticas actualizadas', 'completed': False},
            {'description': 'Registrar reconocimiento del personal pertinente', 'completed': False},
        ],
        'requires_evidence': True,
        'requires_approval': True,
    })

    # 5.5 Contacto con autoridades (Control A.5.5)
    templates.append({
        'title': 'Actualización Semestral de Contactos con Autoridades',
        'description': '''Actualización del directorio de contactos con autoridades competentes.

Contactos a mantener:
- Fuerzas y Cuerpos de Seguridad del Estado
- Autoridades de protección de datos (AEPD)
- Organismos reguladores sectoriales
- CERTs/CSIRTs nacionales (INCIBE-CERT)
- Autoridades locales pertinentes

Requisito ISO 27001: Control A.5.5 - Contacto con las autoridades
Se deben establecer y mantener contactos adecuados con autoridades pertinentes.''',
        'category': TaskCategory.OTROS,
        'frequency': TaskFrequency.SEMESTRAL,
        'priority': TaskPriority.MEDIA,
        'iso_control': '5.5',
        'estimated_hours': 2.0,
        'notify_days_before': 7,
        'requires_evidence': True,
        'requires_approval': False,
    })

    # =========================================================================
    # CAPÍTULO 6: PLANIFICACIÓN
    # =========================================================================

    # 6.1.2 Evaluación de riesgos (Requisito 8.2)
    templates.append({
        'title': 'Evaluación Anual de Riesgos de Seguridad de la Información',
        'description': '''Evaluación completa de riesgos de seguridad de la información según metodología establecida.

Proceso:
- Identificar riesgos asociados a pérdida de confidencialidad, integridad y disponibilidad
- Identificar dueños de los riesgos
- Analizar consecuencias potenciales
- Evaluar probabilidad realista de ocurrencia
- Determinar niveles de riesgo
- Comparar con criterios de riesgo establecidos
- Priorizar tratamiento

Requisito ISO 27001: 6.1.2 Evaluación de riesgos y 8.2 Evaluación periódica
Debe realizarse a intervalos planificados y cuando se propongan cambios importantes.''',
        'category': TaskCategory.EVALUACION_RIESGOS,
        'frequency': TaskFrequency.ANUAL,
        'priority': TaskPriority.CRITICA,
        'iso_control': '6.1.2/8.2',
        'estimated_hours': 40.0,
        'notify_days_before': 30,
        'checklist_template': [
            {'description': 'Revisar y validar criterios de evaluación de riesgos', 'completed': False},
            {'description': 'Identificar activos críticos y su valoración', 'completed': False},
            {'description': 'Identificar amenazas aplicables a cada activo', 'completed': False},
            {'description': 'Identificar vulnerabilidades explotables', 'completed': False},
            {'description': 'Evaluar probabilidad e impacto de materialización', 'completed': False},
            {'description': 'Calcular nivel de riesgo inherente', 'completed': False},
            {'description': 'Evaluar eficacia de controles existentes', 'completed': False},
            {'description': 'Calcular riesgo residual', 'completed': False},
            {'description': 'Actualizar registro de riesgos', 'completed': False},
            {'description': 'Presentar resultados y obtener aceptación de dueños de riesgos', 'completed': False},
        ],
        'requires_evidence': True,
        'requires_approval': True,
    })

    # 6.1.3 Tratamiento de riesgos (Requisito 8.3)
    templates.append({
        'title': 'Revisión Semestral del Plan de Tratamiento de Riesgos',
        'description': '''Revisión del plan de tratamiento de riesgos y su estado de implementación.

Actividades:
- Verificar implementación de controles planificados
- Evaluar eficacia de tratamientos aplicados
- Revisar riesgos residuales
- Actualizar Declaración de Aplicabilidad (SOA)
- Obtener aprobación de dueños de riesgos

Requisito ISO 27001: 6.1.3 Tratamiento de riesgos y 8.3 Implementación
El plan de tratamiento debe implementarse y conservarse como información documentada.''',
        'category': TaskCategory.EVALUACION_RIESGOS,
        'frequency': TaskFrequency.SEMESTRAL,
        'priority': TaskPriority.ALTA,
        'iso_control': '6.1.3/8.3',
        'estimated_hours': 12.0,
        'notify_days_before': 14,
        'requires_evidence': True,
        'requires_approval': True,
    })

    # 6.2 Objetivos de seguridad
    templates.append({
        'title': 'Revisión Trimestral de Objetivos de Seguridad de la Información',
        'description': '''Monitorización y revisión del cumplimiento de objetivos de seguridad.

Verificar:
- Coherencia con política de seguridad
- Medibilidad de objetivos
- Consideración de requisitos aplicables
- Progreso hacia consecución
- Necesidad de actualización

Requisito ISO 27001: 6.2 Los objetivos deben ser monitorizados y actualizados.''',
        'category': TaskCategory.REVISION_CONTROLES,
        'frequency': TaskFrequency.TRIMESTRAL,
        'priority': TaskPriority.ALTA,
        'iso_control': '6.2',
        'estimated_hours': 4.0,
        'notify_days_before': 7,
        'requires_evidence': True,
        'requires_approval': False,
    })

    # =========================================================================
    # CAPÍTULO 7: SOPORTE
    # =========================================================================

    # 7.2 Competencia
    templates.append({
        'title': 'Evaluación Anual de Competencias en Seguridad de la Información',
        'description': '''Evaluación de competencias del personal que afecta al desempeño de seguridad.

Evaluar:
- Competencia necesaria según roles
- Formación recibida
- Experiencia adquirida
- Necesidades de capacitación
- Eficacia de acciones formativas

Requisito ISO 27001: 7.2 La organización debe determinar competencias necesarias y asegurar que las personas sean competentes.''',
        'category': TaskCategory.FORMACION_CONCIENCIACION,
        'frequency': TaskFrequency.ANUAL,
        'priority': TaskPriority.MEDIA,
        'iso_control': '7.2',
        'estimated_hours': 8.0,
        'notify_days_before': 14,
        'requires_evidence': True,
        'requires_approval': False,
    })

    # 7.3 Concienciación (Control A.6.3)
    templates.append({
        'title': 'Sesión Trimestral de Concienciación en Seguridad',
        'description': '''Sesión periódica de formación y concienciación para todo el personal.

Temas a cubrir:
- Política de seguridad de la información
- Contribución a eficacia del SGSI
- Implicaciones de incumplimiento
- Amenazas actuales (phishing, ransomware, ingeniería social)
- Buenas prácticas de seguridad
- Gestión de contraseñas
- Clasificación y manejo de información
- Reporte de incidentes

Requisito ISO 27001: 7.3 y Control A.6.3 - Concienciación, educación y formación
El personal debe ser consciente de la política, su contribución y las implicaciones de incumplimiento.''',
        'category': TaskCategory.FORMACION_CONCIENCIACION,
        'frequency': TaskFrequency.TRIMESTRAL,
        'priority': TaskPriority.ALTA,
        'iso_control': '7.3/A.6.3',
        'estimated_hours': 4.0,
        'notify_days_before': 14,
        'checklist_template': [
            {'description': 'Preparar contenidos actualizados de formación', 'completed': False},
            {'description': 'Incluir casos reales y lecciones aprendidas', 'completed': False},
            {'description': 'Programar sesiones con departamentos', 'completed': False},
            {'description': 'Impartir sesión de concienciación', 'completed': False},
            {'description': 'Realizar evaluación de conocimientos', 'completed': False},
            {'description': 'Registrar asistencia y resultados', 'completed': False},
            {'description': 'Archivar evidencias de formación', 'completed': False},
        ],
        'requires_evidence': True,
        'requires_approval': False,
    })

    # 7.5 Información documentada
    templates.append({
        'title': 'Revisión Semestral de Información Documentada del SGSI',
        'description': '''Revisión de la documentación del SGSI para asegurar su vigencia y adecuación.

Documentos a revisar:
- Alcance del SGSI
- Política y objetivos
- Metodología de evaluación de riesgos
- Declaración de Aplicabilidad (SOA)
- Planes de tratamiento de riesgos
- Procedimientos operacionales
- Registros de desempeño

Requisito ISO 27001: 7.5 El SGSI debe incluir información documentada requerida y necesaria para su eficacia.''',
        'category': TaskCategory.REVISION_CONTROLES,
        'frequency': TaskFrequency.SEMESTRAL,
        'priority': TaskPriority.MEDIA,
        'iso_control': '7.5',
        'estimated_hours': 6.0,
        'notify_days_before': 14,
        'requires_evidence': True,
        'requires_approval': False,
    })

    # =========================================================================
    # CAPÍTULO 8: OPERACIÓN
    # =========================================================================

    # 8.1 Planificación y control operacional (Control A.5.37)
    templates.append({
        'title': 'Revisión Mensual de Procedimientos Operacionales de Seguridad',
        'description': '''Revisión de procedimientos operacionales documentados de los medios de tratamiento de información.

Procedimientos a verificar:
- Procesamiento y manejo de información
- Copias de seguridad
- Gestión de cambios
- Gestión de capacidades
- Segregación de ambientes
- Protección contra malware

Requisito ISO 27001: 8.1 y Control A.5.37 - Documentación de procedimientos operacionales
Los procedimientos deben documentarse y ponerse a disposición de usuarios que los necesiten.''',
        'category': TaskCategory.MANTENIMIENTO_SEGURIDAD,
        'frequency': TaskFrequency.MENSUAL,
        'priority': TaskPriority.MEDIA,
        'iso_control': '8.1/A.5.37',
        'estimated_hours': 3.0,
        'notify_days_before': 3,
        'requires_evidence': True,
        'requires_approval': False,
    })

    # =========================================================================
    # CAPÍTULO 9: EVALUACIÓN DEL DESEMPEÑO
    # =========================================================================

    # 9.1 Seguimiento, medición, análisis y evaluación
    templates.append({
        'title': 'Revisión Trimestral de Indicadores de Desempeño del SGSI',
        'description': '''Seguimiento y evaluación de indicadores clave de desempeño del SGSI.

Indicadores a monitorizar:
- Eficacia de controles de seguridad
- Incidentes de seguridad detectados y resueltos
- Vulnerabilidades identificadas y corregidas
- Cumplimiento de objetivos de seguridad
- Tiempo de respuesta a incidentes
- Nivel de concienciación del personal
- Resultados de pruebas de controles

Requisito ISO 27001: 9.1 La organización debe evaluar desempeño de seguridad y eficacia del SGSI.''',
        'category': TaskCategory.REVISION_CONTROLES,
        'frequency': TaskFrequency.TRIMESTRAL,
        'priority': TaskPriority.ALTA,
        'iso_control': '9.1',
        'estimated_hours': 6.0,
        'notify_days_before': 7,
        'checklist_template': [
            {'description': 'Recopilar métricas del trimestre', 'completed': False},
            {'description': 'Analizar tendencias y desviaciones', 'completed': False},
            {'description': 'Comparar con objetivos establecidos', 'completed': False},
            {'description': 'Identificar áreas de mejora', 'completed': False},
            {'description': 'Generar dashboard de indicadores', 'completed': False},
            {'description': 'Presentar resultados a responsables', 'completed': False},
        ],
        'requires_evidence': True,
        'requires_approval': False,
    })

    # 9.2 Auditoría interna
    templates.append({
        'title': 'Auditoría Interna Semestral del SGSI',
        'description': '''Auditoría interna para verificar conformidad y eficacia del SGSI.

Alcance:
- Cumplimiento de requisitos ISO/IEC 27001
- Cumplimiento de requisitos propios del SGSI
- Implementación y mantenimiento eficaz
- Revisión de hallazgos de auditorías previas

El programa de auditoría debe considerar:
- Importancia de procesos
- Resultados de auditorías previas
- Objetividad e imparcialidad

Requisito ISO 27001: 9.2 Se deben llevar a cabo auditorías internas a intervalos planificados.''',
        'category': TaskCategory.AUDITORIA_INTERNA,
        'frequency': TaskFrequency.SEMESTRAL,
        'priority': TaskPriority.CRITICA,
        'iso_control': '9.2',
        'estimated_hours': 32.0,
        'notify_days_before': 21,
        'checklist_template': [
            {'description': 'Definir criterios y alcance de auditoría', 'completed': False},
            {'description': 'Seleccionar auditores competentes e imparciales', 'completed': False},
            {'description': 'Comunicar programa de auditoría', 'completed': False},
            {'description': 'Revisar documentación del SGSI', 'completed': False},
            {'description': 'Realizar entrevistas con responsables', 'completed': False},
            {'description': 'Verificar controles mediante pruebas', 'completed': False},
            {'description': 'Documentar hallazgos y no conformidades', 'completed': False},
            {'description': 'Reunión de cierre con auditados', 'completed': False},
            {'description': 'Emitir informe de auditoría', 'completed': False},
            {'description': 'Informar resultados a dirección pertinente', 'completed': False},
            {'description': 'Definir y hacer seguimiento de acciones correctivas', 'completed': False},
        ],
        'requires_evidence': True,
        'requires_approval': True,
    })

    # 9.3 Revisión por la dirección
    templates.append({
        'title': 'Revisión Semestral del SGSI por la Alta Dirección',
        'description': '''Revisión del SGSI por la alta dirección para asegurar conveniencia, adecuación y eficacia.

Entradas requeridas (9.3.2):
- Estado de acciones de revisiones previas
- Cambios en cuestiones externas/internas
- Cambios en necesidades de partes interesadas
- Retroalimentación sobre desempeño:
  * No conformidades y acciones correctivas
  * Resultados de seguimiento y medición
  * Resultados de auditorías
  * Cumplimiento de objetivos
- Comentarios de partes interesadas
- Resultados de evaluación de riesgos
- Estado del plan de tratamiento de riesgos
- Oportunidades de mejora continua

Resultados esperados (9.3.3):
- Decisiones sobre mejoras
- Necesidades de cambios en el SGSI

Requisito ISO 27001: 9.3 La alta dirección debe revisar el SGSI a intervalos planificados.''',
        'category': TaskCategory.REVISION_DIRECCION,
        'frequency': TaskFrequency.SEMESTRAL,
        'priority': TaskPriority.CRITICA,
        'iso_control': '9.3',
        'estimated_hours': 8.0,
        'notify_days_before': 30,
        'checklist_template': [
            {'description': 'Preparar informe ejecutivo del desempeño del SGSI', 'completed': False},
            {'description': 'Recopilar estado de acciones de revisión anterior', 'completed': False},
            {'description': 'Analizar cambios en contexto y partes interesadas', 'completed': False},
            {'description': 'Compilar resultados de auditorías y evaluaciones', 'completed': False},
            {'description': 'Evaluar cumplimiento de objetivos de seguridad', 'completed': False},
            {'description': 'Presentar resultados de evaluación de riesgos', 'completed': False},
            {'description': 'Identificar oportunidades de mejora', 'completed': False},
            {'description': 'Convocar reunión con alta dirección', 'completed': False},
            {'description': 'Presentar información de entrada', 'completed': False},
            {'description': 'Documentar decisiones y acuerdos', 'completed': False},
            {'description': 'Comunicar resultados a organización', 'completed': False},
        ],
        'requires_evidence': True,
        'requires_approval': True,
    })

    # =========================================================================
    # CAPÍTULO 10: MEJORA
    # =========================================================================

    # 10.2 No conformidad y acciones correctivas
    templates.append({
        'title': 'Revisión Trimestral de No Conformidades y Acciones Correctivas',
        'description': '''Seguimiento y cierre de no conformidades y eficacia de acciones correctivas.

Verificar:
- Acciones tomadas para controlar y corregir
- Evaluación de causas raíz
- Necesidad de acciones para evitar recurrencia
- Implementación de acciones necesarias
- Eficacia de acciones correctivas
- Cambios necesarios en el SGSI

Requisito ISO 27001: 10.2 Se debe reaccionar ante no conformidades, evaluarlas, implementar acciones y revisar su eficacia.''',
        'category': TaskCategory.REVISION_CONTROLES,
        'frequency': TaskFrequency.TRIMESTRAL,
        'priority': TaskPriority.ALTA,
        'iso_control': '10.2',
        'estimated_hours': 4.0,
        'notify_days_before': 7,
        'requires_evidence': True,
        'requires_approval': False,
    })

    # =========================================================================
    # ANEXO A - CONTROLES ORGANIZACIONALES
    # =========================================================================

    # A.5.9 Inventario de activos
    templates.append({
        'title': 'Actualización Mensual del Inventario de Activos',
        'description': '''Actualización del inventario de información y otros activos asociados.

Incluye:
- Hardware (servidores, equipos de usuario, dispositivos móviles, equipos de red)
- Software (aplicaciones, sistemas operativos, licencias)
- Información (bases de datos, documentos, registros)
- Servicios (cloud, proveedores externos)
- Personas (personal con roles críticos)
- Activos intangibles (reputación, imagen)

Información a mantener:
- Descripción del activo
- Propietario identificado
- Ubicación
- Clasificación de seguridad
- Valor para la organización

Control ISO 27001: A.5.9 - Inventario de información y otros activos asociados
Debe elaborarse y mantenerse un inventario incluyendo identificación de propietarios.''',
        'category': TaskCategory.ACTUALIZACION_INVENTARIOS,
        'frequency': TaskFrequency.MENSUAL,
        'priority': TaskPriority.MEDIA,
        'iso_control': 'A.5.9',
        'estimated_hours': 4.0,
        'notify_days_before': 3,
        'checklist_template': [
            {'description': 'Verificar altas de nuevos activos', 'completed': False},
            {'description': 'Registrar bajas de activos', 'completed': False},
            {'description': 'Actualizar ubicaciones', 'completed': False},
            {'description': 'Verificar propietarios asignados', 'completed': False},
            {'description': 'Revisar clasificación de activos', 'completed': False},
            {'description': 'Actualizar valoración de activos críticos', 'completed': False},
        ],
        'requires_evidence': True,
        'requires_approval': False,
    })

    # A.5.18 Derechos de acceso
    templates.append({
        'title': 'Revisión Trimestral de Derechos de Acceso',
        'description': '''Revisión de derechos de acceso a información y activos asociados.

Verificar:
- Aprobación de accesos
- Adecuación a funciones actuales
- Cuentas de usuario activas/inactivas
- Privilegios administrativos
- Accesos de terceros y proveedores
- Cumplimiento del principio de mínimo privilegio

Acciones:
- Aprovisionar nuevos accesos según política
- Modificar accesos por cambios de rol
- Eliminar accesos innecesarios
- Revocar accesos de personal cesado

Control ISO 27001: A.5.18 - Derechos de acceso
Los derechos deben aprovisionarse, revisarse, modificarse y eliminarse conforme a política y reglas de control de acceso.''',
        'category': TaskCategory.REVISION_ACCESOS,
        'frequency': TaskFrequency.TRIMESTRAL,
        'priority': TaskPriority.ALTA,
        'iso_control': 'A.5.18',
        'estimated_hours': 8.0,
        'notify_days_before': 7,
        'checklist_template': [
            {'description': 'Exportar listado completo de usuarios y permisos', 'completed': False},
            {'description': 'Revisar con responsables de cada departamento', 'completed': False},
            {'description': 'Identificar accesos excesivos o innecesarios', 'completed': False},
            {'description': 'Detectar cuentas inactivas o huérfanas', 'completed': False},
            {'description': 'Revisar especialmente cuentas privilegiadas', 'completed': False},
            {'description': 'Revocar accesos identificados como inadecuados', 'completed': False},
            {'description': 'Actualizar matriz de control de accesos', 'completed': False},
            {'description': 'Documentar cambios realizados', 'completed': False},
        ],
        'requires_evidence': True,
        'requires_approval': True,
    })

    # A.5.19 Seguridad de la información en las relaciones con proveedores
    templates.append({
        'title': 'Revisión Semestral de Seguridad en Proveedores',
        'description': '''Revisión de riesgos de seguridad asociados con uso de productos/servicios de proveedores.

Evaluar:
- Cumplimiento de acuerdos de seguridad
- Cumplimiento de SLAs
- Gestión de incidentes de seguridad
- Accesos de personal de proveedores
- Cambios en servicios prestados
- Medidas de seguridad implementadas
- Tratamiento de información de la organización

Control ISO 27001: A.5.19 y A.5.20 - Seguridad en relaciones con proveedores
Se deben identificar e implementar procesos para gestionar riesgos asociados con proveedores.''',
        'category': TaskCategory.REVISION_PROVEEDORES,
        'frequency': TaskFrequency.SEMESTRAL,
        'priority': TaskPriority.ALTA,
        'iso_control': 'A.5.19/A.5.20',
        'estimated_hours': 10.0,
        'notify_days_before': 14,
        'checklist_template': [
            {'description': 'Listar todos los proveedores críticos', 'completed': False},
            {'description': 'Revisar acuerdos de seguridad vigentes', 'completed': False},
            {'description': 'Evaluar cumplimiento de SLAs de seguridad', 'completed': False},
            {'description': 'Revisar incidentes de seguridad reportados', 'completed': False},
            {'description': 'Verificar controles de acceso de proveedores', 'completed': False},
            {'description': 'Evaluar gestión de cambios en servicios', 'completed': False},
            {'description': 'Solicitar evidencias de certificaciones', 'completed': False},
            {'description': 'Documentar hallazgos y plan de acción', 'completed': False},
        ],
        'requires_evidence': True,
        'requires_approval': True,
    })

    # A.5.24 a A.5.28 - Gestión de incidentes
    templates.append({
        'title': 'Revisión Trimestral de Gestión de Incidentes',
        'description': '''Análisis de eficacia del proceso de gestión de incidentes de seguridad.

Analizar:
- Incidentes registrados en el período
- Tiempos de detección y respuesta
- Eficacia de procedimientos de respuesta
- Lecciones aprendidas
- Mejoras en controles implementadas
- Recopilación de evidencias

Objetivos:
- Fortalecer capacidades de respuesta
- Mejorar detección temprana
- Optimizar procedimientos
- Actualizar planes de respuesta

Control ISO 27001: A.5.24-A.5.28 - Gestión de incidentes y A.5.27 - Aprendizaje
El conocimiento adquirido debe utilizarse para fortalecer controles.''',
        'category': TaskCategory.REVISION_INCIDENTES,
        'frequency': TaskFrequency.TRIMESTRAL,
        'priority': TaskPriority.ALTA,
        'iso_control': 'A.5.24-5.28',
        'estimated_hours': 6.0,
        'notify_days_before': 7,
        'checklist_template': [
            {'description': 'Recopilar todos los incidentes del trimestre', 'completed': False},
            {'description': 'Clasificar por tipo y severidad', 'completed': False},
            {'description': 'Analizar causas raíz de cada incidente', 'completed': False},
            {'description': 'Evaluar tiempos de detección y respuesta', 'completed': False},
            {'description': 'Identificar patrones o tendencias', 'completed': False},
            {'description': 'Verificar eficacia de acciones tomadas', 'completed': False},
            {'description': 'Proponer mejoras en procedimientos', 'completed': False},
            {'description': 'Actualizar plan de respuesta a incidentes', 'completed': False},
            {'description': 'Generar informe de lecciones aprendidas', 'completed': False},
        ],
        'requires_evidence': True,
        'requires_approval': False,
    })

    # A.5.29 y A.5.30 - Continuidad
    templates.append({
        'title': 'Prueba Anual del Plan de Continuidad de Negocio',
        'description': '''Prueba y validación del Plan de Continuidad de Negocio y Recuperación ante Desastres.

Actividades:
- Seleccionar escenario de prueba realista
- Ejecutar simulacro de desastre
- Activar procedimientos de continuidad
- Probar recuperación de sistemas críticos
- Verificar disponibilidad de recursos
- Medir tiempos de recuperación (RTO/RPO)
- Validar comunicaciones de crisis
- Probar ubicaciones alternativas si aplica

Control ISO 27001: A.5.29 y A.5.30 - Seguridad durante interrupción y continuidad TIC
La resiliencia debe planificarse, implementarse, mantenerse y probarse según objetivos de continuidad.''',
        'category': TaskCategory.CONTINUIDAD_NEGOCIO,
        'frequency': TaskFrequency.ANUAL,
        'priority': TaskPriority.CRITICA,
        'iso_control': 'A.5.29/A.5.30',
        'estimated_hours': 24.0,
        'notify_days_before': 30,
        'checklist_template': [
            {'description': 'Revisar y actualizar Plan de Continuidad', 'completed': False},
            {'description': 'Definir escenario de simulacro', 'completed': False},
            {'description': 'Notificar a todos los participantes', 'completed': False},
            {'description': 'Ejecutar simulacro de desastre', 'completed': False},
            {'description': 'Activar procedimientos de recuperación', 'completed': False},
            {'description': 'Probar sistemas de respaldo', 'completed': False},
            {'description': 'Medir tiempos de recuperación', 'completed': False},
            {'description': 'Verificar integridad de datos recuperados', 'completed': False},
            {'description': 'Documentar problemas identificados', 'completed': False},
            {'description': 'Actualizar plan según hallazgos', 'completed': False},
            {'description': 'Presentar resultados a dirección', 'completed': False},
        ],
        'requires_evidence': True,
        'requires_approval': True,
    })

    # A.5.31 - Requisitos legales
    templates.append({
        'title': 'Revisión Anual de Cumplimiento Legal y Regulatorio',
        'description': '''Revisión de cumplimiento de requisitos legales, regulatorios y contractuales.

Normativa aplicable:
- RGPD / Reglamento General de Protección de Datos
- LOPDGDD / Ley Orgánica de Protección de Datos
- Ley de Servicios de la Sociedad de la Información
- Normativa sectorial específica
- ENS / Esquema Nacional de Seguridad (si aplica)
- Directiva NIS2 / Ciberseguridad
- Código Penal (delitos informáticos)
- Propiedad intelectual
- Obligaciones contractuales con clientes

Actividades:
- Identificar normativa aplicable actualizada
- Verificar cumplimiento actual
- Identificar gaps de cumplimiento
- Planificar acciones correctivas

Control ISO 27001: A.5.31 - Identificación de requisitos legales, reglamentarios y contractuales
Los requisitos pertinentes deben identificarse, documentarse y mantenerse actualizados.''',
        'category': TaskCategory.REVISION_LEGAL,
        'frequency': TaskFrequency.ANUAL,
        'priority': TaskPriority.CRITICA,
        'iso_control': 'A.5.31',
        'estimated_hours': 16.0,
        'notify_days_before': 30,
        'checklist_template': [
            {'description': 'Identificar toda la normativa aplicable', 'completed': False},
            {'description': 'Revisar cambios legislativos del año', 'completed': False},
            {'description': 'Evaluar cumplimiento de RGPD/LOPDGDD', 'completed': False},
            {'description': 'Verificar cumplimiento de normativa sectorial', 'completed': False},
            {'description': 'Revisar obligaciones contractuales', 'completed': False},
            {'description': 'Identificar gaps de cumplimiento', 'completed': False},
            {'description': 'Elaborar plan de acción para gaps', 'completed': False},
            {'description': 'Actualizar matriz de cumplimiento legal', 'completed': False},
            {'description': 'Consultar con asesoría legal si necesario', 'completed': False},
        ],
        'requires_evidence': True,
        'requires_approval': True,
    })

    # A.5.35 - Revisión independiente
    templates.append({
        'title': 'Revisión Independiente Anual de la Seguridad',
        'description': '''Revisión independiente del enfoque de gestión de seguridad y su implementación.

Alcance de revisión:
- Procesos del SGSI
- Tecnologías de seguridad implementadas
- Competencia de personas clave
- Eficacia de controles
- Madurez del SGSI
- Comparación con mejores prácticas

La revisión debe ser realizada por:
- Auditor externo independiente
- Consultor especializado
- Personal interno independiente del área

Control ISO 27001: A.5.35 - Revisión independiente de la seguridad de la información
Debe revisarse de forma independiente a intervalos planificados o ante cambios significativos.''',
        'category': TaskCategory.AUDITORIA_INTERNA,
        'frequency': TaskFrequency.ANUAL,
        'priority': TaskPriority.ALTA,
        'iso_control': 'A.5.35',
        'estimated_hours': 16.0,
        'notify_days_before': 30,
        'requires_evidence': True,
        'requires_approval': True,
    })

    # =========================================================================
    # CONTROLES DE PERSONAS
    # =========================================================================

    # A.6.1 - Verificación de antecedentes
    templates.append({
        'title': 'Verificación Anual de Antecedentes de Personal Crítico',
        'description': '''Verificación de antecedentes de personal con acceso a información sensible.

Para personal con acceso a:
- Información clasificada
- Sistemas críticos
- Cuentas privilegiadas
- Datos personales sensibles

Verificaciones según legislación aplicable:
- Antecedentes penales
- Antecedentes laborales
- Referencias profesionales
- Verificación de titulaciones

Control ISO 27001: A.6.1 - Comprobación
Se debe llevar a cabo antes de unirse a la organización y de forma continua.''',
        'category': TaskCategory.OTROS,
        'frequency': TaskFrequency.ANUAL,
        'priority': TaskPriority.MEDIA,
        'iso_control': 'A.6.1',
        'estimated_hours': 4.0,
        'notify_days_before': 30,
        'requires_evidence': True,
        'requires_approval': False,
    })

    # =========================================================================
    # CONTROLES TECNOLÓGICOS
    # =========================================================================

    # A.8.7 - Protección contra malware
    templates.append({
        'title': 'Verificación Mensual de Protección contra Malware',
        'description': '''Verificación del correcto funcionamiento de la protección contra código malicioso.

Verificar:
- Actualización de firmas antimalware
- Estado de protección en endpoints
- Análisis programados ejecutados
- Detecciones y acciones tomadas
- Configuración de políticas
- Protección en servidores y estaciones
- Protección de correo electrónico
- Protección de navegación web

Control ISO 27001: A.8.7 - Controles contra el código malicioso
Debe implementarse protección respaldada por concienciación adecuada.''',
        'category': TaskCategory.MANTENIMIENTO_SEGURIDAD,
        'frequency': TaskFrequency.MENSUAL,
        'priority': TaskPriority.ALTA,
        'iso_control': 'A.8.7',
        'estimated_hours': 2.0,
        'notify_days_before': 3,
        'requires_evidence': True,
        'requires_approval': False,
    })

    # A.8.8 - Gestión de vulnerabilidades
    templates.append({
        'title': 'Escaneo Mensual de Vulnerabilidades',
        'description': '''Escaneo y gestión de vulnerabilidades técnicas de sistemas de información.

Actividades:
- Ejecutar escaneo automatizado de vulnerabilidades
- Revisar boletines de seguridad y CVEs
- Analizar parches de seguridad disponibles
- Evaluar criticidad de vulnerabilidades
- Priorizar según exposición al riesgo
- Planificar aplicación de parches
- Verificar aplicación efectiva
- Mantener sistemas actualizados

Control ISO 27001: A.8.8 - Gestión de vulnerabilidades técnicas
Se debe obtener información sobre vulnerabilidades, evaluar exposición y adoptar medidas adecuadas.''',
        'category': TaskCategory.GESTION_VULNERABILIDADES,
        'frequency': TaskFrequency.MENSUAL,
        'priority': TaskPriority.CRITICA,
        'iso_control': 'A.8.8',
        'estimated_hours': 8.0,
        'notify_days_before': 3,
        'checklist_template': [
            {'description': 'Ejecutar escaneo de vulnerabilidades en infraestructura', 'completed': False},
            {'description': 'Revisar boletines de seguridad del mes', 'completed': False},
            {'description': 'Analizar resultados del escaneo', 'completed': False},
            {'description': 'Clasificar vulnerabilidades por criticidad (CVSS)', 'completed': False},
            {'description': 'Evaluar aplicabilidad a entorno', 'completed': False},
            {'description': 'Planificar remediación de críticas (< 15 días)', 'completed': False},
            {'description': 'Aplicar parches y actualizaciones', 'completed': False},
            {'description': 'Verificar corrección mediante reescaneo', 'completed': False},
            {'description': 'Actualizar registro de vulnerabilidades', 'completed': False},
            {'description': 'Documentar excepciones justificadas', 'completed': False},
        ],
        'requires_evidence': True,
        'requires_approval': False,
    })

    # A.8.13 - Copias de seguridad
    templates.append({
        'title': 'Verificación Semanal de Copias de Seguridad',
        'description': '''Verificación semanal de ejecución correcta de copias de seguridad.

Verificar:
- Ejecución de backups programados (diarios, semanales)
- Estado de trabajos completados/fallidos
- Integridad de copias realizadas
- Espacio de almacenamiento disponible
- Retención según política
- Registro de operaciones
- Alertas generadas

Sistemas a verificar:
- Servidores críticos
- Bases de datos
- Correo electrónico
- Documentos compartidos
- Configuraciones de sistemas

Control ISO 27001: A.8.13 - Copias de seguridad de la información
Las copias deben mantenerse y probarse según política de copias de seguridad acordada.''',
        'category': TaskCategory.COPIAS_SEGURIDAD,
        'frequency': TaskFrequency.SEMANAL,
        'priority': TaskPriority.CRITICA,
        'iso_control': 'A.8.13',
        'estimated_hours': 1.5,
        'notify_days_before': 1,
        'checklist_template': [
            {'description': 'Verificar ejecución de backups diarios', 'completed': False},
            {'description': 'Revisar logs del sistema de backup', 'completed': False},
            {'description': 'Comprobar backups completados exitosamente', 'completed': False},
            {'description': 'Verificar integridad mediante checksums', 'completed': False},
            {'description': 'Comprobar espacio de almacenamiento', 'completed': False},
            {'description': 'Verificar replicación offsite si aplica', 'completed': False},
            {'description': 'Documentar cualquier error o incidencia', 'completed': False},
            {'description': 'Escalar problemas críticos inmediatamente', 'completed': False},
        ],
        'requires_evidence': True,
        'requires_approval': False,
    })

    # A.8.13 y A.8.14 - Pruebas de restauración
    templates.append({
        'title': 'Prueba Trimestral de Restauración de Copias de Seguridad',
        'description': '''Prueba de restauración para validar viabilidad de copias de seguridad.

Objetivos:
- Verificar que copias son restaurables
- Validar integridad de información restaurada
- Medir tiempos de recuperación (RTO)
- Verificar completitud de datos
- Probar procedimientos de recuperación
- Entrenar al personal en restauración

Pruebas rotativas en:
- Sistemas críticos (trimestre 1)
- Bases de datos (trimestre 2)
- Aplicaciones (trimestre 3)
- Ficheros y documentos (trimestre 4)

Control ISO 27001: A.8.13 y A.8.14 - Copias de seguridad y Redundancia
Las copias deben probarse periódicamente según política acordada.''',
        'category': TaskCategory.PRUEBAS_RECUPERACION,
        'frequency': TaskFrequency.TRIMESTRAL,
        'priority': TaskPriority.ALTA,
        'iso_control': 'A.8.13/A.8.14',
        'estimated_hours': 6.0,
        'notify_days_before': 7,
        'checklist_template': [
            {'description': 'Seleccionar sistema/datos para prueba del trimestre', 'completed': False},
            {'description': 'Preparar entorno de pruebas aislado', 'completed': False},
            {'description': 'Documentar estado inicial', 'completed': False},
            {'description': 'Iniciar cronómetro para medir RTO', 'completed': False},
            {'description': 'Ejecutar proceso de restauración', 'completed': False},
            {'description': 'Verificar integridad de datos restaurados', 'completed': False},
            {'description': 'Comprobar funcionalidad de aplicaciones', 'completed': False},
            {'description': 'Documentar tiempo de recuperación', 'completed': False},
            {'description': 'Identificar problemas o mejoras', 'completed': False},
            {'description': 'Actualizar procedimientos si necesario', 'completed': False},
        ],
        'requires_evidence': True,
        'requires_approval': False,
    })

    # A.8.15 - Registro de eventos
    templates.append({
        'title': 'Revisión Semanal de Registros de Eventos de Seguridad',
        'description': '''Revisión de registros de actividades, excepciones y eventos de seguridad.

Eventos a revisar:
- Intentos de acceso fallidos
- Cambios en cuentas privilegiadas
- Accesos a información sensible
- Modificaciones de configuración
- Detecciones de antimalware
- Alertas de sistemas de seguridad
- Errores de aplicaciones críticas

Control ISO 27001: A.8.15 y A.8.16 - Registros de eventos y Seguimiento de actividades
Los registros deben generarse, protegerse, almacenarse y analizarse. Los sistemas deben monitorizarse para comportamientos anómalos.''',
        'category': TaskCategory.MANTENIMIENTO_SEGURIDAD,
        'frequency': TaskFrequency.SEMANAL,
        'priority': TaskPriority.ALTA,
        'iso_control': 'A.8.15/A.8.16',
        'estimated_hours': 3.0,
        'notify_days_before': 1,
        'requires_evidence': True,
        'requires_approval': False,
    })

    # A.8.19 - Instalación de software
    templates.append({
        'title': 'Revisión Mensual de Software Instalado',
        'description': '''Revisión de software instalado en sistemas productivos.

Verificar:
- Software autorizado vs instalado
- Versiones de software crítico
- Licencias válidas y vigentes
- Software sin soporte o EOL
- Actualizaciones pendientes
- Software no autorizado
- Cambios no documentados

Control ISO 27001: A.8.19 - Instalación del software en sistemas en producción
Deben implementarse procedimientos para gestionar de forma segura la instalación de software.''',
        'category': TaskCategory.MANTENIMIENTO_SEGURIDAD,
        'frequency': TaskFrequency.MENSUAL,
        'priority': TaskPriority.MEDIA,
        'iso_control': 'A.8.19',
        'estimated_hours': 4.0,
        'notify_days_before': 3,
        'requires_evidence': True,
        'requires_approval': False,
    })

    # A.8.32 - Gestión de cambios
    templates.append({
        'title': 'Revisión Quincenal del Proceso de Gestión de Cambios',
        'description': '''Revisión de cambios realizados en instalaciones y sistemas de información.

Verificar:
- Cambios solicitados y aprobados
- Cambios implementados
- Pruebas realizadas
- Documentación actualizada
- Cambios de emergencia justificados
- Rollback plans disponibles
- Comunicación de cambios

Control ISO 27001: A.8.32 - Gestión de cambios
Los cambios deben estar sujetos a procedimientos de gestión de cambios.''',
        'category': TaskCategory.MANTENIMIENTO_SEGURIDAD,
        'frequency': TaskFrequency.QUINCENAL,
        'priority': TaskPriority.MEDIA,
        'iso_control': 'A.8.32',
        'estimated_hours': 2.0,
        'notify_days_before': 2,
        'requires_evidence': True,
        'requires_approval': False,
    })

    # =========================================================================
    # CONTROLES FÍSICOS
    # =========================================================================

    # A.7.4 - Monitorización de seguridad física
    templates.append({
        'title': 'Revisión Mensual de Seguridad Física',
        'description': '''Revisión de controles de seguridad física de instalaciones.

Verificar:
- Funcionamiento de sistemas de control de acceso
- Registros de accesos a áreas seguras
- Funcionamiento de cámaras de seguridad
- Integridad de perímetros de seguridad
- Condiciones ambientales (temperatura, humedad)
- Sistemas de detección de incendios
- Iluminación de seguridad
- Alarmas operativas

Control ISO 27001: A.7.4 - Monitorización de la seguridad física
Las instalaciones deben monitorizarse continuamente para detectar acceso físico no autorizado.''',
        'category': TaskCategory.MANTENIMIENTO_SEGURIDAD,
        'frequency': TaskFrequency.MENSUAL,
        'priority': TaskPriority.MEDIA,
        'iso_control': 'A.7.4',
        'estimated_hours': 3.0,
        'notify_days_before': 3,
        'requires_evidence': True,
        'requires_approval': False,
    })

    return templates


def init_task_templates():
    """Inicializa las plantillas de tareas ISO 27001 en nueva instalación"""
    # Importar dependencias de Flask/SQLAlchemy solo cuando se ejecuta standalone
    from application import app
    from models import db, Role, User
    from app.models.task import TaskTemplate, TaskFrequency, TaskPriority, TaskCategory

    with app.app_context():
        # Verificar si ya existen plantillas
        existing_count = TaskTemplate.query.count()
        if existing_count > 0:
            print(f"\nℹ️  Ya existen {existing_count} plantillas de tareas en el sistema.")
            response = input("¿Desea agregar las nuevas plantillas ISO 27001? (s/N): ")
            if response.lower() != 's':
                print("Operación cancelada.")
                return 0

        print("\n" + "=" * 80)
        print("  INICIALIZACIÓN DE PLANTILLAS DE TAREAS ISO/IEC 27001:2023")
        print("=" * 80)
        print("\nEste script creará un conjunto completo de plantillas de tareas periódicas")
        print("recomendadas por la norma ISO/IEC 27001:2023 para el SGSI.\n")

        # Obtener roles del sistema
        print("📋 Cargando roles del sistema...")
        role_ciso = Role.query.filter_by(name='ciso').first()
        role_admin = Role.query.filter_by(name='admin').first()
        role_auditor = Role.query.filter_by(name='auditor').first()

        if not role_ciso:
            print("⚠️  Advertencia: Rol 'CISO' no encontrado.")
        if not role_auditor:
            print("⚠️  Advertencia: Rol 'Auditor Interno' no encontrado.")

        # Obtener plantillas
        print("\n🔨 Generando plantillas de tareas ISO 27001...")
        templates_data = get_task_templates_iso27001()

        print(f"📊 Total de plantillas a crear: {len(templates_data)}\n")

        # Asignar roles predeterminados según categoría
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

        # Crear plantillas
        created_count = 0
        skipped_count = 0
        error_count = 0

        for idx, template_data in enumerate(templates_data, 1):
            try:
                # Verificar si ya existe
                existing = TaskTemplate.query.filter_by(
                    title=template_data['title']
                ).first()

                if existing:
                    print(f"⏭️  [{idx:2d}/{len(templates_data)}] Saltando: '{template_data['title']}' (ya existe)")
                    skipped_count += 1
                    continue

                # Asignar rol predeterminado si no se especificó
                if 'default_role_id' not in template_data or template_data['default_role_id'] is None:
                    template_data['default_role_id'] = role_mappings.get(template_data['category'])

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
                    created_by_id=1,  # Usuario admin
                    created_at=datetime.utcnow()
                )

                db.session.add(template)
                created_count += 1

                # Mostrar progreso
                category_emoji = {
                    TaskCategory.AUDITORIA_INTERNA: '🔍',
                    TaskCategory.EVALUACION_RIESGOS: '⚠️',
                    TaskCategory.REVISION_POLITICAS: '📜',
                    TaskCategory.REVISION_DIRECCION: '👔',
                    TaskCategory.FORMACION_CONCIENCIACION: '🎓',
                    TaskCategory.MANTENIMIENTO_SEGURIDAD: '🔧',
                    TaskCategory.COPIAS_SEGURIDAD: '💾',
                    TaskCategory.REVISION_ACCESOS: '🔐',
                    TaskCategory.ACTUALIZACION_INVENTARIOS: '📦',
                    TaskCategory.REVISION_PROVEEDORES: '🤝',
                    TaskCategory.GESTION_VULNERABILIDADES: '🛡️',
                    TaskCategory.REVISION_INCIDENTES: '🚨',
                    TaskCategory.CONTINUIDAD_NEGOCIO: '🔄',
                    TaskCategory.REVISION_LEGAL: '⚖️',
                    TaskCategory.REVISION_CONTROLES: '✅',
                    TaskCategory.PRUEBAS_RECUPERACION: '🔁',
                    TaskCategory.OTROS: '📋'
                }.get(template_data['category'], '📋')

                print(f"✅ [{idx:2d}/{len(templates_data)}] {category_emoji} Creada: '{template_data['title'][:60]}...'")

            except Exception as e:
                error_count += 1
                print(f"❌ [{idx:2d}/{len(templates_data)}] Error creando '{template_data['title']}': {str(e)}")

        # Guardar cambios
        try:
            db.session.commit()
            print("\n💾 Cambios guardados en base de datos correctamente.")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error al guardar cambios: {str(e)}")
            return 1

        # Resumen final
        print("\n" + "=" * 80)
        print("  RESUMEN DE INICIALIZACIÓN")
        print("=" * 80)
        print(f"\n✅ Plantillas creadas exitosamente: {created_count}")
        print(f"⏭️  Plantillas ya existentes:        {skipped_count}")
        if error_count > 0:
            print(f"❌ Errores encontrados:             {error_count}")
        print(f"\n📊 Total de plantillas en sistema: {TaskTemplate.query.count()}")

        print("\n" + "-" * 80)
        print("📌 PRÓXIMOS PASOS:")
        print("-" * 80)
        print("1. Accede a http://localhost/tareas/templates para ver las plantillas")
        print("2. Genera las primeras tareas desde las plantillas activas")
        print("3. Asigna responsables a cada tipo de tarea")
        print("4. Configura notificaciones por correo electrónico")
        print("5. Revisa y ajusta frecuencias según necesidades de tu organización")
        print("\n" + "=" * 80)

        return 0


def main():
    """Función principal"""
    try:
        result = init_task_templates()
        if result == 0:
            print("\n🎉 ¡Inicialización completada exitosamente!\n")
        return result
    except Exception as e:
        print(f"\n❌ Error fatal durante la inicialización:")
        print(f"   {str(e)}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
