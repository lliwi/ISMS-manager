# Guía de Instalación Limpia - ISMS Manager

## Fecha
2025-10-25

## Propósito
Este documento describe el proceso de instalación completa desde cero del ISMS Manager, incluyendo todos los cambios recientes de refactorización de controles y SOA.

## Requisitos Previos

- Docker y Docker Compose instalados
- Puerto 80 disponible (o configurar otro puerto en `docker-compose.yml`)
- Mínimo 2GB de RAM disponible
- 10GB de espacio en disco

## Proceso de Instalación

### 1. Clonar o Descargar el Repositorio

```bash
git clone <repository-url>
cd "ISMS Manager"
```

### 2. Configurar Variables de Entorno (Opcional)

Copiar el archivo de ejemplo:
```bash
cp .env.example .env
```

Editar `.env` si necesitas cambiar configuraciones por defecto:
- URL de base de datos
- Clave secreta
- Configuración de correo

### 3. Iniciar los Contenedores

```bash
docker-compose up -d
```

Este comando:
1. Construye las imágenes Docker
2. Inicia PostgreSQL
3. Inicia la aplicación Flask
4. Configura Nginx como proxy inverso

### 4. Verificar la Creación de Tablas

La aplicación usa SQLAlchemy ORM que crea automáticamente todas las tablas en el primer inicio:

```bash
docker logs ismsmanager-web-1 | grep -i "creating\|table"
```

**Tablas creadas automáticamente** (incluyen la nueva estructura):
- `users`, `roles`
- `soa_versions`, `soa_controls` ← SOA para controles
- `controles_amenazas` ← **Con estructura nueva** (control_codigo)
- `controles_iso27002` ← Catálogo de referencia
- `amenazas`, `activos_informacion`, `riesgos`
- Y todas las demás tablas del sistema

### 5. Verificar la Estructura de controles_amenazas

Para confirmar que la tabla tiene la estructura correcta:

```bash
docker exec ismsmanager-web-1 bash -c \
  "PGPASSWORD=isms_secure_password psql -h db -U isms -d isms_db \
   -c '\d controles_amenazas'"
```

**Estructura esperada**:
```
     Column     |            Type             | Nullable | Default
----------------+-----------------------------+----------+---------
 id             | integer                     | not null |
 control_codigo | character varying(10)       | not null |    ← STRING
 amenaza_id     | integer                     | not null |
 tipo_control   | character varying(20)       | not null | 'PREVENTIVO'
 efectividad    | numeric(3,2)                |          | 1.00
 created_at     | timestamp without time zone |          | CURRENT_TIMESTAMP
```

**⚠️ IMPORTANTE**: Si ves `control_id` en lugar de `control_codigo`, la instalación no usó los modelos actualizados.

### 6. Acceder a la Aplicación

Abrir navegador en:
```
http://localhost
```

**Credenciales por defecto**:
- Usuario: `admin`
- Contraseña: `admin123`

**⚠️ IMPORTANTE**: Cambiar la contraseña del administrador inmediatamente después del primer login.

## Datos Iniciales (Seed Data)

La instalación automáticamente crea:

### ✅ Creados Automáticamente

1. **Usuario administrador**
   - Username: `admin`
   - Email: `admin@ejemplo.com`
   - Rol: Administrador del Sistema

2. **Roles del sistema**
   - Administrador del Sistema
   - Gestor de Seguridad (CISO)
   - Auditor Interno
   - Responsable de Proceso
   - Usuario General

3. **Tipos de documento**
   - Política
   - Procedimiento
   - Instrucción
   - Registro
   - Acta

4. **Versión SOA inicial**
   - SOA vacío marcado como activo
   - 93 controles ISO 27002:2022
   - Todos con `applicability_status = 'aplicable'`
   - Todos con `maturity_score = 0` (no implementado)

### 📝 Requieren Configuración Manual

1. **Catálogo de Amenazas MAGERIT**
   ```bash
   docker exec ismsmanager-web-1 python -c \
     "from app.risks.seed_amenazas import seed_amenazas; seed_amenazas()"
   ```

2. **Relaciones Control-Amenaza**
   - Definir qué controles mitigan qué amenazas
   - Establecer efectividad de cada control sobre cada amenaza
   - Ver ejemplo en `migrations/014_seed_test_control_amenaza.sql`

3. **Activos de Información**
   - Crear mediante interfaz web o importación

4. **Procesos de Negocio**
   - Definir procesos críticos de la organización

## Verificación Post-Instalación

### 1. Verificar Que No Hay Errores

```bash
docker logs ismsmanager-web-1 --tail 100 | grep -i error
```

Debe devolver: sin resultados (o solo errores normales de desarrollo).

### 2. Verificar SOA Activo

```bash
docker exec ismsmanager-web-1 bash -c \
  "PGPASSWORD=isms_secure_password psql -h db -U isms -d isms_db \
   -c 'SELECT version_number, is_current FROM soa_versions;'"
```

Debe mostrar al menos una versión con `is_current = true`.

### 3. Verificar Controles del SOA

```bash
docker exec ismsmanager-web-1 bash -c \
  "PGPASSWORD=isms_secure_password psql -h db -U isms -d isms_db \
   -c 'SELECT COUNT(*) AS total_controles FROM soa_controls WHERE soa_version_id IN (SELECT id FROM soa_versions WHERE is_current = true);'"
```

Debe mostrar 93 controles (ISO 27002:2022).

### 4. Acceder al Dashboard

1. Login en `http://localhost`
2. Navegar a **Dashboard**
3. Verificar que no hay errores 500
4. Navegar a **SOA** (`http://localhost/soa/`)
5. Debe mostrar los 93 controles

## Migraciones SQL - ¿Son Necesarias?

### ❌ NO para Instalaciones Nuevas

**Las migraciones SQL NO son necesarias en instalaciones nuevas** porque:

1. **SQLAlchemy crea las tablas automáticamente** en [application.py:93](../application.py#L93)
2. Los modelos en `app/risks/models.py` ya tienen la **estructura actualizada**
3. `db.create_all()` crea todas las tablas con la estructura correcta desde el principio

**Conclusión**: En una instalación nueva, **NO ejecutes ninguna migración SQL**. Todo funciona automáticamente.

### ✅ SÍ para Actualizaciones de Instalaciones Existentes

Si ya tienes una instalación con datos, necesitas ejecutar migraciones:
- `010`: Eliminar tabla obsoleta
- `011`: Normalizar umbral de riesgo
- `012`: Normalizar valores de riesgo existentes
- `013`: Refactorizar estructura de controles

Ver [migrations/README.md](../migrations/README.md) para guía completa de migración.

### 📝 Verificación Rápida

Para confirmar que tu instalación nueva tiene la estructura correcta:

```bash
docker exec ismsmanager-web-1 bash -c \
  "PGPASSWORD=isms_secure_password psql -h db -U isms -d isms_db \
   -c '\d controles_amenazas'" | grep control_codigo
```

**Resultado esperado**:
```
control_codigo | character varying(10) | not null |
```

Si ves `control_codigo` → ✅ Estructura correcta, instalación exitosa

## Estructura de Controles - Nueva Arquitectura

### Flujo de Datos para Cálculo de Riesgos

```
1. Crear relación control-amenaza
   ↓
   controles_amenazas.control_codigo = "A.5.1"
   controles_amenazas.amenaza_id = <id>
   controles_amenazas.tipo_control = "PREVENTIVO"
   controles_amenazas.efectividad = 0.8

2. Motor de cálculo busca en SOA activo
   ↓
   SELECT maturity_score FROM soa_controls
   WHERE control_id = "A.5.1"
   AND soa_version_id = (SELECT id FROM soa_versions WHERE is_current = true)
   AND applicability_status = 'aplicable'

3. Normaliza madurez
   ↓
   MAGERIT = min(5, maturity_score × 5.0 / 6.0)

4. Calcula reducción de riesgo
   ↓
   vulnerabilidad = 5 - (MAGERIT × efectividad)
```

### ⚠️ Diferencias con Instalaciones Antiguas

| Aspecto | Instalación Antigua | Instalación Nueva |
|---------|---------------------|-------------------|
| Tabla controles_amenazas | `control_id` INTEGER FK | `control_codigo` VARCHAR(10) |
| Referencia de controles | `controles_iso27002.id` | `soa_controls.control_id` |
| Tipo de control | En `controles_iso27002` | En `controles_amenazas` |
| Fuente de madurez | `salvaguardas_implantadas` | `soa_controls.maturity_score` |
| Escalas | Múltiples inconsistentes | 0-100 normalizada |

## Configuración Inicial Recomendada

### 1. Configurar SOA (Obligatorio)

1. Acceder a **SOA** > **Versión Activa**
2. Para cada control:
   - Marcar `applicability_status`:
     - `aplicable`: Se implementa en tu organización
     - `no_aplicable`: No aplica (justificar)
     - `transferido`: Transferido a tercero (detallar)
   - Establecer `maturity_score` (0-6):
     - 0: No implementado
     - 1-6: Según nivel de madurez CMMI
   - Agregar `evidence`: Evidencias de implementación
   - Asignar `responsible_user_id`: Responsable del control

### 2. Definir Relaciones Control-Amenaza

Las relaciones definen qué controles mitigan qué amenazas:

```sql
-- Ejemplo: Control A.5.1 mitiga amenazas de error humano
INSERT INTO controles_amenazas (control_codigo, amenaza_id, tipo_control, efectividad)
VALUES
  ('A.5.1', (SELECT id FROM amenazas WHERE codigo = 'E.1'), 'PREVENTIVO', 0.80),
  ('A.5.1', (SELECT id FROM amenazas WHERE codigo = 'E.2'), 'PREVENTIVO', 0.75);
```

**Efectividad** (0.0-1.0):
- 1.0: Control totalmente efectivo contra la amenaza
- 0.5: Control parcialmente efectivo
- 0.1: Control con efecto mínimo

### 3. Crear Primera Evaluación de Riesgos

1. **Activos** > **Nuevo Activo**
2. **Riesgos** > **Nueva Evaluación**
3. Seleccionar activos a evaluar
4. Sistema calculará riesgos automáticamente usando SOA activo

## Troubleshooting

### Error: "Could not determine join condition on ControlISO27002.amenazas"

**Causa**: Modelos no actualizados correctamente.

**Solución**:
```bash
docker cp app/risks/models.py ismsmanager-web-1:/app/app/risks/models.py
docker restart ismsmanager-web-1
```

### Error: "Column control_id does not exist"

**Causa**: Migración 013 no se ejecutó o falló.

**Solución**: Verificar estructura de tabla y ejecutar migración manualmente si es necesario.

### Dashboard muestra valores de riesgo > 100

**Causa**: Fórmulas antiguas aún en uso.

**Solución**: Recalcular riesgos existentes (automático al editar evaluación).

## Siguientes Pasos

1. ✅ Cambiar contraseña de admin
2. ✅ Crear usuarios adicionales
3. ✅ Configurar SOA con controles aplicables
4. ✅ Establecer niveles de madurez realistas
5. ✅ Definir relaciones control-amenaza
6. ✅ Importar catálogo de amenazas MAGERIT
7. ✅ Crear activos de información
8. ✅ Realizar primera evaluación de riesgos

## Referencias

- [METODOLOGIA_CALCULO_RIESGOS.md](METODOLOGIA_CALCULO_RIESGOS.md) - Fórmulas y metodología
- [REFACTOR_CONTROLES_SOA.md](REFACTOR_CONTROLES_SOA.md) - Cambios arquitectónicos
- [CLAUDE.md](../CLAUDE.md) - Visión general del proyecto

---

**Documento**: INSTALACION_LIMPIA.md
**Versión**: 1.0
**Fecha**: 2025-10-25
**Sistema**: ISMS Manager
**Autor**: Documentación técnica generada para instalaciones nuevas post-refactorización
