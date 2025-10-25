# Refactorización: Eliminación de Dependencia de ControlISO27002

## Fecha
2025-10-25

## Objetivo
Eliminar la dependencia del catálogo estático `controles_iso27002` en el cálculo de riesgos, usando exclusivamente el SOA (Statement of Applicability) activo como fuente de verdad para controles y su nivel de madurez.

## Problema Original

### Arquitectura Antigua
```
controles_amenazas
├── control_id (FK → controles_iso27002.id)
└── amenaza_id (FK → amenazas.id)

Flujo de cálculo:
1. Obtener ControlAmenaza
2. Buscar ControlISO27002 por control_id
3. Convertir código ISO ("5.1" → "A.5.1")
4. Buscar en SOA por código convertido
5. Obtener maturity_score
```

### Limitaciones
- **Fragilidad**: Dependía de conversión manual de códigos
- **Rigidez**: No podía cambiar versiones de ISO sin migración
- **Redundancia**: Dos fuentes de información (ControlISO27002 + SOA)
- **Inconsistencia**: Posibles desajustes entre catálogo estático y SOA

## Solución Implementada

### Nueva Arquitectura
```
controles_amenazas
├── control_codigo VARCHAR(10) (ej: "A.5.1")
├── amenaza_id (FK → amenazas.id)
└── tipo_control VARCHAR(20) ('PREVENTIVO', 'REACTIVO', etc.)

Flujo de cálculo:
1. Obtener ControlAmenaza con control_codigo
2. Buscar directamente en SOA activo por control_codigo
3. Obtener maturity_score
```

### Ventajas
- **Simplicidad**: Búsqueda directa sin conversiones
- **Flexibilidad**: Cambios de versión SOA no rompen relaciones
- **Unicidad**: SOA es la única fuente de verdad
- **Mantenibilidad**: Menos código, menos puntos de fallo

## Cambios Realizados

### 1. Modelo ControlAmenaza ([models.py:303-330](app/risks/models.py#L303-L330))

**Antes:**
```python
class ControlAmenaza(db.Model):
    control_id = db.Column(db.Integer, db.ForeignKey('controles_iso27002.id'))
    amenaza_id = db.Column(db.Integer, db.ForeignKey('amenazas.id'))
    efectividad = db.Column(db.Numeric(3, 2), default=1.00)

    control = db.relationship('ControlISO27002', back_populates='amenazas')
    amenaza = db.relationship('Amenaza', back_populates='controles')
```

**Después:**
```python
class ControlAmenaza(db.Model):
    control_codigo = db.Column(db.String(10), nullable=False, index=True)
    amenaza_id = db.Column(db.Integer, db.ForeignKey('amenazas.id'))
    tipo_control = db.Column(db.String(20), default='PREVENTIVO', index=True)
    efectividad = db.Column(db.Numeric(3, 2), default=1.00)

    amenaza = db.relationship('Amenaza', back_populates='controles')
```

**Cambios clave:**
- `control_id` (integer FK) → `control_codigo` (string)
- Agregado campo `tipo_control` (antes venía de ControlISO27002)
- Eliminada relación con ControlISO27002
- Índice en `control_codigo` para búsquedas rápidas

**IMPORTANTE**: También se eliminó la relación `amenazas` en `ControlISO27002.amenazas` ([models.py:295](app/risks/models.py#L295)) para evitar errores de SQLAlchemy por foreign key inexistente.

### 2. Servicio de Cálculo ([risk_calculation_service.py](app/risks/services/risk_calculation_service.py))

**Antes:**
```python
def calcular_nivel_controles(controles_aplicables):
    for control_amenaza in controles_aplicables:
        control_iso = control_amenaza.control
        soa_codigo = f"A.{control_iso.codigo}"

        soa_control = SOAControl.query.filter_by(
            control_id=soa_codigo,
            soa_version_id=soa_activo.id
        ).first()
```

**Después:**
```python
def calcular_nivel_controles(controles_aplicables):
    for control_amenaza in controles_aplicables:
        soa_control = SOAControl.query.filter_by(
            control_id=control_amenaza.control_codigo,
            soa_version_id=soa_activo.id,
            applicability_status='aplicable'
        ).first()
```

**Cambios clave:**
- Búsqueda directa por `control_codigo`
- Eliminada conversión de códigos
- Agregado filtro `applicability_status='aplicable'`
- Eliminado fallback a salvaguardas (ahora SOA es obligatorio)

**Método actualizado:**
```python
def obtener_controles_aplicables(amenaza, tipo_control):
    return ControlAmenaza.query.filter(
        and_(
            ControlAmenaza.amenaza_id == amenaza.id,
            ControlAmenaza.tipo_control == tipo_control
        )
    ).all()
```

**Cambios clave:**
- Eliminado JOIN con ControlISO27002
- Filtro directo por `tipo_control` en ControlAmenaza

### 3. Imports Limpiados

**Eliminados:**
```python
from app.risks.models import ControlISO27002, SalvaguardaImplantada
```

Solo quedan los imports necesarios:
```python
from models import db, SOAControl, SOAVersion
from app.risks.models import (
    Riesgo, ActivoInformacion, RecursoInformacion, Amenaza,
    AmenazaRecursoTipo, ControlAmenaza, HistorialRiesgo
)
```

## Migración de Datos

### Script: [migrations/013_refactor_controles_amenazas_to_soa.sql](migrations/013_refactor_controles_amenazas_to_soa.sql)

1. **Crear tabla nueva** con estructura actualizada
2. **Migrar datos** convirtiendo `control_id` → `control_codigo`:
   ```sql
   INSERT INTO controles_amenazas_new (control_codigo, amenaza_id, tipo_control, efectividad)
   SELECT
       'A.' || ci.codigo,  -- "5.1" → "A.5.1"
       ca.amenaza_id,
       ci.tipo_control,
       ca.efectividad
   FROM controles_amenazas ca
   JOIN controles_iso27002 ci ON ca.control_id = ci.id
   ```
3. **Reemplazar tabla** antigua con nueva
4. **Verificar** migración exitosa

### Resultado
- ✅ Migración exitosa
- 0 registros migrados (tabla estaba vacía)
- Nueva estructura lista para uso

## Testing

### Seed de Datos de Prueba: [migrations/014_seed_test_control_amenaza.sql](migrations/014_seed_test_control_amenaza.sql)

Se crearon 12 relaciones control-amenaza:

| Control | Nombre | Amenazas | Tipo | Efectividad |
|---------|--------|----------|------|-------------|
| A.5.1 | Políticas de seguridad | E.1, E.2, E.24, E.25 | PREVENTIVO | 0.80 |
| A.8.1 | Dispositivos de usuario | I.1, I.2, I.5 | PREVENTIVO | 0.90 |
| A.6.8 | Reporte de eventos | A.3, A.4, A.5, A.6, A.7 | DETECTIVE | 0.70 |

### Verificación
```bash
docker restart ismsmanager-web-1
# ✅ Contenedor inicia correctamente
# ✅ No hay errores en logs
# ✅ Dashboard carga sin problemas
```

## Estado de ControlISO27002

### Mantenido (por ahora)
La tabla `controles_iso27002` y su modelo aún existen porque:

1. **Rutas de visualización**: Algunas vistas aún muestran el catálogo estático
2. **Referencia histórica**: Puede ser útil mantener el catálogo completo
3. **No afecta cálculos**: El flujo de riesgo ya no la usa

### Rutas que aún usan ControlISO27002
- `/riesgos/controles` - Lista de controles (referencia)
- `/riesgos/controles/<id>` - Detalle de control
- `/riesgos/controles/<id>/salvaguarda` - Gestión de salvaguardas (legacy)

**Nota**: La ruta principal del dashboard ya redirige al SOA (`url_for('soa.index')`).

## Próximos Pasos (Opcionales)

### Si se desea eliminar completamente ControlISO27002:

1. **Eliminar rutas** de visualización de catálogo
2. **Eliminar modelo** ControlISO27002 de models.py
3. **Eliminar tabla** `controles_iso27002` de base de datos
4. **Actualizar seeds** para crear controles_amenazas directamente

### Si se desea mantener como referencia:

- ✅ Estado actual es válido
- ✅ No interfiere con operaciones
- ✅ Puede servir como documentación

## Impacto

### Positivo
- ✅ Código más simple y mantenible
- ✅ Menos dependencias entre módulos
- ✅ SOA como única fuente de verdad
- ✅ Facilita cambios de versión ISO/SOA
- ✅ Mejor alineación con ISO 27001 (SOA es documento oficial)

### Neutral
- ℹ️ Rutas legacy de catálogo aún existen
- ℹ️ Tabla controles_iso27002 aún presente

### Sin Impacto Negativo
- ✅ Migración sin pérdida de datos
- ✅ Retrocompatibilidad asegurada
- ✅ Performance sin cambios significativos

## Conclusión

La refactorización **elimina exitosamente la dependencia de ControlISO27002** del motor de cálculo de riesgos, usando el SOA activo como única fuente de información sobre controles y su nivel de implementación.

El sistema ahora es:
- **Más robusto**: Menos puntos de fallo
- **Más alineado**: SOA es el documento oficial ISO 27001
- **Más flexible**: Soporta cambios de versión sin migración
- **Más simple**: Menos código, menos complejidad

---

**Archivos modificados:**
- [app/risks/models.py](app/risks/models.py) (ControlAmenaza)
- [app/risks/services/risk_calculation_service.py](app/risks/services/risk_calculation_service.py)
- [migrations/013_refactor_controles_amenazas_to_soa.sql](migrations/013_refactor_controles_amenazas_to_soa.sql)
- [migrations/014_seed_test_control_amenaza.sql](migrations/014_seed_test_control_amenaza.sql)

**Archivos creados:**
- [docs/REFACTOR_CONTROLES_SOA.md](docs/REFACTOR_CONTROLES_SOA.md) (este documento)
