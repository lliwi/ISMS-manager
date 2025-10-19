# Guía de Uso: Sistema de Gestión de Tareas ISO 27001

## 🚀 Inicio Rápido

### Acceder al Sistema

1. **URL Principal:** `http://localhost/tareas`
2. **Usuario:** `admin` / **Contraseña:** `admin123`

### Primera Visualización

Al acceder verás:
- **Dashboard** con 4 métricas principales
- **Tareas Prioritarias** (si hay tareas críticas o de alta prioridad)
- **Mis Tareas Asignadas** (tabla con tus tareas)
- **Distribución por Categoría** (resumen ISO 27001)

## 📋 Funcionalidades Principales

### 1. Ver Plantillas de Tareas

**Navegación:** Tareas → Plantillas

Aquí encontrarás las **15 plantillas predefinidas ISO 27001**:

- Revisión Trimestral de Controles (9.1)
- Auditoría Interna Semestral (9.2)
- Evaluación Anual de Riesgos (8.2)
- Revisión de Políticas (5.1)
- Concienciación en Seguridad (7.2/7.3)
- Y más...

**Acciones disponibles:**
- 👁️ Ver detalles de la plantilla
- ✏️ Editar plantilla (admin/CISO)
- ▶️ Generar tarea ahora

### 2. Generar Tarea Desde Plantilla

1. Ir a **Plantillas**
2. Localizar la plantilla deseada
3. Clic en el botón **▶️** (Generar)
4. Se crea automáticamente una tarea con:
   - Fecha de vencimiento calculada según frecuencia
   - Usuario/Rol asignado por defecto
   - Checklist predefinida
   - Toda la configuración de la plantilla

### 3. Crear Tarea Manual

**Navegación:** Tareas → Nueva Tarea

**Campos del formulario:**
- **Título:** Nombre descriptivo de la tarea
- **Descripción:** Detalles y objetivos
- **Categoría:** Seleccionar del listado ISO 27001
- **Prioridad:** Baja, Media, Alta, Crítica
- **Asignada a:** Usuario responsable
- **Fecha de vencimiento:** Cuándo debe completarse
- **Control ISO:** Número del control (ej: 9.1, 5.18)
- **Horas estimadas:** Tiempo estimado de ejecución
- **Lista de verificación:** Items a completar (uno por línea)

**Ejemplo de checklist:**
```
- Revisar configuración del firewall
- Verificar logs de acceso
- Actualizar documentación
- Realizar pruebas
```

### 4. Trabajar en una Tarea

#### Ver Detalles
1. Clic en el título de la tarea
2. Verás toda la información:
   - Estado actual y progreso
   - Descripción completa
   - Checklist (si existe)
   - Evidencias adjuntas
   - Comentarios
   - Historial de cambios

#### Actualizar Progreso
1. Botón **Actualizar Tarea**
2. Modificar:
   - Estado (Pendiente → En Progreso)
   - Progreso (0-100%)
   - Observaciones
   - Horas reales trabajadas

#### Adjuntar Evidencia
1. Botón **Subir Evidencia**
2. Seleccionar archivo
3. Agregar descripción
4. Upload

**Tipos de archivos soportados:**
- PDF, DOC, DOCX
- XLS, XLSX
- TXT
- Imágenes (PNG, JPG)

#### Comentar
- Escribir comentario en el campo inferior
- Útil para:
  - Preguntas al responsable
  - Aclaraciones
  - Notas de progreso
  - Comunicación con auditor

### 5. Completar Tarea

1. Botón **Completar**
2. Formulario de finalización:
   - **Observaciones:** Comentarios finales
   - **Resultado:** Conclusión de la tarea
   - **Horas reales:** Tiempo efectivo empleado

3. Al completar:
   - Estado → COMPLETADA
   - Progreso → 100%
   - Fecha de finalización registrada
   - Notificación enviada al creador

### 6. Vista de Calendario

**Navegación:** Tareas → Calendario

**Funcionalidades:**
- **Calendario mensual** con todas las tareas
- **Navegación** mes anterior/siguiente
- **Colores por prioridad:**
  - 🟥 Rojo: Crítica/Alta
  - 🟨 Amarillo: Media
  - 🟩 Verde: Baja
  - 🟪 Tachado: Completada

- **Sidebar derecho:**
  - Tareas del mes actual
  - Próximas a vencer

- **Interacción:**
  - Clic en tarea → Ver detalles

### 7. Filtros y Búsqueda

**Filtros disponibles:**
- **Estado:** Pendiente, En Progreso, Completada, Vencida
- **Prioridad:** Todas, Crítica, Alta, Media, Baja
- **Categoría:** 17 categorías ISO 27001

**Aplicar filtros:**
- Seleccionar opciones
- Auto-submit al cambiar

## 🔔 Sistema de Notificaciones

### Tipos de Notificaciones

Recibirás emails automáticos en estos casos:

1. **Nueva Asignación**
   - Cuando se te asigna una tarea
   - Incluye todos los detalles
   - Link directo a la tarea

2. **Recordatorios**
   - 7 días antes del vencimiento
   - 3 días antes
   - 1 día antes
   - El día del vencimiento

3. **Tarea Vencida**
   - Notificación diaria mientras esté vencida

4. **Resumen Semanal**
   - Cada lunes a las 09:00
   - Resumen de todas tus tareas pendientes
   - Tareas vencidas
   - Próximas a vencer

### Ver Emails (Desarrollo)

Durante desarrollo, los emails se envían a **MailHog**:

**URL:** `http://localhost:8025`

Aquí puedes ver todos los emails enviados sin que lleguen a emails reales.

## 🤖 Automatización (Jobs Programados)

El sistema ejecuta automáticamente estas tareas:

### 1. Generación Diaria (00:00)
- Revisa todas las plantillas activas
- Genera tareas según frecuencia
- Asigna automáticamente

### 2. Actualización de Vencidas (Cada hora)
- Marca tareas vencidas automáticamente
- Cambia estado: PENDIENTE → VENCIDA

### 3. Procesamiento de Notificaciones (Cada 30 min)
- Revisa tareas que necesitan notificación
- Envía recordatorios según días faltantes
- Registra envíos en base de datos

### 4. Resumen Semanal (Lunes 09:00)
- Genera resumen para cada usuario activo
- Solo si tiene tareas pendientes
- Incluye métricas personales

### 5. Generación Mensual (Día 1 a las 00:00)
- Genera tareas mensuales del mes
- Útil para tareas recurrentes

## 📊 Métricas y Estadísticas

### Dashboard Principal

**4 Tarjetas de Métricas:**

1. **Tareas Pendientes** (Azul)
   - Tareas en estado PENDIENTE
   - Asignadas a ti

2. **En Progreso** (Celeste)
   - Tareas que estás trabajando
   - Estado EN_PROGRESO

3. **Vencidas** (Rojo)
   - Tareas con fecha pasada
   - Sin completar

4. **Completadas (mes)** (Verde)
   - Tareas finalizadas este mes
   - Indicador de productividad

### Distribución por Categoría

**Gráfico inferior** muestra cuántas tareas hay por cada categoría ISO 27001:

- Revisión de Controles
- Auditoría Interna
- Evaluación de Riesgos
- Y más...

Útil para identificar áreas con más carga de trabajo.

## 🔐 Permisos por Rol

### Administrador (admin)
- ✅ Ver todas las tareas
- ✅ Crear tareas manuales
- ✅ Crear/Editar plantillas
- ✅ Generar desde plantillas
- ✅ Reasignar tareas
- ✅ Eliminar tareas

### CISO (ciso)
- ✅ Ver todas las tareas
- ✅ Crear tareas
- ✅ Crear/Editar plantillas
- ✅ Aprobar tareas críticas
- ✅ Generar reportes

### Auditor Interno (auditor)
- ✅ Ver tareas asignadas
- ✅ Ver historial completo
- ✅ Agregar comentarios
- ✅ Revisar evidencias

### Propietario de Proceso (owner)
- ✅ Ver tareas de su área
- ✅ Crear tareas manuales
- ✅ Actualizar progreso
- ✅ Completar tareas

### Usuario General (user)
- ✅ Ver tareas asignadas
- ✅ Actualizar progreso
- ✅ Adjuntar evidencias
- ✅ Completar tareas

## 💡 Mejores Prácticas

### 1. Actualización Regular
- Actualiza el progreso semanalmente
- Mantén el % de progreso actualizado
- Agrega comentarios sobre avances

### 2. Evidencias
- Adjunta evidencias durante el trabajo, no al final
- Usa nombres descriptivos
- Agrega descripción a cada archivo

### 3. Comunicación
- Usa comentarios para preguntas
- Menciona problemas encontrados
- Documenta decisiones importantes

### 4. Checklist
- Marca items conforme los completes
- Útil para no olvidar pasos
- Facilita revisión de auditorías

### 5. Vencimientos
- No ignores recordatorios
- Si no puedes completar a tiempo:
  - Comunícalo en comentarios
  - Solicita extensión al responsable

### 6. Completar Tareas
- Completa solo cuando REALMENTE finalices
- Agrega observaciones relevantes
- Documenta el resultado obtenido
- Verifica que todas las evidencias estén adjuntas

## 🐛 Solución de Problemas

### No recibo notificaciones
**Verificar:**
1. Tu email está configurado en tu perfil
2. MailHog está corriendo: `http://localhost:8025`
3. Variable `TASK_NOTIFICATION_ENABLED=True`

### No veo mis tareas
**Verificar:**
1. Filtros aplicados (Estado, Prioridad)
2. Usuario asignado correcto
3. Permisos de tu rol

### No puedo crear tareas
**Verificar:**
1. Tu rol (debe ser admin/ciso/owner)
2. Sesión activa
3. Formulario completo (campos obligatorios)

### Error al subir evidencia
**Verificar:**
1. Tamaño del archivo < 16MB
2. Formato permitido (PDF, DOC, XLS, TXT, IMG)
3. Espacio en disco

## 📞 Soporte

Para más información consulta:

- **Documentación Técnica:** `docs/IMPLEMENTACION_COMPLETADA_TAREAS.md`
- **Plan de Implementación:** `docs/PLAN_GESTION_TAREAS.md`
- **Logs del Sistema:** `docker-compose logs web`
- **Base de Datos:** `docker-compose exec db psql -U isms -d isms_db`

---

**Guía de Usuario - Sistema de Gestión de Tareas**
**Versión:** 1.0.0
**Fecha:** Octubre 2025
