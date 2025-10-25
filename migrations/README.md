# Migraciones SQL - ISMS Manager

## ¿Necesito ejecutar estas migraciones?

### 🆕 Instalaciones Nuevas (desde cero)

**Respuesta: NO**

Las migraciones SQL **NO son necesarias** en instalaciones nuevas porque:

1. **SQLAlchemy crea las tablas automáticamente** con la estructura correcta
2. El código en `application.py:93` ejecuta `db.create_all()` que crea todas las tablas basándose en los modelos actuales
3. Los modelos en `app/risks/models.py` ya tienen la estructura actualizada

**Proceso de instalación nueva**:
```bash
docker-compose up -d
# ✅ Tablas creadas automáticamente con estructura correcta
# ✅ Sin necesidad de ejecutar migraciones
```

---

### 🔄 Instalaciones Existentes (actualizaciones)

**Respuesta: SÍ (algunas)**

Si ya tienes una base de datos funcionando con datos, necesitas ejecutar las migraciones para actualizar la estructura.

---

## Catálogo de Migraciones

### Solo para Instalaciones Existentes

| Archivo | Propósito | ¿Nueva Instalación? | ¿Actualización? |
|---------|-----------|---------------------|-----------------|
| `010_remove_recursos_informacion.sql` | Elimina tabla obsoleta recursos_informacion | ❌ No necesario | ✅ Sí ejecutar |
| `011_update_umbral_riesgo_scale.sql` | Actualiza umbral 0-25 → 0-100 | ❌ No necesario | ✅ Sí ejecutar |
| `012_normalize_existing_risk_values.sql` | Normaliza riesgos existentes | ❌ No necesario | ✅ Sí ejecutar |
| `013_refactor_controles_amenazas_to_soa.sql` | Cambia estructura controles_amenazas | ❌ No necesario (idempotente) | ✅ Sí ejecutar |
| `add_audit_document_types.sql` | Agrega tipos de documento de auditoría | ❌ No necesario | ⚠️ Opcional |

### Datos de Prueba/Ejemplo (Opcionales)

| Archivo | Propósito | ¿Cuándo usar? |
|---------|-----------|---------------|
| `014_seed_test_control_amenaza.sql` | Crea relaciones control-amenaza de ejemplo | Solo para testing/demo |

---

## Guía de Uso por Escenario

### Escenario 1: Instalación Nueva desde Cero

```bash
# 1. Iniciar contenedores
docker-compose up -d

# 2. Verificar que las tablas se crearon
docker exec ismsmanager-web-1 bash -c \
  "PGPASSWORD=isms_secure_password psql -h db -U isms -d isms_db -c '\dt'"

# 3. Acceder a la aplicación
# http://localhost
```

**NO ejecutar ninguna migración SQL**. Todo está listo.

---

### Escenario 2: Actualización desde Instalación Antigua

```bash
# 1. Hacer backup de la base de datos
docker exec ismsmanager-db-1 pg_dump -U isms isms_db > backup.sql

# 2. Ejecutar migraciones en orden
cd migrations

# Migración 010: Eliminar tabla obsoleta
docker exec ismsmanager-web-1 bash -c \
  "PGPASSWORD=isms_secure_password psql -h db -U isms -d isms_db \
   -f /app/migrations/010_remove_recursos_informacion.sql"

# Migración 011: Actualizar escala de umbral
docker exec ismsmanager-web-1 bash -c \
  "PGPASSWORD=isms_secure_password psql -h db -U isms -d isms_db \
   -f /app/migrations/011_update_umbral_riesgo_scale.sql"

# Migración 012: Normalizar valores de riesgo
docker exec ismsmanager-web-1 bash -c \
  "PGPASSWORD=isms_secure_password psql -h db -U isms -d isms_db \
   -f /app/migrations/012_normalize_existing_risk_values.sql"

# Migración 013: Refactorizar controles_amenazas
docker exec ismsmanager-web-1 bash -c \
  "PGPASSWORD=isms_secure_password psql -h db -U isms -d isms_db \
   -f /app/migrations/013_refactor_controles_amenazas_to_soa.sql"

# 3. Actualizar código de la aplicación
docker cp app/risks/models.py ismsmanager-web-1:/app/app/risks/models.py
docker cp app/risks/services/risk_calculation_service.py \
  ismsmanager-web-1:/app/app/risks/services/risk_calculation_service.py

# 4. Reiniciar aplicación
docker restart ismsmanager-web-1

# 5. Verificar logs
docker logs ismsmanager-web-1 --tail 50 | grep -i error
```

---

## Detalles de Cada Migración

### 010_remove_recursos_informacion.sql

**Propósito**: Elimina la tabla `recursos_informacion` que fue obsoleta en el rediseño del módulo de riesgos.

**Instalación nueva**: ❌ No necesario (la tabla nunca se crea)

**Actualización**: ✅ Ejecutar si tienes instalación anterior a octubre 2025

---

### 011_update_umbral_riesgo_scale.sql

**Propósito**: Actualiza el campo `umbral_riesgo_objetivo` de escala 0-25 a 0-100.

**Fórmula**: `nuevo_valor = valor_antiguo × 4.0`

**Instalación nueva**: ❌ No necesario (campo se crea directamente con escala 0-100)

**Actualización**: ✅ Ejecutar para normalizar evaluaciones existentes

**Ejemplo**:
```sql
-- Antes
umbral_riesgo_objetivo = 12.00  (escala 0-25)

-- Después
umbral_riesgo_objetivo = 48.00  (escala 0-100)
```

---

### 012_normalize_existing_risk_values.sql

**Propósito**: Normaliza todos los valores de riesgo existentes a la escala 0-100.

**Operaciones**:
- Divide impactos por 5 (escala 0-50 → 0-10)
- Divide probabilidades por 2 (escala 0-20 → 0-10)
- Recalcula niveles de riesgo (0-1000 → 0-100)

**Instalación nueva**: ❌ No necesario (riesgos se calculan directamente con fórmulas nuevas)

**Actualización**: ✅ CRÍTICO - Ejecutar para normalizar todos los riesgos existentes

---

### 013_refactor_controles_amenazas_to_soa.sql

**Propósito**: Cambia la estructura de `controles_amenazas` para usar SOA como referencia única.

**Cambios**:
- `control_id` INTEGER FK → `control_codigo` VARCHAR(10)
- Agrega campo `tipo_control`
- Elimina dependencia de `controles_iso27002`

**Instalación nueva**: ❌ No necesario (tabla se crea con estructura nueva)

**Actualización**: ✅ Ejecutar para migrar estructura antigua

**Idempotencia**: ✅ Seguro ejecutar múltiples veces (detecta si ya está migrado)

---

### 014_seed_test_control_amenaza.sql

**Propósito**: Crea relaciones de ejemplo entre controles y amenazas para testing.

**Instalación nueva**: ⚠️ Opcional (solo para demo/testing)

**Actualización**: ⚠️ Opcional (solo para demo/testing)

**Datos creados**:
- 12 relaciones control-amenaza
- 3 controles: A.5.1, A.6.8, A.8.1
- Efectividades: 0.7 - 0.9

---

### add_audit_document_types.sql

**Propósito**: Agrega tipos de documento específicos para auditorías.

**Instalación nueva**: ❌ No necesario (tipos se crean en seed_data)

**Actualización**: ⚠️ Opcional (solo si no tienes tipos de documento de auditoría)

---

## Verificación Post-Migración

### Para Instalaciones Existentes (después de migrar)

```bash
# 1. Verificar estructura de controles_amenazas
docker exec ismsmanager-web-1 bash -c \
  "PGPASSWORD=isms_secure_password psql -h db -U isms -d isms_db \
   -c '\d controles_amenazas'"

# Debe mostrar:
# - control_codigo VARCHAR(10)  ✅
# - tipo_control VARCHAR(20)     ✅
# - No debe tener control_id     ✅

# 2. Verificar valores de riesgo normalizados
docker exec ismsmanager-web-1 bash -c \
  "PGPASSWORD=isms_secure_password psql -h db -U isms -d isms_db \
   -c 'SELECT MAX(nivel_riesgo_efectivo) FROM riesgos;'"

# Debe ser ≤ 100  ✅

# 3. Verificar umbral actualizado
docker exec ismsmanager-web-1 bash -c \
  "PGPASSWORD=isms_secure_password psql -h db -U isms -d isms_db \
   -c 'SELECT MAX(umbral_riesgo_objetivo) FROM evaluaciones_riesgo;'"

# Debe estar en escala 0-100  ✅
```

---

## Preguntas Frecuentes

### ¿Por qué las migraciones están aquí si no son necesarias para instalaciones nuevas?

Las migraciones son **fundamentales para instalaciones existentes**. Se mantienen para:

1. **Actualizar instalaciones en producción** sin perder datos
2. **Trazabilidad**: Documentan todos los cambios de estructura
3. **Rollback**: Permiten entender cómo revertir cambios si es necesario
4. **Histórico**: Muestran la evolución del sistema

### ¿Qué pasa si ejecuto las migraciones en una instalación nueva?

- **010-012**: Fallarán o no harán nada (tablas/datos no existen)
- **013**: Se omitirá automáticamente (detecta estructura nueva)
- **014**: Funcionará (crea datos de prueba)

**Resultado**: No causa daño, pero es innecesario.

### ¿Cómo sé si necesito ejecutar migraciones?

**Regla simple**:

```bash
# ¿Instalación nueva?
if [ ! -f "ya_tenia_datos_antes.txt" ]; then
  echo "NO ejecutar migraciones"
else
  echo "SÍ ejecutar migraciones 010-013"
fi
```

**Indicadores de instalación existente**:
- Ya tienes usuarios creados
- Ya tienes riesgos evaluados
- Ya tienes activos registrados
- La base de datos tiene datos históricos

---

## Resumen Ejecutivo

| Tipo de Instalación | Migraciones SQL | Razón |
|---------------------|-----------------|-------|
| **Nueva (desde cero)** | ❌ NO ejecutar | `db.create_all()` crea estructura correcta |
| **Actualización (con datos)** | ✅ SÍ ejecutar 010-013 | Actualizar estructura y normalizar datos |
| **Testing/Demo** | ⚠️ Opcional 014 | Solo para datos de ejemplo |

---

**Documento**: migrations/README.md
**Versión**: 1.0
**Fecha**: 2025-10-25
**Última actualización**: Aclaración sobre necesidad de migraciones
