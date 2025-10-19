# Plan de Implementación: Módulo de Gestión de Tareas ISO 27001

## 1. INTRODUCCIÓN

Este documento define la implementación del módulo de Gestión de Tareas Periódicas para el Sistema de Gestión de Seguridad de la Información (SGSI), cumpliendo con los requisitos de la norma **ISO/IEC 27001:2023**.

### 1.1 Objetivos

- Automatizar el seguimiento de tareas periódicas del SGSI
- Garantizar el cumplimiento de controles ISO 27001
- Proporcionar trazabilidad y evidencias para auditorías
- Mejorar la eficiencia en la gestión operacional del SGSI

### 1.2 Requisitos ISO 27001 Aplicables

| Requisito | Descripción | Relación con Tareas |
|-----------|-------------|---------------------|
| **6.2** | Objetivos de seguridad y planificación | Planificación de tareas de seguridad |
| **8.1** | Planificación y control operacional | Procedimientos operacionales documentados |
| **9.1** | Seguimiento, medición, análisis y evaluación | Tareas de monitorización de controles |
| **9.2** | Auditoría interna | Programación de auditorías |
| **9.3** | Revisión por la dirección | Tareas de revisión periódica |
| **Control 5.37** | Documentación de procedimientos operacionales | Registro de ejecución de procedimientos |

---

## 2. ARQUITECTURA DEL MÓDULO

### 2.1 Componentes Principales

```
┌─────────────────────────────────────────────────────────────┐
│                    MÓDULO DE TAREAS                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │   Plantillas   │  │    Tareas    │  │  Notificaciones │ │
│  │   de Tareas    │  │  Periódicas  │  │    por Email    │ │
│  └────────────────┘  └──────────────┘  └─────────────────┘ │
│                                                              │
│  ┌────────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │   Evidencias   │  │  Comentarios │  │    Historial    │ │
│  │  y Documentos  │  │              │  │   de Cambios    │ │
│  └────────────────┘  └──────────────┘  └─────────────────┘ │
│                                                              │
│  ┌────────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │   Dashboard    │  │   Reportes   │  │   Calendario    │ │
│  │   de Tareas    │  │              │  │                 │ │
│  └────────────────┘  └──────────────┘  └─────────────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Modelo de Datos

#### Entidades Principales

1. **TaskTemplate** - Plantillas de tareas recurrentes
2. **Task** - Instancias de tareas
3. **TaskEvidence** - Evidencias documentales
4. **TaskComment** - Comentarios y comunicación
5. **TaskHistory** - Historial de cambios
6. **TaskNotificationLog** - Registro de notificaciones

#### Enumeraciones

- **TaskFrequency**: Diaria, Semanal, Mensual, Trimestral, Semestral, Anual, etc.
- **TaskStatus**: Pendiente, En Progreso, Completada, Vencida, Cancelada
- **TaskPriority**: Baja, Media, Alta, Crítica
- **TaskCategory**: 17 categorías basadas en controles ISO 27001

---

## 3. CATEGORÍAS DE TAREAS ISO 27001

### 3.1 Catálogo de Tareas Periódicas

| Categoría | Control ISO | Frecuencia Típica | Responsable |
|-----------|-------------|-------------------|-------------|
| **Revisión de Controles** | 9.1 | Trimestral | CISO / Propietarios |
| **Auditoría Interna** | 9.2 | Semestral/Anual | Auditor Interno |
| **Evaluación de Riesgos** | 8.2 | Anual | CISO |
| **Revisión de Políticas** | 5.1 | Anual | CISO |
| **Formación y Concienciación** | 7.2, 7.3 | Trimestral | RRHH/CISO |
| **Mantenimiento de Seguridad** | 7.13 | Mensual | Responsable TI |
| **Copias de Seguridad** | 8.13 | Semanal | Responsable TI |
| **Revisión de Accesos** | 5.18 | Trimestral | CISO |
| **Actualización Inventarios** | 5.9 | Mensual | Propietarios |
| **Revisión Proveedores** | 5.22 | Semestral | CISO |
| **Gestión Vulnerabilidades** | 8.8 | Mensual | Responsable TI |
| **Revisión Incidentes** | 5.27 | Trimestral | CISO |
| **Continuidad de Negocio** | 5.30 | Anual | CISO |
| **Revisión Legal** | 5.31 | Anual | Legal/CISO |
| **Revisión por Dirección** | 9.3 | Semestral | Alta Dirección |
| **Pruebas Recuperación** | 8.14 | Anual | Responsable TI |

### 3.2 Plantillas Predefinidas

#### Ejemplo: Revisión Trimestral de Controles

```yaml
Título: Revisión Trimestral de Controles de Seguridad
Descripción: Verificación de la eficacia de los controles implementados
Categoría: REVISION_CONTROLES
Frecuencia: TRIMESTRAL
Prioridad: ALTA
Control ISO: 9.1
Responsable: CISO
Duración Estimada: 8 horas
Requiere Evidencia: Sí
Requiere Aprobación: Sí

Checklist:
  ☐ Revisar controles de acceso implementados
  ☐ Verificar registros de auditoría
  ☐ Comprobar actualizaciones de seguridad
  ☐ Revisar incidentes de seguridad del período
  ☐ Evaluar eficacia de los controles
  ☐ Documentar hallazgos y recomendaciones
  ☐ Presentar informe a la dirección
```

---

## 4. SISTEMA DE NOTIFICACIONES

### 4.1 Configuración SMTP

**Servicio de Correo**: MailHog (desarrollo) / SMTP Externo (producción)

**Variables de Entorno**:
```bash
MAIL_SERVER=mailhog              # Servidor SMTP
MAIL_PORT=1025                    # Puerto SMTP
MAIL_USE_TLS=False               # TLS habilitado
MAIL_USE_SSL=False               # SSL habilitado
MAIL_USERNAME=                    # Usuario SMTP
MAIL_PASSWORD=                    # Contraseña SMTP
MAIL_DEFAULT_SENDER=sgsi@empresa.com
TASK_NOTIFICATION_ENABLED=True
```

**MailHog** (Desarrollo):
- Interfaz Web: http://localhost:8025
- SMTP: localhost:1025
- Captura todos los emails enviados
- No requiere configuración externa

### 4.2 Tipos de Notificaciones

| Tipo | Cuándo se Envía | Destinatarios |
|------|----------------|---------------|
| **Asignación** | Al asignar tarea | Usuario asignado |
| **Recordatorio** | 7, 3, 1 días antes | Usuario asignado |
| **Vencimiento** | En fecha de vencimiento | Usuario asignado + Superior |
| **Vencida** | Diariamente si está vencida | Usuario asignado + Superior |
| **Completada** | Al completar tarea | Creador + Aprobador (si aplica) |
| **Aprobada/Rechazada** | Tras aprobación | Usuario asignado |
| **Resumen Semanal** | Lunes 9:00 AM | Todos con tareas pendientes |
| **Resumen Mensual** | Día 1 de mes | CISO + Alta Dirección |

### 4.3 Plantillas de Email

#### Recordatorio de Tarea

```
Asunto: Recordatorio: [TÍTULO TAREA] - Vence en X días

Hola [NOMBRE],

Tienes una tarea del SGSI pendiente que vence pronto:

Tarea: [TÍTULO]
Categoría: [CATEGORÍA]
Prioridad: [PRIORIDAD]
Vencimiento: [FECHA]
Días restantes: X

Descripción:
[DESCRIPCIÓN]

Por favor, accede al sistema para completar esta tarea:
[ENLACE DIRECTO A LA TAREA]

---
Sistema de Gestión de Seguridad de la Información
ISO/IEC 27001:2023
```

---

## 5. FLUJO DE TRABAJO

### 5.1 Ciclo de Vida de una Tarea

```
┌──────────────┐
│   CREACIÓN   │ ← Desde plantilla o manual
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  PENDIENTE   │ ← Estado inicial
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  ASIGNACIÓN  │ ← Asignar a usuario/rol
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ EN PROGRESO  │ ← Usuario trabaja en la tarea
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  COMPLETADA  │ ← Marcar como completada
└──────┬───────┘
       │
       ├─── Requiere Aprobación? ───┐
       │                              │
       NO                            SÍ
       │                              │
       ▼                              ▼
┌──────────────┐            ┌──────────────┐
│   CERRADA    │            │  APROBACIÓN  │
└──────────────┘            └──────┬───────┘
                                   │
                       ┌───────────┴───────────┐
                       │                       │
                   APROBADA                RECHAZADA
                       │                       │
                       ▼                       ▼
                ┌──────────────┐        ┌──────────────┐
                │   CERRADA    │        │ EN PROGRESO  │
                └──────────────┘        └──────────────┘
```

### 5.2 Generación Automática de Tareas

**Proceso Automático** (Scheduler - Cron):
1. **Diariamente a las 00:00**: Generar tareas del día según plantillas
2. **Semanalmente Lunes 00:00**: Generar tareas semanales
3. **Mensualmente día 1 00:00**: Generar tareas mensuales
4. **Verificación de vencimientos**: Cada hora
5. **Envío de notificaciones**: Cada 30 minutos

```python
# Ejemplo de generación automática
def generate_periodic_tasks():
    """Genera tareas periódicas según plantillas activas"""
    templates = TaskTemplate.query.filter_by(is_active=True).all()

    for template in templates:
        # Verificar si toca generar tarea según frecuencia
        if should_generate_task(template):
            task = Task(
                template_id=template.id,
                title=template.title,
                description=template.description,
                category=template.category,
                priority=template.priority,
                due_date=template.calculate_next_due_date(),
                assigned_to_id=template.default_assignee_id,
                assigned_role_id=template.default_role_id,
                iso_control=template.iso_control,
                requires_approval=template.requires_approval,
                checklist=template.checklist_template
            )
            db.session.add(task)

            # Enviar notificación de asignación
            send_task_assignment_email(task)

    db.session.commit()
```

---

## 6. INTERFACES DE USUARIO

### 6.1 Pantallas Principales

#### 6.1.1 Dashboard de Tareas

**Elementos**:
- **Resumen de Tareas**:
  - Tareas pendientes
  - Tareas vencidas
  - Tareas en progreso
  - Tareas completadas (mes actual)

- **Gráficos**:
  - Tareas por estado (pie chart)
  - Tareas por categoría (bar chart)
  - Evolución mensual (line chart)
  - Cumplimiento por responsable (bar chart)

- **Calendario**:
  - Vista mensual con tareas
  - Código de colores por prioridad
  - Filtros por categoría/responsable

#### 6.1.2 Lista de Tareas

**Características**:
- Tabla con paginación
- Filtros: Estado, Categoría, Prioridad, Responsable, Fecha
- Ordenación: Por vencimiento, prioridad, creación
- Búsqueda: Por título, descripción, control ISO
- Acciones rápidas: Completar, Asignar, Ver detalles
- Exportar: PDF, Excel

#### 6.1.3 Detalle de Tarea

**Secciones**:
1. **Información General**
   - Título, descripción, categoría
   - Prioridad, estado, progreso
   - Control ISO relacionado

2. **Asignación y Fechas**
   - Asignado a
   - Fecha de vencimiento
   - Fecha de inicio
   - Fecha de completado

3. **Checklist**
   - Lista de verificación interactiva
   - Progreso automático

4. **Evidencias**
   - Carga de archivos
   - Visualización de documentos
   - Descarga

5. **Comentarios**
   - Hilo de conversación
   - Menciones @usuario

6. **Historial**
   - Todos los cambios
   - Quién, cuándo, qué

#### 6.1.4 Gestión de Plantillas

**Funcionalidades**:
- CRUD de plantillas
- Activar/Desactivar
- Clonar plantilla
- Vista previa de tareas generadas
- Simulación de calendario

---

## 7. CONTROL DE ACCESO

### 7.1 Permisos por Rol

| Acción | Admin | CISO | Auditor | Propietario | Usuario |
|--------|-------|------|---------|-------------|---------|
| Crear plantilla | ✓ | ✓ | - | - | - |
| Editar plantilla | ✓ | ✓ | - | - | - |
| Eliminar plantilla | ✓ | ✓ | - | - | - |
| Crear tarea manual | ✓ | ✓ | ✓ | ✓ | - |
| Asignar tarea | ✓ | ✓ | ✓ | ✓ | - |
| Ver todas las tareas | ✓ | ✓ | ✓ | ✓ | - |
| Ver mis tareas | ✓ | ✓ | ✓ | ✓ | ✓ |
| Completar tarea asignada | ✓ | ✓ | ✓ | ✓ | ✓ |
| Aprobar tarea | ✓ | ✓ | - | ✓ | - |
| Ver reportes | ✓ | ✓ | ✓ | ✓ | - |
| Configurar notificaciones | ✓ | ✓ | - | - | - |

---

## 8. REPORTES Y MÉTRICAS

### 8.1 Indicadores Clave (KPIs)

1. **Tasa de Cumplimiento**
   ```
   (Tareas Completadas a Tiempo / Total Tareas) × 100
   ```

2. **Tiempo Promedio de Ejecución**
   ```
   Σ(Fecha Completado - Fecha Asignación) / Número de Tareas
   ```

3. **Tareas Vencidas**
   ```
   Tareas con Estado=Vencida
   ```

4. **Eficiencia por Categoría**
   ```
   Cumplimiento % por cada categoría ISO 27001
   ```

5. **Carga de Trabajo por Usuario**
   ```
   Número de tareas asignadas por usuario
   ```

### 8.2 Reportes Predefinidos

1. **Reporte Mensual de Cumplimiento**
   - Tareas completadas vs planificadas
   - Tareas vencidas
   - Tendencias
   - Por categoría ISO 27001

2. **Reporte de Auditoría**
   - Todas las tareas con evidencias
   - Historial completo
   - Exportable para auditorías externas

3. **Reporte de Desempeño por Usuario**
   - Tareas asignadas
   - Tareas completadas
   - Tiempo promedio
   - Calificación de cumplimiento

4. **Reporte de Controles ISO 27001**
   - Estado de cumplimiento por control
   - Próximas revisiones
   - Hallazgos recurrentes

---

## 9. INTEGRACIÓN CON OTROS MÓDULOS

### 9.1 Módulo de Auditorías

- Generar tareas desde hallazgos de auditoría
- Vincular tareas a acciones correctivas
- Seguimiento de cierre de NC

### 9.2 Módulo de Riesgos

- Generar tareas desde tratamiento de riesgos
- Tareas de revisión periódica de riesgos
- Actualización de evaluaciones

### 9.3 Módulo de Incidentes

- Tareas de análisis post-incidente
- Implementación de lecciones aprendidas
- Revisiones de seguridad

### 9.4 Módulo de Documentos

- Adjuntar documentos como evidencias
- Tareas de revisión de documentos
- Actualización de políticas

---

## 10. PLAN DE IMPLEMENTACIÓN

### 10.1 Fases del Proyecto

#### **Fase 1: Modelos y Base de Datos** (COMPLETADO)
- ✅ Definición de modelos SQLAlchemy
- ✅ Migraciones de base de datos
- ✅ Configuración SMTP en Docker Compose

#### **Fase 2: Backend - API y Lógica de Negocio** (PRÓXIMO)
- Crear blueprint `/tasks`
- Implementar rutas CRUD
- Desarrollar generador automático de tareas
- Implementar sistema de notificaciones
- Pruebas unitarias

#### **Fase 3: Frontend - Interfaces de Usuario**
- Templates HTML base
- Dashboard de tareas
- Lista y detalle de tareas
- Gestión de plantillas
- Calendario de tareas

#### **Fase 4: Notificaciones y Automatización**
- Servicio de email
- Scheduler (APScheduler o Celery)
- Cron jobs
- Webhooks

#### **Fase 5: Reportes e Integración**
- Generación de reportes
- Exportación PDF/Excel
- Integración con otros módulos
- Pruebas de integración

#### **Fase 6: Pruebas y Despliegue**
- Pruebas funcionales
- Pruebas de carga
- Documentación de usuario
- Capacitación
- Despliegue en producción

### 10.2 Cronograma Estimado

| Fase | Duración | Inicio | Fin |
|------|----------|--------|-----|
| Fase 1 | 2 días | Completado | Completado |
| Fase 2 | 5 días | - | - |
| Fase 3 | 7 días | - | - |
| Fase 4 | 4 días | - | - |
| Fase 5 | 5 días | - | - |
| Fase 6 | 5 días | - | - |
| **TOTAL** | **28 días** | - | - |

---

## 11. CONFIGURACIÓN DE PRODUCCIÓN

### 11.1 Servidor SMTP Externo

Para producción, configurar un servicio SMTP profesional:

**Opciones Recomendadas**:
- SendGrid
- Amazon SES
- Mailgun
- SMTP Office 365/Gmail

**Ejemplo de Configuración** (.env):
```bash
# Producción - SendGrid
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=apikey
MAIL_PASSWORD=SG.xxxxxxxxxxxxx
MAIL_DEFAULT_SENDER=sgsi@tu-empresa.com
MAIL_MAX_EMAILS=100
TASK_NOTIFICATION_ENABLED=True
```

### 11.2 Scheduler de Tareas

**Opción 1: APScheduler** (Recomendado para aplicaciones medianas)
```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(
    func=generate_periodic_tasks,
    trigger="cron",
    hour=0,
    minute=0
)
scheduler.start()
```

**Opción 2: Celery** (Recomendado para aplicaciones grandes)
```python
from celery import Celery

celery = Celery('tasks', broker='redis://localhost:6379')

@celery.task
def generate_periodic_tasks():
    # ... implementación
    pass

# Configurar Celery Beat para tareas periódicas
```

---

## 12. SEGURIDAD Y CUMPLIMIENTO

### 12.1 Medidas de Seguridad

1. **Autenticación y Autorización**
   - Solo usuarios autenticados
   - Control de acceso basado en roles (RBAC)
   - Validación de permisos en cada acción

2. **Protección de Datos**
   - Cifrado en tránsito (HTTPS)
   - Cifrado de archivos sensibles en reposo
   - Validación de uploads (tipo, tamaño)

3. **Auditoría**
   - Log completo de todas las acciones
   - Registro de IP y timestamp
   - Historial inmutable

4. **Email Seguro**
   - No incluir información sensible en emails
   - Solo enlaces a la aplicación
   - Autenticación requerida para ver tareas

### 12.2 Cumplimiento ISO 27001

| Control | Implementación en Tareas |
|---------|--------------------------|
| **5.2** | Asignación clara de responsabilidades |
| **5.37** | Documentación de procedimientos operacionales |
| **7.5** | Control de información documentada (evidencias) |
| **8.1** | Planificación y control operacional |
| **9.1** | Seguimiento y medición de controles |

---

## 13. PRÓXIMOS PASOS

### Tareas Inmediatas

1. ✅ Crear modelos de base de datos
2. ✅ Configurar SMTP en Docker Compose
3. ⏳ Crear blueprint y rutas
4. ⏳ Implementar servicios de email
5. ⏳ Desarrollar templates HTML
6. ⏳ Implementar generador automático

### Recomendaciones

- Iniciar con un conjunto reducido de plantillas
- Realizar pruebas con usuarios piloto
- Documentar lecciones aprendidas
- Iterar basándose en feedback
- Capacitar a usuarios antes del lanzamiento

---

## ANEXOS

### Anexo A: Estructura de Directorios

```
/app
  /models
    task.py                    # Modelos de tareas
  /routes
    /tasks
      __init__.py             # Blueprint principal
      views.py                # Rutas de vistas
      api.py                  # API REST
  /services
    task_service.py           # Lógica de negocio
    notification_service.py   # Sistema de notificaciones
    scheduler_service.py      # Generación automática
  /templates
    /tasks
      dashboard.html
      list.html
      detail.html
      template_list.html
      calendar.html
  /static
    /js
      /tasks
        task.js
        calendar.js
    /css
      /tasks
        tasks.css
```

### Anexo B: Variables de Entorno

```bash
# SMTP Configuration
MAIL_SERVER=mailhog
MAIL_PORT=1025
MAIL_USE_TLS=False
MAIL_USE_SSL=False
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_DEFAULT_SENDER=sgsi@empresa.com
MAIL_MAX_EMAILS=100

# Task Configuration
TASK_NOTIFICATION_ENABLED=True
TASK_AUTO_GENERATION_ENABLED=True
TASK_SCHEDULER_INTERVAL=3600  # segundos
```

### Anexo C: Ejemplo de Migración

```python
# migrations/versions/xxx_add_task_tables.py

def upgrade():
    # Crear tablas de tareas
    op.create_table('task_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        # ... más columnas
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('tasks',
        # ... definición completa
    )

    # ... más tablas

def downgrade():
    op.drop_table('tasks')
    op.drop_table('task_templates')
    # ... más drops
```

---

**Documento elaborado por:** Sistema ISMS Manager
**Fecha:** 2025-10-19
**Versión:** 1.0
**Estado:** BORRADOR
**Basado en:** ISO/IEC 27001:2023
