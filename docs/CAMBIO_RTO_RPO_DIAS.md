# Cambio de RTO/RPO de Minutos a Días

## Resumen
Se ha modificado la representación de RTO (Recovery Time Objective) y RPO (Recovery Point Objective) para usar **días con decimales** en lugar de minutos, proporcionando mayor flexibilidad y facilidad de uso.

## Cambios Realizados

### 1. Modelo de Datos
**Archivo**: `models.py`

- **Antes**: `rto = db.Column(db.Integer)  # minutos`
- **Después**: `rto = db.Column(db.Float)  # días`

- **Antes**: `rpo = db.Column(db.Integer)  # minutos`
- **Después**: `rpo = db.Column(db.Float)  # días`

### 2. Base de Datos
Se ejecutó una migración para convertir los valores existentes:
- Conversión: `días = minutos / 1440`
- Tipo de columna: `INTEGER` → `DOUBLE PRECISION`

**Archivo de migración**: `migrations/versions/011_convert_rto_rpo_to_days.py`

### 3. Formularios
**Archivo**: `app/templates/services/form.html`

- Se cambió el label de "minutos" a "días"
- Se agregó `step="0.01"` para permitir decimales
- Se actualizaron los placeholders y textos de ayuda

**Ejemplos de uso:**
- `0.5` = 12 horas
- `0.25` = 6 horas
- `1` = 1 día
- `7` = 1 semana

### 4. Vistas de Detalle
**Archivo**: `app/templates/services/detail.html`

- Se muestra el valor en días con 2 decimales
- Si el valor es menor a 1 día, se muestra también en horas como referencia

**Ejemplo de visualización:**
```
RTO: 0.50 días
     (12.0 horas)
```

### 5. Backend
**Archivo**: `app/blueprints/services.py`

- Cambio en funciones `create` y `edit`: `type=int` → `type=float`
- Líneas 166-167 y 318-319

## Ejemplos de Valores

| Días | Equivalente | Uso Típico |
|------|-------------|------------|
| 0.04 | ~1 hora | Servicios críticos 24/7 |
| 0.25 | 6 horas | Servicios importantes |
| 0.5 | 12 horas | Servicios estándar |
| 1 | 1 día | Servicios no críticos |
| 2 | 2 días | Recuperación planificada |
| 7 | 1 semana | Servicios de soporte |

## Compatibilidad

### Datos Existentes
Los valores existentes en la base de datos fueron convertidos automáticamente mediante la migración. Si tenías:
- RTO = 1440 minutos → Ahora es 1.00 días
- RPO = 30 minutos → Ahora es 0.02 días

### Rollback
Si necesitas revertir el cambio, la migración incluye una función `downgrade()` que:
1. Convierte de días a minutos (multiplicando por 1440)
2. Redondea al entero más cercano
3. Cambia el tipo de columna de `FLOAT` a `INTEGER`

## Beneficios del Cambio

1. **Más Intuitivo**: Los valores en días son más fáciles de entender y comunicar
2. **Flexibilidad**: Los decimales permiten representar horas exactas (0.5 = 12h)
3. **Alineación con Estándares**: La mayoría de documentación de continuidad usa días
4. **Menos Errores**: Evita confusión con valores grandes en minutos

## Notas Técnicas

- **Tipo de dato**: `DOUBLE PRECISION` en PostgreSQL
- **Precisión**: 2 decimales en formularios, precisión completa en BD
- **Validación**: Valores mínimos de 0, sin máximo definido
- **NULL permitido**: Sí, RTO/RPO son campos opcionales

## Fecha de Implementación
2025-11-01
