# Módulo de Gestión de Cambios - ISMS Manager

## Resumen

Este documento describe el módulo de **Gestión de Cambios** implementado según la norma ISO 27001:2023, específicamente los controles 6.3 (Planificación de cambios) y 8.32 (Gestión de cambios).

## Controles ISO 27001:2023 Implementados

### Control 6.3 - Planificación de cambios
- Cambios en el SGSI planificados y llevados a cabo de manera controlada
- Revisión de las consecuencias de los cambios
- Documentación completa del cambio y sus impactos
- Programación y planificación de cambios

### Control 8.32 - Gestión de cambios
- Gestión de cambios en instalaciones y sistemas de procesamiento de información
- Procedimientos documentados para el control de cambios
- Evaluación de impactos potenciales de seguridad
- Revisión y aprobación formal de cambios
- Comunicación de cambios a las partes relevantes
- Procedimientos de retroceso

## Arquitectura del Módulo

### Archivos Creados

```
app/
├── models/
│   └── change.py                       # Modelos de base de datos
├── services/
│   ├── change_service.py              # Lógica de negocio
│   └── change_workflow.py             # Máquina de estados y workflow
├── blueprints/
│   └── changes.py                     # Rutas y controladores
└── templates/
    └── changes/
        ├── index.html                 # Listado de cambios
        ├── form.html                  # Formulario crear/editar
        ├── detail.html                # Vista detallada del cambio
        └── calendar.html              # Vista de calendario

migrations/
└── versions/
    └── 008_add_change_management_tables.py  # Migración de base de datos
```

## Modelos de Base de Datos

### Enumeraciones

#### ChangeType (11 tipos)
- INFRASTRUCTURE: Infraestructura
- APPLICATION: Aplicación
- NETWORK: Red
- SECURITY: Seguridad
- PROCESS: Proceso
- POLICY: Política
- ORGANIZATIONAL: Organizacional
- HARDWARE: Hardware
- SOFTWARE: Software
- CONFIGURATION: Configuración
- OTHER: Otro

#### ChangeCategory (4 categorías ITIL v4)
- **MINOR**: Bajo riesgo, bajo impacto, aprobación simplificada
- **STANDARD**: Pre-autorizado, procedimiento estándar conocido
- **MAJOR**: Alto impacto, requiere aprobación CAB completa
- **EMERGENCY**: Urgente, proceso acelerado para mitigar incidentes

#### ChangePriority (4 niveles)
- LOW: Baja
- MEDIUM: Media
- HIGH: Alta
- CRITICAL: Crítica

#### ChangeStatus (14 estados del ciclo de vida)
1. **DRAFT**: Borrador inicial
2. **SUBMITTED**: Enviado para revisión
3. **UNDER_REVIEW**: En revisión
4. **APPROVED**: Aprobado
5. **REJECTED**: Rechazado
6. **SCHEDULED**: Programado
7. **IN_PROGRESS**: En progreso
8. **IMPLEMENTING**: Implementando
9. **IMPLEMENTED**: Implementado
10. **VERIFIED**: Verificado
11. **SUCCESSFUL**: Exitoso
12. **FAILED**: Fallido
13. **ROLLED_BACK**: Revertido
14. **CLOSED**: Cerrado
15. **CANCELLED**: Cancelado

#### RiskLevel (4 niveles)
- LOW: Bajo (probabilidad × impacto ≤ 6)
- MEDIUM: Medio (7-12)
- HIGH: Alto (13-20)
- CRITICAL: Crítico (>20)

#### ApprovalLevel (5 niveles)
- TECHNICAL: Aprobación técnica
- SECURITY: Aprobación de seguridad
- MANAGEMENT: Aprobación de gestión
- CAB: Change Advisory Board
- CISO: Responsable de Seguridad de la Información

### Tablas

#### 1. changes (Tabla principal)
Campos principales:
- `change_code`: Código único (CHG-2025-0001)
- `title`: Título del cambio
- `description`: Descripción detallada
- `change_type`, `category`, `priority`, `status`
- `business_justification`: Justificación de negocio (requerido)
- `expected_benefits`: Beneficios esperados
- `impact_analysis`: Análisis de impacto
- `implementation_plan`: Plan de implementación (requerido)
- `rollback_plan`: Plan de retroceso (requerido)
- `test_plan`: Plan de pruebas
- `communication_plan`: Plan de comunicación
- `scheduled_start_date`, `scheduled_end_date`: Fechas programadas
- `actual_start_date`, `actual_end_date`: Fechas reales
- `estimated_duration`: Duración estimada (horas)
- `estimated_cost`: Costo estimado
- `downtime_required`: Requiere inactividad
- `estimated_downtime_minutes`: Tiempo de inactividad estimado
- `affects_development`, `affects_testing`, `affects_production`: Entornos afectados
- `requester_id`, `owner_id`: Solicitante y responsable
- `related_incident_id`, `related_nonconformity_id`: Relaciones

#### 2. change_approvals
Sistema de aprobaciones multi-nivel:
- `change_id`: Cambio relacionado
- `approver_id`: Aprobador
- `approval_level`: Nivel de aprobación
- `approved`: True/False/None (pendiente)
- `comments`: Comentarios
- `decision_date`: Fecha de decisión

#### 3. change_tasks
Tareas de implementación:
- `change_id`: Cambio relacionado
- `description`: Descripción de la tarea
- `assigned_to_id`: Responsable
- `is_critical`: Si es crítica (debe completarse obligatoriamente)
- `completed`: Estado de completitud
- `completed_at`: Fecha de completitud

#### 4. change_documents
Documentos adjuntos:
- `change_id`: Cambio relacionado
- `file_name`, `file_path`, `file_size`, `mime_type`
- `uploaded_by_id`, `uploaded_at`

#### 5. change_history
Auditoría completa (Control 7.5.3):
- `change_id`: Cambio relacionado
- `user_id`: Usuario que realizó la acción
- `action`: Acción realizada
- `old_status`, `new_status`: Estados anterior y nuevo
- `comments`: Comentarios

#### 6. change_reviews
Post-Implementation Review (PIR):
- `change_id`: Cambio relacionado
- `reviewer_id`: Revisor
- `review_date`: Fecha de revisión
- `objectives_met`: ¿Se cumplieron los objetivos?
- `review_summary`: Resumen de la revisión
- `lessons_learned`: Lecciones aprendidas
- `issues_encountered`: Problemas encontrados
- `recommendations`: Recomendaciones

#### 7. change_risk_assessments
Evaluación de riesgos (matriz 5×5):
- `change_id`: Cambio relacionado
- `probability`: Probabilidad (1-5)
- `impact`: Impacto (1-5)
- `risk_level`: Nivel de riesgo calculado
- `risk_description`: Descripción del riesgo
- `mitigation_plan`: Plan de mitigación

#### 8. change_assets (many-to-many)
Relación con activos afectados:
- `change_id`, `asset_id`

## Servicios de Lógica de Negocio

### ChangeService

Métodos principales:

1. **create_change(data, current_user_id)**: Crea un nuevo cambio con código auto-generado
2. **update_change(change_id, data)**: Actualiza un cambio existente
3. **delete_change(change_id)**: Elimina un cambio (solo si está en DRAFT)
4. **get_change(change_id)**: Obtiene un cambio por ID
5. **list_changes(filters, page, per_page)**: Lista cambios con filtros y paginación
6. **submit_for_review(change_id, current_user_id)**: Envía para revisión (DRAFT → SUBMITTED)
7. **approve(change_id, approver_id, comments, level)**: Aprueba un cambio
8. **reject(change_id, approver_id, reason)**: Rechaza un cambio
9. **schedule(change_id, start_date, end_date)**: Programa un cambio
10. **start_implementation(change_id, current_user_id)**: Inicia implementación
11. **complete_implementation(change_id, current_user_id)**: Completa implementación
12. **verify_success(change_id, current_user_id)**: Verifica éxito
13. **mark_failed(change_id, current_user_id, reason)**: Marca como fallido
14. **rollback(change_id, current_user_id, reason)**: Ejecuta retroceso
15. **close(change_id, current_user_id, comments)**: Cierra el cambio
16. **cancel(change_id, current_user_id, reason)**: Cancela el cambio
17. **add_task(change_id, data)**: Añade tarea de implementación
18. **complete_task(task_id, user_id)**: Completa una tarea
19. **add_risk_assessment(change_id, data)**: Añade evaluación de riesgos
20. **create_pir(change_id, data)**: Crea revisión post-implementación
21. **get_dashboard_stats()**: Obtiene estadísticas del dashboard
22. **get_upcoming_changes(days)**: Obtiene cambios próximos
23. **get_pending_approvals(user_id)**: Obtiene aprobaciones pendientes

### ChangeWorkflow

Métodos principales:

1. **can_transition(change, new_status)**: Valida si la transición es válida
2. **validate_transition_requirements(change, new_status)**: Valida requisitos para transición
3. **get_next_approval_level(change)**: Obtiene siguiente nivel de aprobación requerido
4. **requires_cab_approval(change)**: Determina si requiere aprobación CAB
5. **calculate_risk_score(probability, impact)**: Calcula puntuación de riesgo
6. **get_risk_level(score)**: Obtiene nivel de riesgo

Transiciones válidas definidas en `TRANSITIONS` dict.

## Rutas y Endpoints

### Vistas principales
- `GET /cambios/`: Listado de cambios con filtros
- `GET /cambios/new`: Formulario de nuevo cambio
- `POST /cambios/new`: Crear nuevo cambio
- `GET /cambios/<id>`: Detalle del cambio
- `GET /cambios/<id>/edit`: Editar cambio
- `POST /cambios/<id>/edit`: Guardar edición
- `GET /cambios/calendar`: Vista de calendario

### Acciones de workflow
- `POST /cambios/<id>/submit`: Enviar para revisión
- `POST /cambios/<id>/approve`: Aprobar
- `POST /cambios/<id>/reject`: Rechazar
- `POST /cambios/<id>/schedule`: Programar
- `POST /cambios/<id>/start`: Iniciar implementación
- `POST /cambios/<id>/complete`: Completar implementación
- `POST /cambios/<id>/verify`: Verificar éxito
- `POST /cambios/<id>/fail`: Marcar como fallido
- `POST /cambios/<id>/rollback`: Retroceder
- `POST /cambios/<id>/close`: Cerrar
- `POST /cambios/<id>/cancel`: Cancelar

### Gestión de tareas
- `GET /cambios/<id>/tasks/new`: Nueva tarea
- `POST /cambios/<id>/tasks/new`: Crear tarea
- `POST /cambios/<id>/tasks/<task_id>/complete`: Completar tarea

### Evaluación de riesgos
- `GET /cambios/<id>/risk/new`: Nueva evaluación de riesgos
- `POST /cambios/<id>/risk/new`: Crear evaluación

### Post-Implementation Review
- `GET /cambios/<id>/pir/new`: Nueva PIR
- `POST /cambios/<id>/pir/new`: Crear PIR

### APIs
- `GET /cambios/api/pending-approvals`: Aprobaciones pendientes del usuario

## Templates HTML

### index.html
- 4 tarjetas de estadísticas (Total, Pendientes, Programados, Este Mes)
- Filtros avanzados (estado, categoría, prioridad, tipo, búsqueda)
- Tabla sorteable y paginada
- Badges con colores por categoría

### form.html
Secciones:
1. **Información Básica**: título, descripción, tipo, categoría, prioridad
2. **Justificación**: justificación de negocio, beneficios, análisis de impacto
3. **Planes**: implementación, retroceso, pruebas, comunicación
4. **Programación**: fechas, duración, costo
5. **Entornos**: desarrollo, pruebas, producción
6. **Tiempo de Inactividad**: requerido, duración estimada
7. **Responsables**: solicitante, responsable

### detail.html
Muestra:
- Información completa del cambio
- Botones de acciones según estado y permisos
- Timeline de aprobaciones
- Tareas de implementación
- Evaluaciones de riesgos
- Post-Implementation Review
- Historial completo de cambios
- Metadata y relaciones

Modales para:
- Aprobar/Rechazar
- Programar
- Retroceder
- Cerrar
- Cancelar

### calendar.html
- Calendario FullCalendar con eventos
- Filtros por categoría, prioridad, entorno
- Leyenda de colores
- Lista de próximos cambios programados
- Iconos para producción e inactividad

## Instalación y Configuración

### 1. Ejecutar Migración de Base de Datos

```bash
# Asegúrate de estar en el directorio del proyecto
cd "/home/llibert/Documents/development/flask/ISMS Manager"

# Ejecuta la migración
flask db upgrade
```

Esto creará las siguientes tablas:
- changes
- change_approvals
- change_tasks
- change_documents
- change_history
- change_reviews
- change_risk_assessments
- change_assets

Y los siguientes ENUM types:
- changetype
- changecategory
- changepriority
- changestatus
- risklevel
- approvallevel
- approvalstatus

### 2. Verificar Registro del Blueprint

El blueprint ya está registrado en `application.py`:

```python
from app.blueprints.changes import changes_bp
app.register_blueprint(changes_bp, url_prefix='/cambios')
```

### 3. Añadir al Menú de Navegación

Edita el archivo `app/templates/base.html` o el archivo de navegación correspondiente y añade:

```html
<li class="nav-item">
    <a class="nav-link" href="{{ url_for('changes.index') }}">
        <i class="fas fa-exchange-alt me-2"></i>
        Gestión de Cambios
    </a>
</li>
```

### 4. Permisos de Usuario

El módulo utiliza los roles existentes del sistema:
- **admin**: Acceso completo
- **ciso**: Aprobaciones de alto nivel, puede cerrar cambios
- **owner**: Puede crear, editar y gestionar cambios
- **auditor**: Solo lectura para auditoría
- **user**: Puede crear cambios básicos

## Flujo de Trabajo Típico

### Cambio Estándar

1. Usuario crea cambio en estado **DRAFT**
2. Usuario completa formulario y envía → **SUBMITTED**
3. Sistema evalúa nivel de aprobación requerido → **UNDER_REVIEW**
4. Aprobaciones técnicas y de seguridad → **APPROVED**
5. Responsable programa el cambio → **SCHEDULED**
6. En fecha programada, inicia implementación → **IN_PROGRESS**
7. Ejecuta tareas de implementación → **IMPLEMENTING**
8. Completa implementación → **IMPLEMENTED**
9. Verifica que funciona correctamente → **SUCCESSFUL**
10. Completa PIR y cierra → **CLOSED**

### Cambio de Emergencia

1. Usuario crea cambio con categoría **EMERGENCY**
2. Envía para revisión → **SUBMITTED**
3. Aprobación acelerada (puede ser post-implementación) → **APPROVED**
4. Implementa inmediatamente → **IN_PROGRESS** → **IMPLEMENTING**
5. Completa y verifica → **IMPLEMENTED** → **SUCCESSFUL**
6. Documentación post-implementación y PIR → **CLOSED**

### Cambio Fallido con Retroceso

1. Durante implementación se detecta problema
2. Se ejecuta plan de retroceso → **ROLLED_BACK**
3. Se analiza causa del fallo
4. Se cierra con lecciones aprendidas → **CLOSED**

## Mejores Prácticas

### Documentación de Cambios

1. **Título claro y descriptivo**: "Actualización de servidor PostgreSQL 14 a 15"
2. **Justificación de negocio completa**: explicar el "por qué"
3. **Plan de implementación detallado**: paso a paso
4. **Plan de retroceso viable**: siempre debe existir
5. **Análisis de impacto realista**: no subestimar riesgos

### Evaluación de Riesgos

- Utilizar matriz de probabilidad × impacto (1-5)
- Documentar todos los riesgos identificados
- Definir planes de mitigación para riesgos altos
- Revisar riesgos antes de aprobación final

### Aprobaciones

- Cambios MINOR: aprobación técnica
- Cambios STANDARD: aprobación técnica + seguridad
- Cambios MAJOR: aprobación completa CAB
- Cambios EMERGENCY: aprobación acelerada (puede ser posterior)

### Post-Implementation Review (PIR)

- Ejecutar siempre después de cambios MAJOR
- Recomendable para cambios STANDARD con incidencias
- Documentar lecciones aprendidas
- Actualizar procedimientos basándose en experiencia

## Compliance ISO 27001:2023

### Control 6.3 - Planificación de cambios
✅ Cambios planificados y controlados
✅ Revisión de consecuencias
✅ Documentación completa
✅ Programación adecuada

### Control 8.32 - Gestión de cambios
✅ Procedimientos documentados
✅ Evaluación de impactos de seguridad (change_risk_assessments)
✅ Aprobación formal (change_approvals)
✅ Comunicación a partes relevantes (communication_plan)
✅ Procedimientos de retroceso (rollback_plan)

### Control 7.5.3 - Control de la información documentada
✅ Auditoría completa (change_history)
✅ Trazabilidad de cambios
✅ Registro de aprobaciones

### Controles relacionados
- **5.8**: Gestión de activos (relación con change_assets)
- **8.1**: Dispositivos de punto final de usuario (cambios en hardware)
- **8.19**: Instalación de software en sistemas operacionales (cambios en software)
- **8.31**: Separación de entornos de desarrollo, prueba y producción (affects_*)

## Mantenimiento y Soporte

### Estadísticas y KPIs

El servicio proporciona métricas útiles:
- Total de cambios
- Cambios por estado
- Cambios programados
- Tasa de éxito/fallo
- Tiempo promedio de implementación
- Cambios por categoría

### Monitorización

Consultas útiles:

```python
# Cambios con aprobaciones pendientes
Change.query.join(ChangeApproval).filter(
    ChangeApproval.approved == None
).all()

# Cambios próximos en 7 días
ChangeService.get_upcoming_changes(days=7)

# Cambios fallidos en el último mes
Change.query.filter(
    Change.status == ChangeStatus.FAILED,
    Change.actual_end_date >= datetime.now() - timedelta(days=30)
).all()
```

### Logs y Auditoría

Todas las acciones quedan registradas en `change_history`:
- Cambios de estado
- Aprobaciones/Rechazos
- Modificaciones de datos
- Usuario y timestamp de cada acción

## Testing

### Tests Unitarios Recomendados

1. **Modelo Change**: validaciones, métodos, propiedades
2. **ChangeService**: todas las operaciones CRUD
3. **ChangeWorkflow**: transiciones de estado, validaciones
4. **Rutas**: respuestas HTTP, permisos, formularios

### Tests de Integración

1. Flujo completo de cambio exitoso
2. Flujo de cambio con retroceso
3. Sistema de aprobaciones multi-nivel
4. Validaciones de transición de estado

## Próximas Mejoras

### Funcionalidades Adicionales

1. **Notificaciones por email**: alertas en cambios de estado
2. **Dashboard de métricas**: gráficos y tendencias
3. **Exportación a PDF**: documentación completa del cambio
4. **Plantillas de cambios**: para cambios recurrentes
5. **Change Advisory Board (CAB) virtual**: reuniones y votaciones
6. **Integración con calendario corporativo**: Outlook, Google Calendar
7. **Conflictos de programación**: detectar solapamientos
8. **Tiempo de mantenimiento**: ventanas de cambio predefinidas

### Optimizaciones

1. Caché de estadísticas
2. Búsqueda full-text en cambios
3. Filtros guardados por usuario
4. Vistas personalizadas

## Soporte

Para problemas o preguntas sobre el módulo de Gestión de Cambios:

1. Revisar logs en `change_history`
2. Verificar permisos de usuario
3. Comprobar estado del cambio y transiciones válidas
4. Consultar este documento

## Referencias

- **ISO/IEC 27001:2023**: Sección 6.3 y Anexo A Control 8.32
- **ITIL v4**: Change Management (categorías y workflows)
- **NIST SP 800-53**: CM (Configuration Management)

---

**Fecha de creación**: 2025-10-15
**Versión**: 1.0
**Autor**: ISMS Manager Development Team
