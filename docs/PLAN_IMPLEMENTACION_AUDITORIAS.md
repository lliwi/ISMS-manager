# Plan de Implementación del Módulo de Auditorías ISO 27001

**Proyecto:** ISMS Manager
**Módulo:** Gestión de Auditorías
**Versión:** 1.0
**Fecha:** 2025-10-17
**Normas aplicables:** ISO/IEC 27001:2023, ISO 19011:2018

---

## 📋 RESUMEN EJECUTIVO

El módulo de auditorías ya tiene **una base de datos sólida y bien estructurada**. Los modelos existentes en `app/models/audit.py` cubren los requisitos de ISO 27001:2023 cláusulas **9.2 (Auditoría interna)** y **9.3 (Revisión por la dirección)**.

**Estado actual:** 10% completado (solo modelos de datos)
**Falta:** Implementar controladores, servicios, vistas y flujos de trabajo

---

## 🎯 REQUISITOS SEGÚN ISO 27001:2023

### Cláusula 9.2 - Auditoría Interna

#### 9.2.1 Consideraciones Generales
La organización debe realizar auditorías internas a intervalos planificados para verificar si el SGSI:
- ✅ Cumple con los requisitos propios de la organización
- ✅ Cumple con los requisitos de ISO 27001
- ✅ Está implementado y mantenido eficazmente

#### 9.2.2 Programa de Auditoría Interna
Debe incluir:
- **Frecuencia** de auditorías
- **Métodos** de auditoría
- **Responsabilidades** claras
- **Requisitos de planificación**
- **Elaboración de informes**
- **Consideraciones:** importancia de procesos y resultados de auditorías previas
- **Criterios y alcance** por auditoría
- **Selección de auditores** (objetividad e imparcialidad)
- **Reporte a la dirección** pertinente

### Requisitos Clave de la Norma

#### Documentación Requerida (Cláusula 7.5)
- ✅ Programa de auditoría interna
- ✅ Plan de auditoría por cada auditoría
- ✅ Informes de auditoría
- ✅ Evidencias de auditoría
- ✅ Registros de hallazgos
- ✅ Planes de acción correctiva

#### Información Documentada (Cláusula 9.2.2)
- ✅ Evidencia de implementación del programa de auditoría
- ✅ Resultados de las auditorías

---

## 🏗️ ARQUITECTURA DEL MÓDULO

### 1. COMPONENTES PRINCIPALES

```
auditorías/
├── Programa Anual de Auditorías
├── Planificación de Auditorías Individuales
├── Ejecución de Auditorías
├── Gestión de Hallazgos
├── Acciones Correctivas
├── Seguimiento y Cierre
└── Informes y Métricas
```

### 2. FLUJOS DE TRABAJO CLAVE

#### A. Ciclo de Vida del Programa Anual
```
BORRADOR → REVISIÓN → APROBACIÓN → EN EJECUCIÓN → COMPLETADO
```

#### B. Ciclo de Vida de Auditoría Individual
```
PLANIFICADA → NOTIFICADA → PREPARACIÓN → EJECUCIÓN →
ELABORACIÓN INFORME → COMPLETADA → SEGUIMIENTO → CERRADA
```

#### C. Ciclo de Vida de Hallazgos
```
ABIERTO → PLAN DE ACCIÓN → APROBADO → EN TRATAMIENTO →
RESUELTO → VERIFICADO → CERRADO
```

---

## 📅 PLAN DE IMPLEMENTACIÓN DETALLADO

### FASE 1: Servicios y Lógica de Negocio 🔧

#### 1.1 Servicio de Programas de Auditoría
**Archivo:** `app/services/audit_program_service.py`

**Funciones principales:**
```python
class AuditProgramService:
    - create_program(year, title, description, scope, objectives)
    - approve_program(program_id, approver_id)
    - calculate_coverage()  # Cobertura de controles ISO 27001
    - propose_schedule()    # Calendario basado en riesgos
    - get_program_metrics(program_id)
    - update_program_status(program_id, status)
    - get_completion_rate(program_id)
```

**Reglas de negocio:**
- ✅ Un programa activo por año fiscal
- ✅ Debe cubrir todos los controles del Anexo A aplicables
- ✅ Frecuencia basada en criticidad (controles críticos: semestral, otros: anual)
- ✅ Solo usuarios con rol CISO o Admin pueden aprobar programas
- ✅ Cobertura mínima requerida: 80% de controles aplicables

#### 1.2 Servicio de Auditorías
**Archivo:** `app/services/audit_service.py`

**Funciones principales:**
```python
class AuditService:
    - create_audit(audit_data, program_id=None)
    - generate_audit_code()  # AUD-YYYY-###
    - assign_team(audit_id, team_members)
    - validate_independence(auditor_id, area)
    - update_status(audit_id, new_status, user_id)
    - upload_document(audit_id, document_type, file)
    - calculate_conformity_rate(audit_id)
    - generate_audit_report(audit_id)
    - notify_auditees(audit_id)
    - schedule_followup(audit_id, followup_date)
```

**Transiciones de estado permitidas:**
```python
STATE_TRANSITIONS = {
    'PLANNED': ['NOTIFIED', 'CANCELLED'],
    'NOTIFIED': ['PREPARATION', 'CANCELLED'],
    'PREPARATION': ['IN_PROGRESS', 'CANCELLED'],
    'IN_PROGRESS': ['REPORTING'],
    'REPORTING': ['COMPLETED'],
    'COMPLETED': ['CLOSED'],
    'CLOSED': [],
    'CANCELLED': []
}
```

**Reglas de negocio:**
- ✅ Auditor líder debe tener calificación válida
- ✅ Equipo auditor debe ser independiente del área auditada
- ✅ Plan de auditoría obligatorio antes de iniciar ejecución
- ✅ Informe final obligatorio antes de completar auditoría
- ✅ Todos los hallazgos mayores deben tener plan de acción
- ✅ Notificar con al menos 7 días de antelación

#### 1.3 Servicio de Hallazgos
**Archivo:** `app/services/finding_service.py`

**Funciones principales:**
```python
class FindingService:
    - create_finding(audit_id, finding_data)
    - generate_finding_code(audit_code)  # HAL-YYYY-###-##
    - classify_finding(finding_type)
    - assign_responsible(finding_id, user_id)
    - perform_root_cause_analysis(finding_id, analysis)
    - link_to_control(finding_id, control_id)
    - update_status(finding_id, new_status)
    - calculate_risk_level(finding)
    - set_closure_deadline(finding_type)
    - notify_responsible(finding_id)
```

**Plazos de cierre por severidad:**
```python
CLOSURE_DEADLINES = {
    'MAJOR_NC': 30,              # días
    'MINOR_NC': 60,              # días
    'OBSERVATION': 90,            # días
    'OPPORTUNITY_IMPROVEMENT': 120  # días
}
```

**Reglas de negocio:**
- ✅ No conformidades mayores requieren acción inmediata (< 24h)
- ✅ Responsable debe pertenecer al área afectada
- ✅ Causa raíz obligatoria para todas las NCs
- ✅ Evidencia documentada obligatoria
- ✅ Vinculación con control ISO 27001 cuando aplique
- ✅ Notificación automática al responsable y su jefe directo

#### 1.4 Servicio de Acciones Correctivas
**Archivo:** `app/services/corrective_action_service.py`

**Funciones principales:**
```python
class CorrectiveActionService:
    - create_action(finding_id, action_data)
    - generate_action_code()  # AC-YYYY-###
    - assign_resources(action_id, resources)
    - update_progress(action_id, percentage, notes)
    - complete_action(action_id, completion_date)
    - verify_effectiveness(action_id, verified_by, notes)
    - reopen_action(action_id, reason)
    - calculate_cost(action_id)
    - track_delays(action_id)
```

**Estados de acción:**
```python
ACTION_STATUS = {
    'PLANNED': 'Planificada',
    'IN_PROGRESS': 'En progreso',
    'COMPLETED': 'Completada',
    'VERIFIED': 'Verificada',
    'REJECTED': 'Rechazada',
    'CANCELLED': 'Cancelada'
}
```

**Reglas de negocio:**
- ✅ Plan de acción debe aprobarse antes de iniciar
- ✅ Verificador debe ser diferente al responsable de implementación
- ✅ Eficacia debe verificarse después de 3 meses de implementación
- ✅ Cierre requiere aprobación del auditor líder
- ✅ Acciones vencidas generan alerta automática
- ✅ Reapertura requiere justificación documentada

---

### FASE 2: Controladores y Rutas 🛣️

#### 2.1 Controlador Principal de Auditorías
**Archivo:** `app/blueprints/audits.py`

**Rutas implementadas:**

```python
# ===== DASHBOARD =====
GET  /auditorias/                          → index()
# Dashboard principal con KPIs, calendario y alertas

# ===== PROGRAMAS DE AUDITORÍA =====
GET  /auditorias/programas                 → list_programs()
GET  /auditorias/programas/nuevo           → create_program_form()
POST /auditorias/programas                 → create_program()
GET  /auditorias/programas/<id>            → view_program()
GET  /auditorias/programas/<id>/editar     → edit_program_form()
PUT  /auditorias/programas/<id>            → update_program()
POST /auditorias/programas/<id>/aprobar    → approve_program()
GET  /auditorias/programas/<id>/calendario → program_calendar()
GET  /auditorias/programas/<id>/metricas   → program_metrics()

# ===== AUDITORÍAS =====
GET  /auditorias/lista                     → list_audits()
GET  /auditorias/nueva                     → create_audit_form()
POST /auditorias                           → create_audit()
GET  /auditorias/<id>                      → view_audit()
GET  /auditorias/<id>/editar               → edit_audit_form()
PUT  /auditorias/<id>                      → update_audit()
DELETE /auditorias/<id>                    → delete_audit()

# Transiciones de estado
POST /auditorias/<id>/notificar            → notify_audit()
POST /auditorias/<id>/iniciar              → start_audit()
POST /auditorias/<id>/completar            → complete_audit()
POST /auditorias/<id>/cerrar               → close_audit()
POST /auditorias/<id>/cancelar             → cancel_audit()

# ===== EQUIPO AUDITOR =====
GET  /auditorias/<id>/equipo               → view_team()
POST /auditorias/<id>/equipo               → add_team_member()
PUT  /auditorias/<id>/equipo/<member_id>   → update_team_member()
DELETE /auditorias/<id>/equipo/<member_id> → remove_team_member()
GET  /auditorias/<id>/equipo/<member_id>/independencia → check_independence()

# ===== HALLAZGOS =====
GET  /auditorias/<id>/hallazgos            → list_findings()
POST /auditorias/<id>/hallazgos            → create_finding()
GET  /hallazgos/<id>                       → view_finding()
PUT  /hallazgos/<id>                       → update_finding()
DELETE /hallazgos/<id>                     → delete_finding()
POST /hallazgos/<id>/estado                → update_finding_status()

# ===== ACCIONES CORRECTIVAS =====
GET  /hallazgos/<id>/acciones              → list_actions()
POST /hallazgos/<id>/acciones              → create_action()
GET  /acciones/<id>                        → view_action()
PUT  /acciones/<id>                        → update_action()
POST /acciones/<id>/progreso               → update_progress()
POST /acciones/<id>/completar              → complete_action()
POST /acciones/<id>/verificar              → verify_action()
POST /acciones/<id>/reabrir                → reopen_action()

# ===== DOCUMENTOS =====
GET  /auditorias/<id>/documentos           → list_documents()
POST /auditorias/<id>/documentos           → upload_document()
GET  /auditorias/<id>/documentos/<doc_id>  → view_document()
GET  /auditorias/<id>/documentos/<doc_id>/download → download_document()
DELETE /auditorias/<id>/documentos/<doc_id> → delete_document()

# ===== EVIDENCIAS =====
GET  /auditorias/<id>/evidencias           → list_evidences()
POST /auditorias/<id>/evidencias           → upload_evidence()
GET  /evidencias/<id>                      → view_evidence()
DELETE /evidencias/<id>                    → delete_evidence()

# ===== LISTAS DE VERIFICACIÓN =====
GET  /auditorias/<id>/checklist            → view_checklist()
POST /auditorias/<id>/checklist            → save_checklist()
GET  /auditorias/<id>/checklist/progreso   → checklist_progress()

# Plantillas de checklist
GET  /auditorias/checklist-templates       → list_templates()
POST /auditorias/checklist-templates       → create_template()
GET  /auditorias/checklist-templates/<id>  → view_template()
PUT  /auditorias/checklist-templates/<id>  → update_template()

# ===== INFORMES =====
GET  /auditorias/<id>/informe              → view_report()
POST /auditorias/<id>/informe/generar      → generate_report()
POST /auditorias/<id>/informe/publicar     → publish_report()
GET  /auditorias/<id>/informe/pdf          → download_report_pdf()

# ===== MÉTRICAS Y KPIs =====
GET  /auditorias/metricas                  → audit_metrics()
GET  /auditorias/dashboard                 → audit_dashboard()
GET  /auditorias/estadisticas              → audit_statistics()
GET  /auditorias/tendencias                → audit_trends()

# ===== CALENDARIO =====
GET  /auditorias/calendario                → audit_calendar()
GET  /auditorias/calendario/eventos        → calendar_events()  # JSON para FullCalendar

# ===== EXPORTACIÓN =====
GET  /auditorias/exportar                  → export_audits()
GET  /hallazgos/exportar                   → export_findings()
GET  /auditorias/<id>/exportar-completo    → export_audit_complete()

# ===== AUDITORES =====
GET  /auditorias/auditores                 → list_auditors()
GET  /auditorias/auditores/<id>            → view_auditor()
GET  /auditorias/auditores/<id>/calificaciones → auditor_qualifications()
POST /auditorias/auditores/<id>/calificaciones → add_qualification()
```

**Permisos por rol:**
```python
PERMISSIONS = {
    'ADMIN': ['*'],  # Todos los permisos
    'CISO': [
        'view_all', 'create_program', 'approve_program',
        'view_reports', 'export_data', 'manage_auditors'
    ],
    'LEAD_AUDITOR': [
        'create_audit', 'manage_audit', 'create_finding',
        'approve_actions', 'close_audit', 'generate_report'
    ],
    'AUDITOR': [
        'view_assigned_audits', 'create_finding',
        'upload_evidence', 'fill_checklist'
    ],
    'AREA_MANAGER': [
        'view_area_audits', 'create_action',
        'update_action_progress'
    ],
    'USER': ['view_own_findings', 'update_assigned_actions']
}
```

---

### FASE 3: Vistas y Templates 🎨

#### 3.1 Estructura de Plantillas

```
templates/audits/
├── index.html                      # Dashboard principal
│
├── programs/
│   ├── list.html                   # Lista de programas
│   ├── form.html                   # Crear/editar programa
│   ├── view.html                   # Detalle del programa
│   ├── calendar.html               # Vista calendario anual
│   └── metrics.html                # Métricas del programa
│
├── audits/
│   ├── list.html                   # Lista de auditorías con filtros
│   ├── form.html                   # Crear/editar auditoría
│   ├── view.html                   # Detalle auditoría (tabs)
│   │   ├── tab_info.html           # Información general
│   │   ├── tab_team.html           # Equipo auditor
│   │   ├── tab_plan.html           # Plan de auditoría
│   │   ├── tab_execution.html      # Ejecución y evidencias
│   │   ├── tab_findings.html       # Hallazgos
│   │   ├── tab_documents.html      # Documentos
│   │   └── tab_report.html         # Informe
│   ├── calendar.html               # Calendario auditorías
│   └── timeline.html               # Timeline de auditoría
│
├── findings/
│   ├── list.html                   # Lista hallazgos con filtros
│   ├── form.html                   # Crear/editar hallazgo
│   ├── view.html                   # Detalle hallazgo completo
│   ├── matrix.html                 # Matriz de hallazgos
│   └── widgets/
│       ├── finding_card.html       # Card de hallazgo
│       ├── finding_status.html     # Badge de estado
│       └── finding_timeline.html   # Timeline de estados
│
├── actions/
│   ├── list.html                   # Lista de acciones
│   ├── form.html                   # Crear plan de acción
│   ├── view.html                   # Detalle acción
│   ├── progress_form.html          # Actualizar progreso
│   └── verification_form.html      # Verificación eficacia
│
├── checklists/
│   ├── templates_list.html         # Lista de plantillas
│   ├── template_form.html          # Crear/editar plantilla
│   ├── execution_form.html         # Ejecutar checklist
│   └── iso27001_templates/
│       ├── organizational.html     # Controles organizacionales (5)
│       ├── people.html             # Controles de personas (6)
│       ├── physical.html           # Controles físicos (7)
│       └── technological.html      # Controles tecnológicos (8)
│
├── reports/
│   ├── audit_report.html           # Informe de auditoría
│   ├── program_report.html         # Informe del programa
│   ├── metrics_dashboard.html      # KPIs y métricas
│   ├── findings_report.html        # Informe de hallazgos
│   ├── coverage_report.html        # Cobertura ISO 27001
│   └── trends_report.html          # Tendencias y evolución
│
├── auditors/
│   ├── list.html                   # Lista de auditores
│   ├── profile.html                # Perfil del auditor
│   └── qualifications.html         # Calificaciones
│
└── partials/
    ├── audit_timeline.html         # Timeline de auditoría
    ├── findings_summary.html       # Resumen de hallazgos
    ├── action_progress.html        # Progreso de acciones
    ├── iso_controls_coverage.html  # Cobertura controles
    ├── kpi_card.html               # Card de KPI
    ├── status_badge.html           # Badge de estado
    ├── priority_badge.html         # Badge de prioridad
    └── audit_card.html             # Card de auditoría
```

#### 3.2 Componentes Visuales Clave

##### Dashboard Principal (index.html)

**Secciones:**
```html
<!-- KPIs Principales -->
<div class="row">
    <div class="col-md-3">
        <div class="kpi-card">
            <i class="fas fa-clipboard-list"></i>
            <h3>{{ audits_planned }}</h3>
            <p>Auditorías Planificadas</p>
        </div>
    </div>
    <div class="col-md-3">
        <div class="kpi-card">
            <i class="fas fa-check-circle"></i>
            <h3>{{ audits_completed }}</h3>
            <p>Auditorías Completadas</p>
        </div>
    </div>
    <div class="col-md-3">
        <div class="kpi-card">
            <i class="fas fa-exclamation-triangle"></i>
            <h3>{{ findings_open }}</h3>
            <p>Hallazgos Abiertos</p>
        </div>
    </div>
    <div class="col-md-3">
        <div class="kpi-card">
            <i class="fas fa-percentage"></i>
            <h3>{{ conformity_rate }}%</h3>
            <p>Tasa de Conformidad</p>
        </div>
    </div>
</div>

<!-- Gráficos -->
<div class="row">
    <div class="col-md-6">
        <canvas id="findingsByTypeChart"></canvas>
    </div>
    <div class="col-md-6">
        <canvas id="trendChart"></canvas>
    </div>
</div>

<!-- Calendario -->
<div class="row">
    <div class="col-md-12">
        <div id="auditCalendar"></div>
    </div>
</div>

<!-- Alertas y Notificaciones -->
<div class="row">
    <div class="col-md-6">
        <h4>Auditorías Próximas</h4>
        <ul class="audit-list">
            <!-- Lista de auditorías -->
        </ul>
    </div>
    <div class="col-md-6">
        <h4>Hallazgos Críticos</h4>
        <ul class="findings-list">
            <!-- Lista de hallazgos -->
        </ul>
    </div>
</div>
```

##### Vista de Auditoría (audits/view.html)

**Estructura con tabs:**
```html
<div class="audit-header">
    <h2>{{ audit.audit_code }} - {{ audit.title }}</h2>
    <span class="badge badge-{{ audit.status.value }}">
        {{ audit.status.value }}
    </span>
</div>

<ul class="nav nav-tabs" role="tablist">
    <li class="nav-item">
        <a class="nav-link active" data-toggle="tab" href="#info">
            <i class="fas fa-info-circle"></i> Información
        </a>
    </li>
    <li class="nav-item">
        <a class="nav-link" data-toggle="tab" href="#team">
            <i class="fas fa-users"></i> Equipo
            <span class="badge">{{ audit.team_members|length }}</span>
        </a>
    </li>
    <li class="nav-item">
        <a class="nav-link" data-toggle="tab" href="#findings">
            <i class="fas fa-search"></i> Hallazgos
            <span class="badge badge-danger">{{ audit.total_findings }}</span>
        </a>
    </li>
    <li class="nav-item">
        <a class="nav-link" data-toggle="tab" href="#documents">
            <i class="fas fa-file-alt"></i> Documentos
        </a>
    </li>
    <li class="nav-item">
        <a class="nav-link" data-toggle="tab" href="#report">
            <i class="fas fa-file-pdf"></i> Informe
        </a>
    </li>
</ul>

<div class="tab-content">
    <!-- Contenido de cada tab -->
</div>
```

##### Vista de Hallazgo (findings/view.html)

**Componentes:**
```html
<!-- Cabecera del hallazgo -->
<div class="finding-header">
    <h3>{{ finding.finding_code }}</h3>
    <span class="badge badge-{{ finding.finding_type.value }}">
        {{ finding.finding_type.value }}
    </span>
    <span class="badge badge-{{ finding.status.value }}">
        {{ finding.status.value }}
    </span>
</div>

<!-- Información principal -->
<div class="finding-info">
    <h4>{{ finding.title }}</h4>
    <p>{{ finding.description }}</p>

    <!-- Control ISO 27001 -->
    <div class="control-reference">
        <strong>Control ISO 27001:</strong>
        <a href="{{ url_for('controls.view', id=finding.affected_control) }}">
            {{ finding.affected_control }}
        </a>
    </div>

    <!-- Evidencia -->
    <div class="evidence">
        <h5>Evidencia</h5>
        <p>{{ finding.evidence }}</p>
    </div>

    <!-- Análisis de causa raíz -->
    <div class="root-cause">
        <h5>Análisis de Causa Raíz</h5>
        <p>{{ finding.root_cause }}</p>
    </div>
</div>

<!-- Acciones correctivas -->
<div class="corrective-actions">
    <h5>Plan de Acción Correctiva</h5>
    {% for action in finding.corrective_actions %}
        <!-- Card de acción -->
    {% endfor %}
</div>

<!-- Timeline -->
<div class="timeline">
    <h5>Timeline de Seguimiento</h5>
    <!-- Eventos del hallazgo -->
</div>
```

#### 3.3 Librerías JavaScript Requeridas

```javascript
// Calendario
- FullCalendar v5
- Moment.js

// Gráficos
- Chart.js
- ApexCharts (alternativa)

// Tablas
- DataTables
- Export buttons (PDF, Excel, CSV)

// UI
- Bootstrap 5
- FontAwesome
- Select2 (selects mejorados)
- Flatpickr (date picker)
- Dropzone.js (upload de archivos)

// Validación
- jQuery Validation

// Editores
- TinyMCE o CKEditor (para informes)
- SimpleMDE (Markdown)

// Timeline
- Vis.js Timeline
```

---

### FASE 4: Integraciones 🔗

#### 4.1 Integración con Otros Módulos

##### Con SOA (Statement of Applicability)

**Funcionalidades:**
```python
# Vincular auditorías con controles del Anexo A
- Seleccionar controles a auditar desde SOA
- Verificar estado de implementación de controles
- Generar hallazgos automáticos si control no implementado
- Actualizar estado de control post-auditoría
- Calcular % de cobertura de controles auditados
```

**Flujo:**
```
1. Auditoría → Seleccionar controles desde SOA
2. Ejecutar checklist por control
3. Registrar hallazgos vinculados al control
4. Actualizar estado del control en SOA
5. Generar informe de cobertura
```

##### Con Gestión de Riesgos

**Funcionalidades:**
```python
# Priorizar auditorías según nivel de riesgo
- Calcular prioridad de auditoría basada en riesgos asociados
- Auditorías más frecuentes para áreas de alto riesgo
- Vincular hallazgos con riesgos identificados
- Actualizar evaluación de riesgos post-auditoría
- Generar acciones de mitigación desde hallazgos
```

**Flujo:**
```
1. Programa de auditoría → Priorizar por matriz de riesgos
2. Auditoría → Revisar controles de riesgos críticos
3. Hallazgo → Vincular con riesgo existente
4. Post-auditoría → Actualizar nivel de riesgo residual
```

##### Con No Conformidades

**Funcionalidades:**
```python
# Sincronización bidireccional
- Crear NC automáticamente desde hallazgos mayores
- Sincronizar acciones correctivas
- Compartir análisis de causa raíz
- Consolidar métricas de NCs y hallazgos
```

**Flujo:**
```
1. Hallazgo Mayor → Auto-crear NC
2. Plan de Acción → Sincronizar con NC
3. Cierre de Hallazgo → Cerrar NC asociada
4. Métricas → Consolidar datos
```

##### Con Gestión Documental

**Funcionalidades:**
```python
# Control de documentos de auditoría
- Almacenar documentos con control de versiones
- Aplicar flujo de aprobación a informes
- Mantener trazabilidad documental
- Archivo digital de evidencias
- Gestionar obsoletos
```

**Tipos de documentos gestionados:**
- Plan de auditoría
- Listas de verificación
- Evidencias
- Actas de reuniones (apertura/cierre)
- Informe de auditoría
- Planes de acción correctiva

##### Con Gestión de Usuarios

**Funcionalidades:**
```python
# Gestión de auditores
- Validar calificaciones de auditores
- Verificar independencia (no auditar propia área)
- Registrar horas de auditoría para certificación
- Gestionar competencias de auditores
- Evaluación de desempeño de auditores
```

**Validaciones:**
- ✅ Auditor líder debe tener calificación válida
- ✅ Certificación no vencida
- ✅ Horas mínimas de auditoría completadas
- ✅ No conflicto de intereses

##### Con Incidentes de Seguridad

**Funcionalidades:**
```python
# Análisis de incidentes en auditorías
- Revisar incidentes durante auditoría
- Verificar tratamiento y cierre adecuado
- Identificar patrones recurrentes
- Auditar proceso de gestión de incidentes
```

---

### FASE 5: Funcionalidades Avanzadas ⚡

#### 5.1 Automatizaciones

```python
# ==== NOTIFICACIONES AUTOMÁTICAS ====

class AuditNotificationService:

    # Notificaciones de auditoría
    - notify_audit_planned(audit_id, days_before=7)
      » Email a auditor líder y equipo
      » Email a responsables del área auditada

    - notify_audit_starting_soon(audit_id, days_before=2)
      » Recordatorio a todo el equipo
      » Checklist de preparación

    - notify_audit_overdue(audit_id)
      » Alerta si auditoría no completada en plazo

    # Notificaciones de hallazgos
    - notify_finding_created(finding_id)
      » Email a responsable del hallazgo
      » Copia a jefe de área

    - notify_finding_deadline_approaching(finding_id, days_before=5)
      » Recordatorio de plazo próximo a vencer

    - notify_finding_overdue(finding_id)
      » Alerta de hallazgo vencido
      » Escalamiento automático

    # Notificaciones de acciones
    - notify_action_assigned(action_id)
      » Email al responsable de la acción

    - notify_action_progress_update(action_id)
      » Notificar a auditor líder

    - notify_action_verification_needed(action_id)
      » Solicitar verificación al verificador

    # Notificaciones del programa
    - notify_program_approved(program_id)
      » Email a todos los auditores
      » Publicar en dashboard

    - notify_recurring_audit_due(schedule_id)
      » Recordar auditoría recurrente
      » Auto-crear draft de auditoría

# ==== GENERACIÓN AUTOMÁTICA ====

class AuditAutoGenerationService:

    - generate_audit_code()
      » Formato: AUD-YYYY-###
      » Secuencial por año

    - generate_finding_code(audit_code)
      » Formato: HAL-YYYY-###-##
      » Vinculado a auditoría

    - generate_action_code()
      » Formato: AC-YYYY-###

    - generate_audit_from_template(template_id, target_date)
      » Crear auditoría desde plantilla
      » Pre-cargar checklist y equipo

    - generate_annual_program(year, base_program_id=None)
      » Proponer programa basado en año anterior
      » Calcular frecuencias automáticamente
      » Sugerir fechas basadas en disponibilidad

    - generate_audit_report_draft(audit_id)
      » Informe preliminar desde hallazgos
      » Secciones pre-completadas
      » Resumen ejecutivo automático

    - propose_audit_calendar(program_id)
      » Distribuir auditorías en el año
      » Considerar vacaciones y períodos críticos
      » Balancear carga de auditores

# ==== CÁLCULOS AUTOMÁTICOS ====

class AuditMetricsCalculator:

    - calculate_conformity_rate(audit_id)
      » % conformidad = (Total items - NCs) / Total items × 100

    - calculate_recurrence_index()
      » Hallazgos recurrentes / Total hallazgos

    - calculate_average_closure_time(period='month')
      » Tiempo promedio de cierre por período

    - calculate_iso27001_coverage(program_id)
      » % controles Anexo A auditados

    - calculate_auditor_workload(auditor_id, period='month')
      » Horas de auditoría por auditor

    - calculate_finding_severity_score(finding_id)
      » Puntuación basada en impacto y probabilidad

    - update_program_completion_rate(program_id)
      » Actualizar % completado del programa

    - calculate_audit_cost(audit_id)
      » Costo estimado: horas × tarifa + gastos

# ==== TAREAS PROGRAMADAS (Cron Jobs) ====

# Ejecutar diariamente
- send_daily_notifications()
  » Auditorías próximas (7 días)
  » Hallazgos por vencer (5 días)
  » Acciones vencidas

# Ejecutar semanalmente
- generate_weekly_summary()
  » Resumen de auditorías completadas
  » Hallazgos abiertos/cerrados
  » KPIs principales

# Ejecutar mensualmente
- calculate_monthly_metrics()
  » Actualizar métricas del período
  » Generar informe automático
  » Exportar para dirección

# Ejecutar trimestralmente
- trigger_recurring_audits()
  » Crear auditorías recurrentes trimestrales
  » Notificar auditores

# Ejecutar anualmente
- generate_annual_program_proposal()
  » Propuesta de programa para próximo año
  » Basado en historial y riesgos
```

#### 5.2 Listas de Verificación (Checklists)

##### Plantillas Predefinidas ISO 27001

**5. Controles Organizacionales (37 controles)**
```
Archivo: checklists/iso27001/organizational_controls.json

Secciones:
├── 5.1-5.7   Políticas y liderazgo
├── 5.8-5.14  Gestión de activos e información
├── 5.15-5.23 Gestión de accesos y proveedores
├── 5.24-5.30 Gestión de incidentes y continuidad
└── 5.31-5.37 Requisitos legales y cumplimiento

Formato por item:
{
  "control_id": "5.1",
  "control_name": "Políticas para la seguridad de la información",
  "questions": [
    {
      "id": "5.1.1",
      "question": "¿Existe una política de seguridad de la información aprobada por la dirección?",
      "evidence_required": true,
      "iso_clause": "5.1",
      "guidance": "Verificar documento de política, fecha de aprobación y firma de dirección"
    },
    {
      "id": "5.1.2",
      "question": "¿La política se ha comunicado a todo el personal?",
      "evidence_required": true,
      "guidance": "Verificar actas de difusión, confirmaciones de lectura"
    }
  ]
}
```

**6. Controles de Personas (8 controles)**
```
Archivo: checklists/iso27001/people_controls.json

Secciones:
├── 6.1-6.2  Contratación
├── 6.3-6.4  Concienciación y formación
└── 6.5-6.8  Responsabilidades y acuerdos

Enfoque: Verificar procesos de selección, formación,
          acuerdos de confidencialidad y responsabilidades
```

**7. Controles Físicos (14 controles)**
```
Archivo: checklists/iso27001/physical_controls.json

Secciones:
├── 7.1-7.4  Perímetros y controles de acceso
├── 7.5-7.9  Protección ambiental y equipos
└── 7.10-7.14 Medios de almacenamiento y suministros

Enfoque: Inspección física, verificación de controles
          de acceso, protección de equipos
```

**8. Controles Tecnológicos (34 controles)**
```
Archivo: checklists/iso27001/technological_controls.json

Secciones:
├── 8.1-8.5   Dispositivos y autenticación
├── 8.6-8.14  Gestión de capacidad y configuración
├── 8.15-8.23 Seguridad de redes y desarrollo
└── 8.24-8.34 Testing y protección de sistemas

Enfoque: Pruebas técnicas, revisión de logs,
          análisis de configuraciones
```

##### Funcionalidades del Sistema de Checklists

```python
class ChecklistService:

    # Gestión de plantillas
    - create_template(name, control_domain, items)
    - import_iso27001_templates()
    - customize_template(template_id, changes)
    - export_template(template_id, format='json')

    # Ejecución de checklist
    - assign_checklist(audit_id, template_id, auditor_id, area)
    - complete_checklist_item(item_id, result, evidence, notes)
    - calculate_completion_percentage(checklist_id)
    - auto_generate_findings(checklist_id)
      » Si respuesta = "No Conforme" → Crear hallazgo automático

    # Resultados
    - get_checklist_results(audit_id)
    - export_checklist_results(checklist_id, format='pdf')
    - compare_checklist_results(checklist_id1, checklist_id2)

    # Análisis
    - identify_control_gaps(audit_id)
    - generate_coverage_matrix(audit_id)
```

**Estructura de item de checklist:**
```python
{
    "item_id": "5.1.1",
    "question": "¿Existe una política de seguridad?",
    "result": "conformant|non_conformant|not_applicable|not_verified",
    "evidence": "POL-SI-001 v2.0 aprobada 2025-01-15",
    "evidence_files": ["POL-SI-001.pdf"],
    "notes": "Política actualizada y vigente",
    "auditor_id": 123,
    "verification_date": "2025-10-17",
    "finding_created": true,
    "finding_id": 456
}
```

#### 5.3 Generación de Informes

##### Informes Disponibles

| # | Informe | Descripción | Formato | Audiencia |
|---|---------|-------------|---------|-----------|
| 1 | **Informe de Auditoría** | Informe completo según ISO 19011 | PDF | Dirección, Auditado |
| 2 | **Resumen Ejecutivo** | Hallazgos principales + KPIs | PDF/PPT | Alta Dirección |
| 3 | **Plan de Auditoría** | Programa detallado pre-auditoría | PDF | Equipo auditor, Auditado |
| 4 | **Informe del Programa** | Estado del programa anual | PDF | CISO, Dirección |
| 5 | **Métricas de Auditoría** | KPIs y tendencias | Excel/PDF | CISO, Auditor Líder |
| 6 | **Matriz de Hallazgos** | Todos los hallazgos con estado | Excel | Equipos operativos |
| 7 | **Cobertura ISO 27001** | % implementación Anexo A | PDF | CISO, Certificadores |
| 8 | **Informe de Seguimiento** | Estado de acciones correctivas | PDF | Dirección, Auditado |

##### Estructura de Informe de Auditoría (ISO 19011)

```markdown
# INFORME DE AUDITORÍA

## 1. PORTADA
- Logo de la organización
- Título del informe
- Código de auditoría
- Fecha de emisión
- Clasificación (Confidencial)

## 2. INFORMACIÓN GENERAL
- Código de auditoría: AUD-2025-001
- Tipo de auditoría: Auditoría Interna Planificada
- Alcance: Controles de seguridad física (Anexo A.7)
- Áreas auditadas: Oficina central, Data center
- Fechas:
  - Notificación: 2025-10-01
  - Ejecución: 2025-10-15 al 2025-10-17
  - Informe: 2025-10-20
- Estado: Completada

## 3. EQUIPO AUDITOR
| Rol | Nombre | Calificación |
|-----|--------|--------------|
| Auditor Líder | Juan Pérez | Lead Auditor ISO 27001 |
| Auditor | María García | Auditor ISO 27001 |
| Experto Técnico | Carlos López | CISSP |

## 4. ALCANCE Y OBJETIVOS

### 4.1 Alcance
Verificar la implementación y eficacia de los controles de seguridad
física definidos en el Anexo A.7 de ISO 27001:2022 en:
- Perímetros de seguridad física
- Controles de acceso
- Seguridad de oficinas y equipos
- Protección contra amenazas ambientales

### 4.2 Objetivos
1. Verificar conformidad con requisitos de ISO 27001:2022
2. Evaluar eficacia de controles implementados
3. Identificar oportunidades de mejora
4. Proporcionar evidencia para certificación

## 5. CRITERIOS DE AUDITORÍA
- ISO/IEC 27001:2022 - Anexo A.7
- Política de Seguridad Física POL-SF-001 v1.0
- Procedimiento de Control de Acceso PROC-CA-001 v2.0
- Legislación aplicable (LOPD, etc.)

## 6. RESUMEN EJECUTIVO

### 6.1 Conclusión General
CONFORME CON OBSERVACIONES

La organización ha implementado controles de seguridad física
adecuados que cumplen con los requisitos de ISO 27001:2022.
Se identificaron 2 no conformidades menores y 3 observaciones
que requieren atención para mejorar la eficacia del sistema.

### 6.2 Estadísticas de Hallazgos
- Total de hallazgos: 5
- No conformidades mayores: 0
- No conformidades menores: 2
- Observaciones: 3
- Oportunidades de mejora: 0

### 6.3 Tasa de Conformidad
85% de conformidad global

## 7. HALLAZGOS DETALLADOS

### 7.1 NO CONFORMIDADES MAYORES
Ninguna

### 7.2 NO CONFORMIDADES MENORES

#### NC-001: HAL-2025-001-01
**Control afectado:** 7.2 - Controles físicos de entrada

**Descripción:**
No se registra la salida de visitantes en el libro de control
de acceso en el 30% de los casos revisados.

**Evidencia:**
- Revisión de libro de visitas del mes de septiembre
- 12 de 40 visitas sin registro de salida
- Entrevista con personal de recepción

**Impacto:**
Imposibilidad de verificar que los visitantes han abandonado
las instalaciones, riesgo de acceso no autorizado a áreas
restringidas.

**Causa raíz:**
Procedimiento de control de acceso no especifica obligación
de registrar salida, personal de recepción no entrenado.

**Plazo de cierre:** 60 días

---

#### NC-002: HAL-2025-001-02
**Control afectado:** 7.4 - Monitorización de la seguridad física

**Descripción:**
Sistema de CCTV del data center tiene 2 cámaras sin funcionar
desde hace 15 días.

**Evidencia:**
- Inspección física del data center
- Revisión de logs del sistema de videovigilancia
- Ticket de mantenimiento #1234 sin resolver

**Impacto:**
Puntos ciegos en la monitorización del área crítica,
imposibilidad de verificar accesos en zona afectada.

**Causa raíz:**
No existe procedimiento de mantenimiento preventivo para
equipos de seguridad física.

**Plazo de cierre:** 30 días

### 7.3 OBSERVACIONES

#### OBS-001: HAL-2025-001-03
**Control:** 7.7 - Puesto de trabajo despejado

**Descripción:**
En 5 puestos de trabajo se observaron documentos clasificados
como "Confidencial" sobre las mesas al finalizar la jornada.

**Recomendación:**
Reforzar la política de "Clear Desk" mediante recordatorios
visuales y verificaciones periódicas.

---

#### OBS-002: HAL-2025-001-04
**Control:** 7.11 - Instalaciones de suministro

**Descripción:**
El tiempo de autonomía del SAI del data center (30 minutos)
es inferior al recomendado (1 hora) para garantizar apagado
ordenado de todos los sistemas.

**Recomendación:**
Evaluar ampliación de capacidad del SAI o implementar
procedimiento de apagado priorizado.

---

#### OBS-003: HAL-2025-001-05
**Control:** 7.3 - Seguridad de oficinas

**Descripción:**
No existe señalización clara de las zonas de seguridad
restringida en la planta 2.

**Recomendación:**
Implementar señalización según procedimiento de control
de acceso.

## 8. CONCLUSIONES

1. **Fortalezas identificadas:**
   - Sistema de control de acceso biométrico bien implementado
   - Perímetros de seguridad física claramente definidos
   - Personal consciente de políticas de seguridad
   - Mantenimiento regular de sistemas de climatización

2. **Áreas de mejora:**
   - Procedimientos de control de visitantes
   - Mantenimiento preventivo de sistemas de seguridad
   - Cultura de "Clear Desk"
   - Capacidad de sistemas de respaldo

3. **Riesgos identificados:**
   - Riesgo MEDIO: Acceso no controlado de visitantes
   - Riesgo BAJO: Puntos ciegos en videovigilancia
   - Riesgo BAJO: Falta de autonomía eléctrica

## 9. RECOMENDACIONES

1. **Corto plazo (< 30 días):**
   - Reparar cámaras de CCTV del data center
   - Actualizar procedimiento de control de visitantes
   - Implementar señalización de zonas restringidas

2. **Medio plazo (30-90 días):**
   - Desarrollar plan de mantenimiento preventivo
   - Implantar programa de verificación "Clear Desk"
   - Realizar evaluación de capacidad del SAI

3. **Largo plazo (> 90 días):**
   - Considerar actualización del sistema de videovigilancia
   - Evaluar implementación de torniquetes en accesos
   - Desarrollar plan de continuidad para sistemas críticos

## 10. SEGUIMIENTO

Se programará auditoría de seguimiento para:
- Fecha: 2025-12-15
- Verificar cierre de no conformidades
- Validar eficacia de acciones correctivas

## 11. ANEXOS

A. Lista de documentos revisados
B. Lista de personal entrevistado
C. Fotografías de evidencias
D. Checklist de auditoría completado
E. Planes de acción correctiva

## 12. FIRMAS

**Auditor Líder:**
Juan Pérez
Fecha: 2025-10-20

**Responsable del Área Auditada:**
Pedro Martínez - Jefe de Seguridad Física
Fecha: 2025-10-21

**Aprobación CISO:**
Ana Rodríguez - CISO
Fecha: 2025-10-22
```

##### Generación Automática de Informes

```python
class AuditReportGenerator:

    def generate_audit_report(self, audit_id, template='standard'):
        """
        Genera informe completo de auditoría

        Templates disponibles:
        - standard: Informe completo ISO 19011
        - executive: Resumen ejecutivo para dirección
        - technical: Informe técnico detallado
        - certification: Formato para certificación externa
        """

        audit = AuditRecord.query.get(audit_id)

        # Recopilar datos
        data = {
            'audit': audit,
            'team': audit.team_members,
            'findings': audit.findings,
            'major_ncs': audit.findings.filter_by(finding_type=FindingType.MAJOR_NC).all(),
            'minor_ncs': audit.findings.filter_by(finding_type=FindingType.MINOR_NC).all(),
            'observations': audit.findings.filter_by(finding_type=FindingType.OBSERVATION).all(),
            'stats': self._calculate_stats(audit),
            'iso_controls_coverage': self._get_iso_coverage(audit),
            'timeline': self._get_audit_timeline(audit),
            'evidences': audit.evidences,
            'checklists': audit.checklists
        }

        # Generar PDF
        html = render_template(f'audits/reports/{template}.html', **data)
        pdf = self._html_to_pdf(html)

        # Guardar
        filename = f"Informe_Auditoria_{audit.audit_code}.pdf"
        filepath = self._save_report(pdf, filename)

        # Registrar documento
        self._register_document(audit_id, filepath, DocumentType.AUDIT_REPORT)

        return filepath

    def generate_program_report(self, program_id):
        """Genera informe del programa anual"""
        pass

    def generate_findings_matrix(self, filters=None):
        """Genera matriz Excel de hallazgos"""
        pass

    def generate_metrics_dashboard(self, period):
        """Genera dashboard de métricas en PDF"""
        pass

    def export_to_powerpoint(self, audit_id):
        """Exporta resumen ejecutivo a PowerPoint"""
        pass
```

---

### FASE 6: Validaciones y Reglas de Negocio ✅

#### 6.1 Validaciones por Entidad

##### Programa de Auditoría

```python
class ProgramValidator:

    @staticmethod
    def validate_create(program_data):
        errors = []

        # Solo un programa activo por año
        existing = AuditProgram.query.filter_by(
            year=program_data['year'],
            status=ProgramStatus.APPROVED
        ).first()
        if existing:
            errors.append(f"Ya existe un programa aprobado para {program_data['year']}")

        # Fechas coherentes
        if program_data['start_date'] >= program_data['end_date']:
            errors.append("La fecha de inicio debe ser anterior a la fecha de fin")

        # Año válido
        current_year = datetime.now().year
        if program_data['year'] < current_year:
            errors.append("No se pueden crear programas para años pasados")

        if program_data['year'] > current_year + 1:
            errors.append("Solo se pueden crear programas para el año actual y siguiente")

        return errors

    @staticmethod
    def validate_approve(program, user):
        errors = []

        # Solo CISO o Admin pueden aprobar
        if not user.has_role(['CISO', 'ADMIN']):
            errors.append("No tiene permisos para aprobar programas")

        # Debe estar en borrador
        if program.status != ProgramStatus.DRAFT:
            errors.append("Solo se pueden aprobar programas en estado Borrador")

        # Debe tener auditorías planificadas
        if program.audits.count() == 0:
            errors.append("El programa no tiene auditorías planificadas")

        # Cobertura mínima
        coverage = calculate_iso_coverage(program)
        if coverage < 80:
            errors.append(f"Cobertura insuficiente ({coverage}%). Mínimo requerido: 80%")

        return errors
```

##### Auditoría

```python
class AuditValidator:

    @staticmethod
    def validate_create(audit_data):
        errors = []

        # Auditor líder obligatorio
        if not audit_data.get('lead_auditor_id'):
            errors.append("Debe asignar un auditor líder")

        # Auditor líder debe estar calificado
        lead_auditor = User.query.get(audit_data['lead_auditor_id'])
        if not lead_auditor.is_qualified_lead_auditor():
            errors.append("El auditor líder no tiene calificación válida")

        # Fechas coherentes
        if audit_data.get('start_date') and audit_data.get('end_date'):
            if audit_data['start_date'] > audit_data['end_date']:
                errors.append("Fecha de inicio debe ser anterior a fecha de fin")

        # Alcance obligatorio
        if not audit_data.get('scope'):
            errors.append("Debe definir el alcance de la auditoría")

        return errors

    @staticmethod
    def validate_team_member(audit, user_id, area):
        errors = []

        user = User.query.get(user_id)

        # Verificar independencia
        if user.department == area:
            errors.append(f"{user.full_name} no puede auditar su propia área")

        # Verificar calificación
        if not user.is_qualified_auditor():
            errors.append(f"{user.full_name} no tiene calificación de auditor")

        # Verificar disponibilidad
        conflicting_audits = self._check_availability(user_id, audit.start_date, audit.end_date)
        if conflicting_audits:
            errors.append(f"{user.full_name} tiene auditorías en las mismas fechas")

        return errors

    @staticmethod
    def validate_status_transition(audit, new_status, user):
        errors = []

        current_status = audit.status
        allowed_transitions = STATE_TRANSITIONS.get(current_status.value, [])

        if new_status not in allowed_transitions:
            errors.append(f"Transición no permitida: {current_status.value} → {new_status}")

        # Validaciones específicas por transición
        if new_status == AuditStatus.IN_PROGRESS:
            # Debe tener plan de auditoría
            if not audit.audit_plan_file:
                errors.append("Debe cargar el plan de auditoría antes de iniciar")

            # Debe tener equipo asignado
            if audit.team_members.count() == 0:
                errors.append("Debe asignar equipo auditor antes de iniciar")

        if new_status == AuditStatus.COMPLETED:
            # Debe tener informe
            if not audit.audit_report_file:
                errors.append("Debe generar el informe antes de completar")

            # Todos los hallazgos mayores deben tener plan de acción
            major_findings = audit.findings.filter_by(finding_type=FindingType.MAJOR_NC).all()
            for finding in major_findings:
                if finding.corrective_actions.count() == 0:
                    errors.append(f"Hallazgo {finding.finding_code} sin plan de acción")

        if new_status == AuditStatus.CLOSED:
            # Todos los hallazgos deben estar cerrados
            open_findings = audit.findings.filter(
                FindingStatus.status != FindingStatus.CLOSED
            ).count()
            if open_findings > 0:
                errors.append(f"Quedan {open_findings} hallazgos sin cerrar")

        return errors

    @staticmethod
    def validate_document_upload(audit, document_type, file):
        errors = []

        # Extensiones permitidas
        allowed_extensions = {
            DocumentType.AUDIT_PLAN: ['.pdf', '.docx'],
            DocumentType.AUDIT_REPORT: ['.pdf'],
            DocumentType.CHECKLIST: ['.pdf', '.xlsx'],
            DocumentType.EVIDENCE: ['.pdf', '.jpg', '.png', '.docx', '.xlsx']
        }

        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions.get(document_type, []):
            errors.append(f"Formato no permitido para {document_type.value}: {file_ext}")

        # Tamaño máximo (10 MB)
        max_size = 10 * 1024 * 1024
        if len(file.read()) > max_size:
            errors.append("El archivo excede el tamaño máximo (10 MB)")
        file.seek(0)  # Reset file pointer

        return errors
```

##### Hallazgo

```python
class FindingValidator:

    @staticmethod
    def validate_create(audit_id, finding_data):
        errors = []

        # Título obligatorio
        if not finding_data.get('title'):
            errors.append("El título es obligatorio")

        # Descripción obligatoria
        if not finding_data.get('description'):
            errors.append("La descripción es obligatoria")

        # Tipo de hallazgo obligatorio
        if not finding_data.get('finding_type'):
            errors.append("Debe clasificar el hallazgo")

        # Evidencia obligatoria
        if not finding_data.get('evidence'):
            errors.append("Debe documentar la evidencia del hallazgo")

        # Causa raíz obligatoria para NCs
        finding_type = finding_data.get('finding_type')
        if finding_type in [FindingType.MAJOR_NC, FindingType.MINOR_NC]:
            if not finding_data.get('root_cause'):
                errors.append("El análisis de causa raíz es obligatorio para no conformidades")

        # Responsable obligatorio
        if not finding_data.get('responsible_id'):
            errors.append("Debe asignar un responsable")

        # Control ISO 27001 cuando aplique
        if finding_data.get('affected_control'):
            control = validate_iso_control(finding_data['affected_control'])
            if not control:
                errors.append("Control ISO 27001 no válido")

        return errors

    @staticmethod
    def validate_closure(finding):
        errors = []

        # Debe tener al menos una acción correctiva completada
        completed_actions = finding.corrective_actions.filter_by(
            status=ActionStatus.COMPLETED
        ).count()

        if completed_actions == 0:
            errors.append("Debe tener al menos una acción correctiva completada")

        # Acciones deben estar verificadas
        verified_actions = finding.corrective_actions.filter_by(
            effectiveness_verified=True
        ).count()

        if verified_actions == 0:
            errors.append("Las acciones deben estar verificadas")

        # No puede haber acciones en progreso
        in_progress = finding.corrective_actions.filter_by(
            status=ActionStatus.IN_PROGRESS
        ).count()

        if in_progress > 0:
            errors.append("Hay acciones correctivas en progreso")

        return errors
```

##### Acción Correctiva

```python
class ActionValidator:

    @staticmethod
    def validate_create(finding_id, action_data):
        errors = []

        # Descripción obligatoria
        if not action_data.get('description'):
            errors.append("La descripción de la acción es obligatoria")

        # Responsable obligatorio
        if not action_data.get('responsible_id'):
            errors.append("Debe asignar un responsable")

        # Verificador obligatorio
        if not action_data.get('verifier_id'):
            errors.append("Debe asignar un verificador")

        # Verificador != Responsable
        if action_data.get('responsible_id') == action_data.get('verifier_id'):
            errors.append("El verificador debe ser diferente al responsable")

        # Fecha de finalización
        if not action_data.get('planned_completion_date'):
            errors.append("Debe establecer fecha de finalización")

        # Fecha realista
        completion_date = action_data.get('planned_completion_date')
        if completion_date:
            # No puede ser en el pasado
            if completion_date < datetime.now().date():
                errors.append("La fecha de finalización no puede ser en el pasado")

            # No puede ser más de 1 año en el futuro
            max_date = datetime.now().date() + timedelta(days=365)
            if completion_date > max_date:
                errors.append("La fecha de finalización es demasiado lejana")

        # Tipo de acción
        if not action_data.get('action_type'):
            errors.append("Debe especificar el tipo de acción")

        return errors

    @staticmethod
    def validate_complete(action):
        errors = []

        # Progreso debe ser 100%
        if action.progress_percentage < 100:
            errors.append("El progreso debe ser 100% para completar")

        # Debe tener notas de implementación
        if not action.progress_notes:
            errors.append("Debe documentar la implementación")

        return errors

    @staticmethod
    def validate_verify(action, verifier_id):
        errors = []

        # Acción debe estar completada
        if action.status != ActionStatus.COMPLETED:
            errors.append("Solo se pueden verificar acciones completadas")

        # Verificador asignado
        if action.verifier_id != verifier_id:
            errors.append("No es el verificador asignado")

        # Tiempo mínimo de implementación (3 meses para verificar eficacia)
        if action.actual_completion_date:
            min_date = action.actual_completion_date + timedelta(days=90)
            if datetime.now().date() < min_date:
                errors.append("Debe esperar 3 meses para verificar eficacia")

        return errors
```

#### 6.2 Matriz de Reglas de Negocio

| Entidad | Regla | Validación | Consecuencia |
|---------|-------|------------|--------------|
| **Programa** | Un programa activo por año | `validate_unique_active_program()` | Bloqueo de creación |
| **Programa** | Cobertura mínima 80% | `validate_coverage()` | Bloqueo de aprobación |
| **Auditoría** | Auditor líder calificado | `validate_lead_auditor_qualification()` | Bloqueo de creación |
| **Auditoría** | Equipo independiente | `validate_team_independence()` | Bloqueo de asignación |
| **Auditoría** | Plan antes de iniciar | `validate_audit_plan_exists()` | Bloqueo de transición |
| **Auditoría** | Informe antes de completar | `validate_report_exists()` | Bloqueo de transición |
| **Hallazgo** | Evidencia documentada | `validate_evidence()` | Bloqueo de creación |
| **Hallazgo** | Causa raíz para NCs | `validate_root_cause()` | Bloqueo de creación |
| **Hallazgo** | Plazo según severidad | `auto_set_deadline()` | Cálculo automático |
| **Acción** | Verificador ≠ Responsable | `validate_verifier()` | Bloqueo de creación |
| **Acción** | 3 meses antes de verificar | `validate_verification_timing()` | Bloqueo de verificación |
| **Acción** | Progreso 100% para completar | `validate_completion()` | Bloqueo de transición |

---

### FASE 7: Métricas y KPIs 📊

#### 7.1 Indicadores Clave de Rendimiento

##### Indicadores de Ejecución del Programa

```python
class ProgramMetrics:

    # KPI 1: Cumplimiento del Programa
    def program_completion_rate(program_id):
        """
        % auditorías completadas vs planificadas
        Meta: ≥ 90%
        """
        program = AuditProgram.query.get(program_id)
        total = program.audits.count()
        completed = program.audits.filter(
            AuditRecord.status.in_([AuditStatus.COMPLETED, AuditStatus.CLOSED])
        ).count()

        return (completed / total * 100) if total > 0 else 0

    # KPI 2: Cumplimiento de Plazos
    def on_time_completion_rate(program_id):
        """
        % auditorías completadas en plazo
        Meta: ≥ 85%
        """
        program = AuditProgram.query.get(program_id)
        completed_audits = program.audits.filter_by(status=AuditStatus.COMPLETED).all()

        on_time = sum(1 for audit in completed_audits
                     if audit.report_date <= audit.planned_date)

        return (on_time / len(completed_audits) * 100) if completed_audits else 0

    # KPI 3: Cobertura ISO 27001
    def iso27001_coverage(program_id):
        """
        % controles Anexo A auditados
        Meta: ≥ 80%
        """
        program = AuditProgram.query.get(program_id)

        # Obtener todos los controles aplicables del SOA
        applicable_controls = get_applicable_controls()
        total_controls = len(applicable_controls)

        # Controles auditados en el programa
        audited_controls = set()
        for audit in program.audits:
            if audit.audited_controls:
                audited_controls.update(json.loads(audit.audited_controls))

        return (len(audited_controls) / total_controls * 100) if total_controls > 0 else 0

    # KPI 4: Promedio de Horas por Auditoría
    def average_audit_hours(program_id):
        """
        Horas promedio de auditoría
        Meta: Según planificación
        """
        program = AuditProgram.query.get(program_id)
        completed_audits = program.audits.filter_by(status=AuditStatus.COMPLETED).all()

        total_hours = sum(
            (audit.end_date - audit.start_date).days * 8
            for audit in completed_audits
            if audit.start_date and audit.end_date
        )

        return total_hours / len(completed_audits) if completed_audits else 0
```

##### Indicadores de Hallazgos

```python
class FindingMetrics:

    # KPI 5: Total de Hallazgos
    def total_findings(period='month'):
        """
        Total de hallazgos por período
        Segmentado por severidad
        """
        start_date, end_date = get_period_dates(period)

        findings = AuditFinding.query.filter(
            AuditFinding.created_at.between(start_date, end_date)
        ).all()

        return {
            'total': len(findings),
            'major_nc': sum(1 for f in findings if f.finding_type == FindingType.MAJOR_NC),
            'minor_nc': sum(1 for f in findings if f.finding_type == FindingType.MINOR_NC),
            'observations': sum(1 for f in findings if f.finding_type == FindingType.OBSERVATION),
            'opportunities': sum(1 for f in findings if f.finding_type == FindingType.OPPORTUNITY_IMPROVEMENT)
        }

    # KPI 6: Tasa de Recurrencia
    def recurrence_rate():
        """
        % hallazgos recurrentes
        Meta: < 10%
        """
        all_findings = AuditFinding.query.all()

        # Identificar hallazgos recurrentes (mismo control en últimos 2 años)
        recurrent_findings = 0
        for finding in all_findings:
            if finding.affected_control:
                previous = AuditFinding.query.filter(
                    AuditFinding.affected_control == finding.affected_control,
                    AuditFinding.created_at < finding.created_at,
                    AuditFinding.created_at >= finding.created_at - timedelta(days=730),
                    AuditFinding.id != finding.id
                ).first()

                if previous:
                    recurrent_findings += 1

        return (recurrent_findings / len(all_findings) * 100) if all_findings else 0

    # KPI 7: Hallazgos Cerrados en Plazo
    def findings_closed_on_time(period='month'):
        """
        % hallazgos cerrados dentro del plazo
        Meta: ≥ 80%
        """
        start_date, end_date = get_period_dates(period)

        closed_findings = AuditFinding.query.filter(
            AuditFinding.status == FindingStatus.CLOSED,
            AuditFinding.updated_at.between(start_date, end_date)
        ).all()

        on_time = sum(1 for f in closed_findings if was_closed_on_time(f))

        return (on_time / len(closed_findings) * 100) if closed_findings else 0

    # KPI 8: Hallazgos Vencidos
    def overdue_findings():
        """
        Número de hallazgos vencidos
        Meta: 0
        """
        today = datetime.now().date()

        overdue = AuditFinding.query.filter(
            AuditFinding.status.in_([
                FindingStatus.OPEN,
                FindingStatus.ACTION_PLAN_APPROVED,
                FindingStatus.IN_TREATMENT
            ])
        ).all()

        overdue_count = 0
        for finding in overdue:
            deadline = calculate_finding_deadline(finding)
            if deadline < today:
                overdue_count += 1

        return {
            'total': overdue_count,
            'major': sum(1 for f in overdue if f.finding_type == FindingType.MAJOR_NC),
            'minor': sum(1 for f in overdue if f.finding_type == FindingType.MINOR_NC)
        }

    # KPI 9: Tiempo Promedio de Cierre
    def average_closure_time(period='year'):
        """
        Días promedio de cierre de hallazgos
        Meta: < 60 días
        """
        start_date, end_date = get_period_dates(period)

        closed_findings = AuditFinding.query.filter(
            AuditFinding.status == FindingStatus.CLOSED,
            AuditFinding.updated_at.between(start_date, end_date)
        ).all()

        total_days = sum(
            (f.updated_at.date() - f.created_at.date()).days
            for f in closed_findings
        )

        return total_days / len(closed_findings) if closed_findings else 0
```

##### Indicadores de Eficacia

```python
class EffectivenessMetrics:

    # KPI 10: Eficacia de Acciones Correctivas
    def action_effectiveness_rate():
        """
        % acciones verificadas como efectivas
        Meta: ≥ 90%
        """
        verified_actions = CorrectiveAction.query.filter_by(
            status=ActionStatus.VERIFIED
        ).all()

        effective = sum(1 for action in verified_actions
                       if action.effectiveness_verified)

        return (effective / len(verified_actions) * 100) if verified_actions else 0

    # KPI 11: Hallazgos Reabiertos
    def reopened_findings_rate():
        """
        % hallazgos reabiertos después de cierre
        Meta: < 5%
        """
        all_closed = AuditFinding.query.filter_by(status=FindingStatus.CLOSED).count()

        # Buscar en logs de cambios de estado los reabiertos
        reopened = count_reopened_findings()

        return (reopened / all_closed * 100) if all_closed > 0 else 0

    # KPI 12: Tendencia de No Conformidades
    def nc_trend(months=12):
        """
        Tendencia de NCs en los últimos N meses
        Resultado: ↑ (creciente), → (estable), ↓ (decreciente)
        """
        monthly_data = []

        for i in range(months):
            start = datetime.now().replace(day=1) - timedelta(days=30*i)
            end = start + timedelta(days=30)

            nc_count = AuditFinding.query.filter(
                AuditFinding.finding_type.in_([FindingType.MAJOR_NC, FindingType.MINOR_NC]),
                AuditFinding.created_at.between(start, end)
            ).count()

            monthly_data.append(nc_count)

        # Calcular tendencia con regresión lineal simple
        trend = calculate_trend(monthly_data)

        if trend > 0.1:
            return '↑ Creciente'
        elif trend < -0.1:
            return '↓ Decreciente'
        else:
            return '→ Estable'
```

##### Indicadores Estratégicos

```python
class StrategicMetrics:

    # KPI 13: Índice de Conformidad Global
    def global_conformity_index():
        """
        Índice de conformidad del SGSI
        Meta: ≥ 85%

        Fórmula: 100 - (NCs Mayores * 10 + NCs Menores * 5 + Obs * 1) / Total Controles
        """
        total_controls = get_applicable_controls_count()

        # Hallazgos activos de las últimas auditorías
        recent_audits = get_recent_audits(months=12)

        major_ncs = sum(audit.major_findings_count for audit in recent_audits)
        minor_ncs = sum(audit.minor_findings_count for audit in recent_audits)
        observations = sum(audit.observations_count for audit in recent_audits)

        penalty = (major_ncs * 10 + minor_ncs * 5 + observations * 1) / total_controls

        return max(0, 100 - penalty)

    # KPI 14: Evolución Año a Año
    def year_over_year_evolution():
        """
        Comparación de hallazgos año actual vs año anterior
        """
        current_year = datetime.now().year

        current_findings = get_findings_by_year(current_year)
        previous_findings = get_findings_by_year(current_year - 1)

        return {
            'current': current_findings,
            'previous': previous_findings,
            'change_percent': calculate_change_percent(current_findings, previous_findings),
            'improvement': current_findings['total'] < previous_findings['total']
        }

    # KPI 15: Madurez del SGSI
    def sgsi_maturity_level():
        """
        Nivel de madurez del SGSI basado en auditorías

        Niveles:
        1 - Inicial: > 20 NCs mayores
        2 - Gestionado: 10-20 NCs mayores
        3 - Definido: 5-10 NCs mayores
        4 - Gestionado Cuantitativamente: 1-5 NCs mayores
        5 - Optimizado: 0 NCs mayores, conformidad > 95%
        """
        recent_audits = get_recent_audits(months=12)
        total_major_ncs = sum(audit.major_findings_count for audit in recent_audits)
        conformity = global_conformity_index()

        if total_major_ncs == 0 and conformity > 95:
            return {'level': 5, 'description': 'Optimizado'}
        elif total_major_ncs <= 5:
            return {'level': 4, 'description': 'Gestionado Cuantitativamente'}
        elif total_major_ncs <= 10:
            return {'level': 3, 'description': 'Definido'}
        elif total_major_ncs <= 20:
            return {'level': 2, 'description': 'Gestionado'}
        else:
            return {'level': 1, 'description': 'Inicial'}
```

#### 7.2 Dashboard de Visualizaciones

##### Gráficos Principales

```javascript
// 1. Gráfico de Barras: Hallazgos por Severidad
const findingsByTypeChart = {
    type: 'bar',
    data: {
        labels: ['NCs Mayores', 'NCs Menores', 'Observaciones', 'Oportunidades'],
        datasets: [{
            label: 'Cantidad',
            data: [2, 5, 8, 3],
            backgroundColor: [
                'rgba(220, 53, 69, 0.8)',   // Rojo - Mayor
                'rgba(255, 193, 7, 0.8)',   // Amarillo - Menor
                'rgba(13, 110, 253, 0.8)',  // Azul - Observación
                'rgba(25, 135, 84, 0.8)'    // Verde - Oportunidad
            ]
        }]
    },
    options: {
        responsive: true,
        plugins: {
            title: {
                display: true,
                text: 'Distribución de Hallazgos por Severidad'
            }
        }
    }
};

// 2. Gráfico de Líneas: Tendencia de NCs
const trendChart = {
    type: 'line',
    data: {
        labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'],
        datasets: [
            {
                label: 'NCs Mayores',
                data: [5, 3, 4, 2, 1, 2],
                borderColor: 'rgb(220, 53, 69)',
                backgroundColor: 'rgba(220, 53, 69, 0.1)'
            },
            {
                label: 'NCs Menores',
                data: [12, 10, 8, 7, 6, 5],
                borderColor: 'rgb(255, 193, 7)',
                backgroundColor: 'rgba(255, 193, 7, 0.1)'
            }
        ]
    },
    options: {
        responsive: true,
        plugins: {
            title: {
                display: true,
                text: 'Tendencia de No Conformidades'
            }
        },
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
};

// 3. Gráfico Circular: Distribución por Área
const findingsByAreaChart = {
    type: 'pie',
    data: {
        labels: ['IT', 'RRHH', 'Operaciones', 'Finanzas', 'Legal'],
        datasets: [{
            data: [15, 8, 12, 5, 3],
            backgroundColor: [
                'rgba(220, 53, 69, 0.8)',
                'rgba(255, 193, 7, 0.8)',
                'rgba(13, 110, 253, 0.8)',
                'rgba(25, 135, 84, 0.8)',
                'rgba(108, 117, 125, 0.8)'
            ]
        }]
    },
    options: {
        responsive: true,
        plugins: {
            title: {
                display: true,
                text: 'Hallazgos por Área'
            }
        }
    }
};

// 4. Heatmap: Controles ISO 27001 con más Hallazgos
const controlsHeatmap = {
    type: 'matrix',
    data: {
        datasets: [{
            label: 'Hallazgos por Control',
            data: [
                {x: '5.1', y: 'Q1', v: 3},
                {x: '5.2', y: 'Q1', v: 1},
                {x: '7.2', y: 'Q2', v: 5},
                {x: '8.5', y: 'Q3', v: 2},
                // ... más datos
            ],
            backgroundColor(context) {
                const value = context.dataset.data[context.dataIndex].v;
                const alpha = value / 10;
                return `rgba(220, 53, 69, ${alpha})`;
            }
        }]
    },
    options: {
        responsive: true,
        plugins: {
            title: {
                display: true,
                text: 'Controles con Mayor Cantidad de Hallazgos'
            },
            tooltip: {
                callbacks: {
                    title() {
                        return '';
                    },
                    label(context) {
                        const v = context.dataset.data[context.dataIndex];
                        return [
                            'Control: ' + v.x,
                            'Período: ' + v.y,
                            'Hallazgos: ' + v.v
                        ];
                    }
                }
            }
        },
        scales: {
            x: {
                type: 'category',
                labels: ['5.1', '5.2', '7.2', '8.5', '8.15'],
                title: {
                    display: true,
                    text: 'Control ISO 27001'
                }
            },
            y: {
                type: 'category',
                labels: ['Q1', 'Q2', 'Q3', 'Q4'],
                title: {
                    display: true,
                    text: 'Trimestre'
                }
            }
        }
    }
};

// 5. Gráfico de Embudo: Estados de Hallazgos
const findingsStatesFunnel = {
    type: 'bar',
    data: {
        labels: ['Abiertos', 'Plan Aprobado', 'En Tratamiento', 'Resueltos', 'Verificados', 'Cerrados'],
        datasets: [{
            label: 'Hallazgos',
            data: [25, 20, 15, 10, 7, 5],
            backgroundColor: [
                'rgba(220, 53, 69, 0.8)',
                'rgba(255, 193, 7, 0.8)',
                'rgba(13, 110, 253, 0.8)',
                'rgba(13, 202, 240, 0.8)',
                'rgba(111, 66, 193, 0.8)',
                'rgba(25, 135, 84, 0.8)'
            ]
        }]
    },
    options: {
        indexAxis: 'y',
        responsive: true,
        plugins: {
            title: {
                display: true,
                text: 'Embudo de Estados de Hallazgos'
            }
        }
    }
};
```

##### Widgets de KPIs

```html
<!-- KPI Cards -->
<div class="row">
    <!-- Auditorías Planificadas -->
    <div class="col-md-3">
        <div class="kpi-card kpi-primary">
            <div class="kpi-icon">
                <i class="fas fa-clipboard-list"></i>
            </div>
            <div class="kpi-content">
                <h3 class="kpi-value">24</h3>
                <p class="kpi-label">Auditorías Planificadas</p>
                <div class="kpi-progress">
                    <div class="progress">
                        <div class="progress-bar" style="width: 75%"></div>
                    </div>
                    <span class="kpi-progress-text">75% completado</span>
                </div>
            </div>
        </div>
    </div>

    <!-- Conformidad Global -->
    <div class="col-md-3">
        <div class="kpi-card kpi-success">
            <div class="kpi-icon">
                <i class="fas fa-check-circle"></i>
            </div>
            <div class="kpi-content">
                <h3 class="kpi-value">87%</h3>
                <p class="kpi-label">Conformidad Global</p>
                <div class="kpi-trend trend-up">
                    <i class="fas fa-arrow-up"></i> +3% vs mes anterior
                </div>
            </div>
        </div>
    </div>

    <!-- Hallazgos Abiertos -->
    <div class="col-md-3">
        <div class="kpi-card kpi-warning">
            <div class="kpi-icon">
                <i class="fas fa-exclamation-triangle"></i>
            </div>
            <div class="kpi-content">
                <h3 class="kpi-value">15</h3>
                <p class="kpi-label">Hallazgos Abiertos</p>
                <div class="kpi-breakdown">
                    <span class="badge badge-danger">2 Mayores</span>
                    <span class="badge badge-warning">5 Menores</span>
                    <span class="badge badge-info">8 Obs</span>
                </div>
            </div>
        </div>
    </div>

    <!-- Hallazgos Vencidos -->
    <div class="col-md-3">
        <div class="kpi-card kpi-danger">
            <div class="kpi-icon">
                <i class="fas fa-clock"></i>
            </div>
            <div class="kpi-content">
                <h3 class="kpi-value">3</h3>
                <p class="kpi-label">Hallazgos Vencidos</p>
                <div class="kpi-alert">
                    <i class="fas fa-bell"></i> Requiere atención inmediata
                </div>
            </div>
        </div>
    </div>
</div>
```

---

## 🎯 PRIORIZACIÓN DE IMPLEMENTACIÓN

### Sprint 1 (MVP) - 2 semanas
**Objetivo:** Sistema básico funcional para gestionar auditorías

- [x] Modelos de datos (Ya completado)
- [ ] Servicio de auditorías básico (`audit_service.py`)
- [ ] CRUD de auditorías (crear, listar, ver, editar)
- [ ] Gestión de hallazgos (crear, listar, ver)
- [ ] Vistas principales (lista, detalle)
- [ ] Generación de códigos únicos (AUD-YYYY-###)

**Entregables:**
- Crear auditoría con información básica
- Registrar hallazgos en auditoría
- Listar auditorías y hallazgos
- Vista de detalle de auditoría

### Sprint 2 - 2 semanas
**Objetivo:** Gestión completa del ciclo de auditoría

- [ ] Programa anual de auditorías
- [ ] Gestión de equipo auditor
- [ ] Acciones correctivas para hallazgos
- [ ] Transiciones de estado de auditoría
- [ ] Notificaciones por email básicas
- [ ] Validaciones de independencia

**Entregables:**
- Programa anual con calendario
- Asignación de equipo auditor
- Plan de acciones correctivas
- Workflow de estados completo

### Sprint 3 - 2 semanas
**Objetivo:** Documentación y seguimiento

- [ ] Gestión de documentos de auditoría
- [ ] Listas de verificación (checklists)
- [ ] Plantillas ISO 27001 predefinidas
- [ ] Generación de informe básico (PDF)
- [ ] Integración con SOA (controles ISO 27001)
- [ ] Métricas básicas (KPIs principales)

**Entregables:**
- Subir y gestionar documentos
- Ejecutar checklist ISO 27001
- Generar informe de auditoría PDF
- Dashboard con KPIs básicos

### Sprint 4 - 2 semanas
**Objetivo:** Funcionalidades avanzadas y optimización

- [ ] Validaciones completas de negocio
- [ ] Integraciones con otros módulos (Riesgos, NCs, Documentos)
- [ ] Dashboard completo con gráficos
- [ ] Automatizaciones (notificaciones, tareas programadas)
- [ ] Exportación de informes (Excel, PPT)
- [ ] Sistema de permisos por rol

**Entregables:**
- Todas las validaciones implementadas
- Dashboard interactivo completo
- Notificaciones automáticas
- Exportación de datos
- Sistema listo para producción

---

## 📚 CONSIDERACIONES TÉCNICAS

### Buenas Prácticas ISO 19011:2018

#### Principios de Auditoría
1. **Integridad:** Base de profesionalismo
2. **Presentación imparcial:** Obligación de informar con veracidad
3. **Debido cuidado profesional:** Aplicación de diligencia y juicio
4. **Confidencialidad:** Seguridad de la información
5. **Independencia:** Base de imparcialidad
6. **Enfoque basado en evidencia:** Método racional para conclusiones fiables

#### Gestión del Programa de Auditoría
- Establecer objetivos del programa
- Determinar y evaluar riesgos y oportunidades
- Establecer el programa de auditoría
- Implementar el programa
- Hacer seguimiento del programa
- Revisar y mejorar el programa

#### Actividades de Auditoría
1. **Inicio de auditoría**
   - Establecer contacto con el auditado
   - Determinar viabilidad de la auditoría

2. **Preparación de actividades de auditoría**
   - Revisión de información documentada
   - Planificación de auditoría
   - Asignación de trabajo al equipo auditor

3. **Realización de actividades de auditoría**
   - Reunión de apertura
   - Comunicación durante auditoría
   - Recopilación y verificación de evidencias
   - Generación de hallazgos
   - Preparación de conclusiones
   - Reunión de cierre

4. **Preparación y distribución del informe**

5. **Seguimiento de auditoría**

6. **Finalización de auditoría**

### Seguridad y Permisos

```python
ROLES_PERMISSIONS = {
    'ADMIN': {
        'audits': ['*'],  # Todos los permisos
        'programs': ['*'],
        'findings': ['*'],
        'actions': ['*']
    },
    'CISO': {
        'audits': ['view_all', 'create', 'edit', 'delete', 'approve'],
        'programs': ['view_all', 'create', 'edit', 'approve'],
        'findings': ['view_all', 'create', 'edit'],
        'actions': ['view_all', 'approve', 'verify']
    },
    'LEAD_AUDITOR': {
        'audits': ['view_assigned', 'view_all', 'create', 'edit', 'manage_team'],
        'programs': ['view_all'],
        'findings': ['create', 'edit', 'close'],
        'actions': ['view', 'approve']
    },
    'AUDITOR': {
        'audits': ['view_assigned', 'edit_assigned'],
        'programs': ['view'],
        'findings': ['create', 'edit_assigned'],
        'actions': ['view']
    },
    'AREA_MANAGER': {
        'audits': ['view_own_area'],
        'programs': ['view'],
        'findings': ['view_own_area', 'comment'],
        'actions': ['create', 'update_progress']
    },
    'USER': {
        'audits': ['view_public'],
        'programs': ['view'],
        'findings': ['view_assigned'],
        'actions': ['view_assigned', 'update_assigned']
    }
}
```

### Trazabilidad y Auditoría

```python
class AuditLog(db.Model):
    """Log de todas las acciones en auditorías"""
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    entity_type = db.Column(db.String(50))  # audit, finding, action
    entity_id = db.Column(db.Integer)
    action = db.Column(db.String(50))  # create, update, delete, status_change
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Datos del cambio
    old_value = db.Column(db.Text)
    new_value = db.Column(db.Text)
    field_changed = db.Column(db.String(100))

    # Contexto
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(255))

    def __repr__(self):
        return f'<AuditLog {self.entity_type}:{self.entity_id} {self.action}>'
```

**Eventos a registrar:**
- ✅ Creación de auditoría
- ✅ Cambios de estado
- ✅ Asignación de equipo auditor
- ✅ Creación de hallazgos
- ✅ Modificación de hallazgos
- ✅ Creación de acciones correctivas
- ✅ Aprobación de planes de acción
- ✅ Verificación de eficacia
- ✅ Cierre de hallazgos
- ✅ Generación de informes
- ✅ Aprobación de programas

### Versionado de Documentos

```python
class DocumentVersion(db.Model):
    """Control de versiones de documentos de auditoría"""
    __tablename__ = 'document_versions'

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('audit_documents.id'))
    document = db.relationship('AuditDocument')

    version_number = db.Column(db.String(20))  # 1.0, 1.1, 2.0
    file_path = db.Column(db.String(500))
    file_hash = db.Column(db.String(64))  # SHA-256

    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_by = db.relationship('User')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    change_notes = db.Column(db.Text)
    is_current = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<DocumentVersion {self.version_number}>'
```

### Backup y Recuperación

```python
# Configuración de backup automático
BACKUP_CONFIG = {
    'evidences': {
        'path': '/backups/audit_evidences',
        'frequency': 'daily',
        'retention_days': 1095  # 3 años
    },
    'documents': {
        'path': '/backups/audit_documents',
        'frequency': 'daily',
        'retention_days': 2555  # 7 años (requisito legal)
    },
    'reports': {
        'path': '/backups/audit_reports',
        'frequency': 'weekly',
        'retention_days': 3650  # 10 años
    }
}

def backup_audit_data(audit_id):
    """Crear backup completo de una auditoría"""
    audit = AuditRecord.query.get(audit_id)

    backup_data = {
        'audit': audit.to_dict(),
        'team': [member.to_dict() for member in audit.team_members],
        'findings': [finding.to_dict() for finding in audit.findings],
        'actions': [action.to_dict() for action in get_all_actions(audit)],
        'evidences': [evidence.to_dict() for evidence in audit.evidences],
        'documents': [doc.to_dict() for doc in audit.documents],
        'logs': [log.to_dict() for log in get_audit_logs(audit_id)]
    }

    # Guardar JSON
    backup_file = f"audit_{audit.audit_code}_backup_{datetime.now().strftime('%Y%m%d')}.json"
    save_backup(backup_data, backup_file)

    # Copiar archivos físicos
    copy_audit_files(audit_id)

    return backup_file
```

---

## 📝 PRÓXIMOS PASOS

### Checklist de Implementación

- [ ] **Sprint 1 - MVP (2 semanas)**
  - [ ] Crear servicio de auditorías
  - [ ] Implementar CRUD de auditorías
  - [ ] Implementar CRUD de hallazgos
  - [ ] Crear vistas principales
  - [ ] Testing básico

- [ ] **Sprint 2 - Ciclo Completo (2 semanas)**
  - [ ] Programa anual
  - [ ] Equipo auditor
  - [ ] Acciones correctivas
  - [ ] Estados y transiciones
  - [ ] Notificaciones

- [ ] **Sprint 3 - Documentación (2 semanas)**
  - [ ] Gestión documental
  - [ ] Listas de verificación
  - [ ] Plantillas ISO 27001
  - [ ] Generación de informes
  - [ ] Integración con SOA

- [ ] **Sprint 4 - Optimización (2 semanas)**
  - [ ] Validaciones completas
  - [ ] Integraciones con módulos
  - [ ] Dashboard y KPIs
  - [ ] Automatizaciones
  - [ ] Exportaciones

### Recursos Necesarios

**Desarrollo:**
- Desarrollador backend: 8 semanas
- Desarrollador frontend: 4 semanas
- Diseñador UX/UI: 1 semana

**Documentación:**
- Plantillas ISO 27001 Anexo A
- Guías de usuario
- Manual del auditor
- Procedimientos de auditoría

**Infraestructura:**
- Almacenamiento para documentos: 50 GB inicial
- Servidor de correo para notificaciones
- Librería de generación PDF (WeasyPrint/ReportLab)
- Sistema de tareas programadas (Celery/Cron)

---

## 🎓 FORMACIÓN REQUERIDA

### Para el Equipo de Desarrollo
- ISO/IEC 27001:2022 - Fundamentos
- ISO 19011:2018 - Guía de auditoría
- Procesos de auditoría interna
- Gestión de hallazgos y acciones correctivas

### Para los Usuarios Finales
- Uso del módulo de auditorías
- Creación y gestión de hallazgos
- Elaboración de informes
- Listas de verificación ISO 27001
- Gestión de acciones correctivas

---

## 📚 REFERENCIAS

### Normas Aplicables
- **ISO/IEC 27001:2023** - Sistemas de gestión de la seguridad de la información
- **ISO/IEC 27002:2022** - Código de prácticas para controles de seguridad de la información
- **ISO 19011:2018** - Directrices para la auditoría de sistemas de gestión
- **ISO 31000:2018** - Gestión del riesgo

### Documentación Adicional
- Guía de implementación ISO 27001
- Plantillas de auditoría ISO 27001
- Mejores prácticas de auditoría interna
- Casos de uso de SGSI

---

## 🔄 CONTROL DE VERSIONES

| Versión | Fecha | Autor | Cambios |
|---------|-------|-------|---------|
| 1.0 | 2025-10-17 | Claude | Plan inicial de implementación |

---

## ✅ ESTADO ACTUAL

**Modelos de datos:** ✅ Completado (100%)
**Servicios:** ⏳ Pendiente (0%)
**Controladores:** ⏳ Pendiente (0%)
**Vistas:** ⏳ Pendiente (0%)
**Integraciones:** ⏳ Pendiente (0%)

**Progreso global:** 10% completado

---

**Última actualización:** 2025-10-17
**Próxima revisión:** Al finalizar Sprint 1
