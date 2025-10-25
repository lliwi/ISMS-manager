# Funcionalidad: Gestión de Catálogo de Amenazas MAGERIT

## Resumen

Se ha implementado un módulo completo de administración para el catálogo de amenazas MAGERIT 3.2, accesible desde **http://localhost/admin/settings** → **Catálogo de Amenazas**.

---

## Características Implementadas

### ✅ 1. Listado de Amenazas
**URL**: `http://localhost/admin/settings/amenazas`

**Funcionalidades**:
- Vista de tabla con todas las amenazas configuradas
- Filtros por grupo (NATURALES, INDUSTRIALES, ERRORES, ATAQUES)
- Búsqueda por código, nombre o descripción
- Estadísticas por grupo con contadores
- Visualización de dimensiones CIA afectadas
- Contador de controles y riesgos asociados
- Acciones: Ver, Editar, Eliminar

**Vista previa**:
```
┌─────────────────────────────────────────────────────┐
│ 🔥 NATURALES (10)  🏭 INDUSTRIALES (15)            │
│ 👤 ERRORES (20)    🔫 ATAQUES (30)                 │
└─────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────┐
│ Código │ Nombre        │ Grupo      │ Dimensiones  │
│ A.25   │ Robo de eq... │ ATAQUES    │ C I D        │
│ N.1    │ Fuego         │ NATURALES  │ I D          │
└─────────────────────────────────────────────────────┘
```

---

### ✅ 2. Crear Nueva Amenaza
**URL**: `http://localhost/admin/settings/amenazas/new`

**Campos del formulario**:
- **Código*** (ej: A.25, N.1, I.6, E.1)
- **Nombre*** (ej: "Robo de equipos o documentos")
- **Descripción** (texto largo)
- **Grupo*** (NATURALES, INDUSTRIALES, ERRORES, ATAQUES)
- **Categoría MAGERIT** (clasificación adicional)
- **Dimensiones CIA***:
  - ☑ Confidencialidad (C)
  - ☑ Integridad (I)
  - ☑ Disponibilidad (D)

**Validaciones**:
- Código único (no duplicados)
- Al menos una dimensión CIA debe estar seleccionada
- Campos obligatorios marcados con *

**Panel de ayuda**:
- Explicación de códigos MAGERIT
- Ejemplos de amenazas
- Definición de dimensiones CIA

---

### ✅ 3. Editar Amenaza Existente
**URL**: `http://localhost/admin/settings/amenazas/<id>/edit`

**Funcionalidades**:
- Pre-poblado con datos actuales
- Validación de código único (excepto el propio)
- Verificación de dimensiones CIA
- Información de metadatos (fecha creación/actualización)

---

### ✅ 4. Ver Detalle de Amenaza
**URL**: `http://localhost/admin/settings/amenazas/<id>`

**Información mostrada**:

#### Información General
- Código y nombre
- Grupo (con badge de color)
- Categoría MAGERIT
- Dimensiones afectadas (badges CIA)
- Descripción completa

#### Controles Asociados
Tabla con controles del catálogo `controles_amenazas`:
- Código del control (ej: A.5.1)
- Nombre del control SOA
- Tipo (PREVENTIVO, REACTIVO, DETECTIVE)
- Efectividad (%)

#### Riesgos Asociados
Lista de riesgos que usan esta amenaza:
- Código del riesgo
- Activo afectado
- Dimensión
- Riesgo intrínseco
- Riesgo efectivo
- Limitado a 10 primeros (con contador total)

#### Panel Lateral
- **Estadísticas**: Controles, Riesgos, Recursos asociados
- **Metadatos**: ID, fechas de creación/actualización
- **Acciones**: Editar, Eliminar (con validación)

---

### ✅ 5. Eliminar Amenaza
**URL**: `POST /admin/settings/amenazas/<id>/delete`

**Validaciones de seguridad**:
- ❌ No se puede eliminar si tiene riesgos asociados
- ⚠️ Advertencia si tiene controles asociados
- ✅ Solo admin puede eliminar
- Confirmación JavaScript antes de eliminar

**Mensaje de error típico**:
```
No se puede eliminar la amenaza A.25 porque está
siendo usada en 156 riesgo(s)
```

---

## Archivos Creados/Modificados

### Backend (Python)

#### `/app/blueprints/admin.py`
**Cambios**:
- Importado modelo `Amenaza` de `app.risks.models`
- Agregado contador `amenazas_count` en vista `settings()`
- Nuevas rutas:
  - `@admin_bp.route('/settings/amenazas')` - Listado
  - `@admin_bp.route('/settings/amenazas/new')` - Crear
  - `@admin_bp.route('/settings/amenazas/<id>/edit')` - Editar
  - `@admin_bp.route('/settings/amenazas/<id>')` - Ver detalle
  - `@admin_bp.route('/settings/amenazas/<id>/delete')` - Eliminar

**Líneas modificadas**: 3-4, 438, 1030-1265

---

### Frontend (Templates)

#### `/app/templates/admin/settings.html`
**Cambios**:
- Agregada tarjeta "Catálogo de Amenazas" con:
  - Icono: `fa-exclamation-triangle`
  - Color: rojo (danger)
  - Contador: `{{ amenazas_count }}`
  - Botón: "Gestionar Catálogo de Amenazas"

**Líneas agregadas**: 139-168

#### `/app/templates/admin/amenazas.html` (NUEVO)
**Contenido**: 230 líneas
- Listado completo de amenazas
- Filtros por grupo y búsqueda
- Tarjetas de estadísticas por grupo
- Tabla responsive con acciones
- Script de confirmación de eliminación

#### `/app/templates/admin/amenaza_form.html` (NUEVO)
**Contenido**: 185 líneas
- Formulario de creación/edición
- Validación JavaScript de dimensiones CIA
- Panel de ayuda lateral
- Información de metadatos (en edición)

#### `/app/templates/admin/view_amenaza.html` (NUEVO)
**Contenido**: 280 líneas
- Vista detallada completa
- Tablas de controles y riesgos asociados
- Panel lateral con estadísticas y acciones
- Script de confirmación de eliminación

---

## Integración con Módulo de Riesgos

### Flujo de Uso

```
┌─────────────────────┐
│  Admin configura    │
│  Catálogo MAGERIT   │
│  (Amenazas)         │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│  Gestor de Riesgos  │
│  crea catálogo      │
│  Controles-Amenazas │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│  Sistema calcula    │
│  riesgos basándose  │
│  en controles SOA   │
└─────────────────────┘
```

### Relaciones en Base de Datos

```sql
amenazas
  ├── id, codigo, nombre, descripcion
  ├── grupo, categoria_magerit
  ├── afecta_confidencialidad
  ├── afecta_integridad
  └── afecta_disponibilidad
      │
      ├──→ controles_amenazas (N:M)
      │     ├── control_codigo
      │     ├── tipo_control
      │     └── efectividad
      │         │
      │         └──→ soa_controls (lectura madurez)
      │
      └──→ riesgos (1:N)
            ├── nivel_riesgo_intrinseco
            ├── nivel_riesgo_efectivo
            └── clasificacion_efectiva
```

---

## Permisos y Roles

| Acción | Admin | CISO | Auditor | Owner | User |
|--------|-------|------|---------|-------|------|
| **Listar amenazas** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Ver detalle** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Crear amenaza** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Editar amenaza** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Eliminar amenaza** | ✅ | ❌ | ❌ | ❌ | ❌ |

**Decoradores aplicados**:
- Listado/Ver/Crear/Editar: `@role_required('admin', 'ciso')`
- Eliminar: `@role_required('admin')`

---

## Ejemplos de Uso

### Crear Amenaza "Robo de Equipos"

1. Acceder a `http://localhost/admin/settings`
2. Click en "Gestionar Catálogo de Amenazas"
3. Click en "Nueva Amenaza"
4. Llenar formulario:
   ```
   Código: A.25
   Nombre: Robo de equipos o documentos
   Descripción: Sustracción física de equipos informáticos,
                dispositivos móviles o documentos...
   Grupo: ATAQUES
   Categoría: Robo

   Dimensiones:
   ☑ Confidencialidad (pérdida de información)
   ☑ Integridad (no aplicable)
   ☑ Disponibilidad (pérdida de acceso)
   ```
5. Click en "Crear Amenaza"

### Buscar Amenazas de Tipo "Fuego"

1. Acceder a listado de amenazas
2. En campo de búsqueda escribir: `fuego`
3. Sistema filtra: `N.1 - Fuego` y resultados relacionados

### Ver Impacto de una Amenaza

1. Click en botón "Ver detalle" (👁️) de cualquier amenaza
2. Revisar sección "Riesgos Asociados"
3. Ver cuántos riesgos activos usan esta amenaza
4. Ver controles que la mitigan

---

## Validaciones y Protecciones

### Validaciones de Backend
- ✅ Código único por amenaza
- ✅ Campos obligatorios: código, nombre, grupo
- ✅ Al menos una dimensión CIA debe estar seleccionada
- ✅ Grupo debe ser uno de los 4 predefinidos

### Validaciones de Frontend
- ✅ JavaScript valida dimensiones antes de enviar
- ✅ Campos required en HTML5
- ✅ Maxlength en campos de texto
- ✅ Confirmación antes de eliminar

### Protecciones de Integridad
- ❌ No eliminar si tiene riesgos asociados
- ⚠️ Advertir si tiene controles asociados
- ✅ CSRF token en todos los formularios
- ✅ Sanitización de entrada vía Flask

---

## Catálogo MAGERIT 3.2 Predefinido

El sistema viene con amenazas precargadas en `init_sql.sql`:

### Naturales (N.*)
- N.1 - Fuego
- N.2 - Daños por agua

### Industriales (I.*)
- I.1 - Contaminación mecánica
- I.2 - Contaminación electromagnética
- I.6 - **Corte del suministro eléctrico**
- I.10 - Degradación de los soportes de almacenamiento

### Errores (E.*)
- E.1 - **Errores de los usuarios**
- E.2 - Errores del administrador
- E.15 - Alteración de la información
- E.18 - Destrucción de la información
- E.19 - Fugas de información
- E.23 - Errores de mantenimiento
- E.25 - Indisponibilidad del personal

### Ataques (A.*)
- A.11 - **Acceso no autorizado**
- A.15 - Modificación deliberada de la información
- A.18 - **Destrucción de información**
- A.19 - Divulgación de información
- A.22 - Manipulación de programas
- A.23 - Manipulación de los equipos
- A.24 - **Denegación de servicio**
- A.25 - **Robo de equipos o documentos**
- A.26 - Ataque destructivo
- A.27 - Ocupación enemiga
- A.28 - Indisponibilidad del personal
- A.29 - Extorsión
- A.30 - Ingeniería social

**Total inicial**: ~25 amenazas predefinidas

---

## Comandos Útiles

### Verificar amenazas en BD
```bash
docker exec ismsmanager-web-1 bash -c "PGPASSWORD=isms_secure_password psql -h db -U isms -d isms_db -c 'SELECT codigo, nombre, grupo FROM amenazas ORDER BY codigo;'"
```

### Contar amenazas por grupo
```bash
docker exec ismsmanager-web-1 bash -c "PGPASSWORD=isms_secure_password psql -h db -U isms -d isms_db -c 'SELECT grupo, COUNT(*) FROM amenazas GROUP BY grupo;'"
```

### Ver amenazas con controles
```bash
docker exec ismsmanager-web-1 bash -c "PGPASSWORD=isms_secure_password psql -h db -U isms -d isms_db -c 'SELECT a.codigo, a.nombre, COUNT(ca.id) AS controles FROM amenazas a LEFT JOIN controles_amenazas ca ON ca.amenaza_id = a.id GROUP BY a.id ORDER BY controles DESC LIMIT 10;'"
```

---

## Próximos Pasos Recomendados

### 1. Completar Catálogo MAGERIT
- ✅ Agregar las ~70 amenazas restantes de MAGERIT 3.2
- Categorizar todas correctamente
- Documentar cada amenaza

### 2. Integración con Matriz de Controles
- Vincular amenazas con controles ISO 27002:2022
- Definir efectividades por defecto
- Automatizar sugerencias de controles

### 3. Dashboard de Amenazas
- Gráfico de distribución por grupo
- Top amenazas más frecuentes
- Heat map de amenazas vs activos

### 4. Exportación/Importación
- Exportar catálogo a Excel/CSV
- Importar amenazas masivamente
- Compartir catálogos entre instalaciones

---

## Problemas Conocidos y Soluciones

### ⚠️ No se puede eliminar amenaza con riesgos

**Problema**: Al intentar eliminar una amenaza que tiene riesgos asociados, el sistema muestra error.

**Solución esperada**: Este es el comportamiento correcto. Primero se deben eliminar o reasignar los riesgos.

**Workaround**:
```sql
-- Ver qué riesgos usan la amenaza
SELECT * FROM riesgos WHERE amenaza_id = X;

-- Eliminar riesgos (si es apropiado)
DELETE FROM riesgos WHERE amenaza_id = X;
```

---

## Conclusión

✅ **Módulo completamente funcional** para la gestión del catálogo de amenazas MAGERIT 3.2

✅ **Integrado** con el módulo de gestión de riesgos existente

✅ **Interfaz intuitiva** siguiendo el mismo diseño del sistema

✅ **Validaciones robustas** para mantener integridad referencial

✅ **Listo para producción** y uso inmediato

---

**Fecha**: 2025-10-25
**Versión**: 1.0
**Autor**: Implementación técnica - ISMS Manager
**URL**: http://localhost/admin/settings → Catálogo de Amenazas
