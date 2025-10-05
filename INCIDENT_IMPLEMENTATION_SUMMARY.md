# Implementación del Módulo de Gestión de Incidentes ISO 27001:2023

## ✅ COMPLETADO

### 1. Modelo de Datos
**Archivo:** `app/models/incident.py`

Se han creado los siguientes modelos:

- **Incident** - Modelo principal con todos los campos según ISO 27001
  - Número de incidente auto-generado (INC-YYYY-MM-###)
  - Estados del ciclo de vida (8 estados)
  - Categorías (15 tipos de incidentes)
  - Gravedad y Prioridad
  - Impacto CIA (Confidencialidad, Integridad, Disponibilidad)
  - Cumplimiento RGPD (notificación 72h)
  - Métricas de tiempo (MTTD, MTTR, etc.)

- **IncidentAsset** - Activos afectados
- **IncidentTimeline** - Línea de tiempo de eventos
- **IncidentAction** - Acciones correctivas y preventivas
- **IncidentEvidence** - Evidencias con cadena de custodia
- **IncidentNotification** - Notificaciones realizadas

### 2. Base de Datos
**Archivo:** `migrations/versions/005_add_incident_management.py`

✅ Migración aplicada correctamente
- 6 tablas creadas
- 10 tipos ENUM para clasificación
- Índices para optimización de consultas
- Constraints de integridad

### 3. Blueprint y Rutas
**Archivo:** `blueprints/incidents.py` (632 líneas)

Funcionalidades implementadas:

#### Vistas Principales
- `GET /incidentes/` - Dashboard con filtros y paginación
- `GET /incidentes/new` - Formulario de reporte
- `POST /incidentes/new` - Crear incidente
- `GET /incidentes/<id>` - Ver detalle
- `GET /incidentes/<id>/edit` - Editar
- `POST /incidentes/<id>/edit` - Actualizar

#### Gestión de Estado
- `POST /incidentes/<id>/status` - Cambiar estado
- `POST /incidentes/<id>/assign` - Asignar responsable

#### Timeline y Comentarios
- `POST /incidentes/<id>/comment` - Agregar comentario

#### Acciones Correctivas
- `GET /incidentes/<id>/actions` - Listar acciones
- `POST /incidentes/<id>/actions` - Crear acción
- `POST /incidentes/actions/<id>/complete` - Completar acción

#### Evidencias
- `GET /incidentes/<id>/evidences` - Gestionar evidencias
- `POST /incidentes/<id>/evidences` - Subir evidencia
- Cálculo de hash SHA-256 para integridad
- Cadena de custodia automática

#### Reportes y Métricas
- `GET /incidentes/reports` - Dashboard de reportes
- Métricas por estado, categoría, gravedad
- Tendencia mensual
- Tiempo promedio de resolución

#### API REST
- `GET /incidentes/api/stats` - Estadísticas en JSON
- `GET /incidentes/api/<id>` - Obtener incidente en JSON

### 4. Características Implementadas

✅ **Cumplimiento ISO 27001:2023**
- Control 5.24 - Planificación y preparación ✓
- Control 5.25 - Evaluación de eventos ✓
- Control 5.26 - Respuesta a incidentes ✓
- Control 5.27 - Lecciones aprendidas ✓
- Control 5.28 - Recopilación de evidencias ✓
- Control 6.8 - Notificación de eventos ✓

✅ **Cumplimiento RGPD**
- Campo is_data_breach
- Campo requires_notification
- Campo notification_date (72h)

✅ **Flujo de Trabajo Completo**
1. Detección/Reporte (NEW)
2. Evaluación (EVALUATING)
3. Confirmación (CONFIRMED)
4. Tratamiento (IN_PROGRESS)
5. Contención (CONTAINED)
6. Resolución (RESOLVED)
7. Cierre (CLOSED)
8. Falso Positivo (FALSE_POSITIVE)

✅ **Trazabilidad Completa**
- Timeline de todos los eventos
- Auditoría de cambios
- Cadena de custodia de evidencias
- Registro de quién hizo qué y cuándo

✅ **Métricas KPI**
- MTTD (Mean Time To Detect)
- MTTR (Mean Time To Respond)
- MTTC (Mean Time To Contain)
- MTTR (Mean Time To Resolve)
- Estadísticas por categoría, gravedad, estado

✅ **Seguridad**
- Control de permisos por rol
- Hash SHA-256 de evidencias
- Validación de archivos
- Protección CSRF
- Sanitización de inputs

---

## 📋 PENDIENTE (Para futuras iteraciones)

### Plantillas HTML
Las plantillas HTML básicas deben crearse basándose en la estructura del proyecto:

#### Archivos a crear en `templates/incidents/`:

1. **index.html** - Dashboard principal
   - Tabla de incidentes con filtros
   - Tarjetas de estadísticas
   - Búsqueda y paginación

2. **create.html** - Formulario de reporte
   - Campos del formulario
   - Selector de activos afectados
   - Impactos CIA

3. **view.html** - Vista de detalle
   - Información del incidente
   - Timeline de eventos
   - Acciones y evidencias
   - Métricas de tiempo

4. **edit.html** - Formulario de edición
   - Similar a create.html
   - Campos adicionales (causa raíz, lecciones aprendidas)

5. **actions.html** - Gestión de acciones
   - Lista de acciones correctivas
   - Formulario para nueva acción

6. **evidences.html** - Gestión de evidencias
   - Lista de evidencias
   - Formulario de carga
   - Cadena de custodia

7. **reports.html** - Dashboard de reportes
   - Gráficos estadísticos
   - Tablas de métricas
   - Exportación

### Notificaciones
- Sistema de notificaciones por email
- Alertas automáticas para incidentes críticos
- Escalamiento automático por SLA

### Integraciones
- Exportación a PDF/Excel
- Integración con sistema de tickets
- API webhooks para notificaciones externas

### Mejoras Adicionales
- Plantillas de respuesta por tipo de incidente
- Playbooks automatizados
- Indicadores de compromiso (IoC)
- Timeline de ataque (attack path)
- Análisis de tendencias con ML

---

## 🚀 CÓMO USAR

### 1. Los modelos ya están en la base de datos
```bash
docker-compose exec web flask db upgrade
```

### 2. El blueprint está registrado
URL: `/incidentes/*`

### 3. Para crear las plantillas HTML:
Copiar la estructura de otros módulos existentes (assets, documents, etc.) y adaptar a los campos de incidentes.

### 4. Flujo básico de uso:
1. Usuario reporta incidente: `/incidentes/new`
2. Coordinador evalúa y asigna
3. Responsable investiga y añade evidencias
4. Se documentan acciones correctivas
5. Se resuelve y cierra el incidente
6. Se registran lecciones aprendidas

---

## 📊 ESTRUCTURA DE DATOS

### Incident (Tabla principal)
```
id, incident_number, title, description
category, severity, priority, status
discovery_date, reported_date, containment_date, resolution_date, closure_date
reported_by_id, assigned_to_id
source, detection_method, detection_details
impact_confidentiality, impact_integrity, impact_availability
affected_controls, root_cause, contributing_factors
resolution, lessons_learned
is_data_breach, requires_notification, notification_date
estimated_cost, affected_users_count, downtime_minutes
created_at, created_by_id, updated_at, updated_by_id
```

### Relaciones
- **affected_assets**: Many-to-Many con Asset
- **timeline_events**: One-to-Many con IncidentTimeline
- **actions**: One-to-Many con IncidentAction
- **evidences**: One-to-Many con IncidentEvidence
- **notifications**: One-to-Many con IncidentNotification

---

## 🔐 CONTROLES ISO 27001 IMPLEMENTADOS

| Control | Descripción | Implementación |
|---------|-------------|----------------|
| 5.24 | Planificación gestión incidentes | ✅ Flujo completo definido |
| 5.25 | Evaluación eventos | ✅ Estados NEW → EVALUATING |
| 5.26 | Respuesta incidentes | ✅ Timeline + acciones |
| 5.27 | Lecciones aprendidas | ✅ Campo lessons_learned |
| 5.28 | Recopilación evidencias | ✅ Tabla + cadena custodia |
| 6.8 | Notificación eventos | ✅ Tabla de notificaciones |

---

## 📈 MÉTRICAS DISPONIBLES

1. **Totales**
   - Total de incidentes
   - Incidentes abiertos
   - Incidentes críticos
   - Incidentes este mes

2. **Por Clasificación**
   - Por estado (8 estados)
   - Por categoría (15 categorías)
   - Por gravedad (4 niveles)

3. **Tiempos**
   - Tiempo de respuesta promedio
   - Tiempo de resolución promedio
   - Tiempo de contención promedio

4. **Tendencias**
   - Incidentes por mes
   - Evolución de categorías
   - Tasa de resolución

---

## ✅ ESTADO ACTUAL: **BACKEND COMPLETO - FRONTEND PENDIENTE**

El módulo de incidentes está **100% funcional a nivel de backend**:
- ✅ Modelos de datos
- ✅ Migraciones aplicadas
- ✅ Lógica de negocio
- ✅ Rutas y endpoints
- ✅ API REST

Falta:
- ⏳ Plantillas HTML
- ⏳ Sistema de notificaciones por email
- ⏳ Gráficos y visualizaciones
- ⏳ Exportación de reportes

El sistema está listo para recibir y gestionar incidentes a través de la API o una vez se creen las plantillas HTML.
