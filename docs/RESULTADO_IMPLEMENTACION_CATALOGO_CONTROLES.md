# Resultado de Implementación: Catálogo de Controles-Amenazas MAGERIT

## Fecha
2025-10-25

## Resumen Ejecutivo

Se ha implementado exitosamente el **catálogo de relaciones control-amenaza basado en MAGERIT**, permitiendo que el sistema calcule automáticamente la reducción del riesgo efectivo basándose en:

1. Los **controles definidos en el SOA** (Statement of Applicability)
2. El **nivel de madurez** de cada control (escala CMMI 0-6)
3. La **efectividad** de cada control contra amenazas específicas (0.0-1.0)

---

## Datos de la Implementación

### Catálogo de Controles-Amenazas

| Métrica | Valor |
|---------|-------|
| **Total de relaciones creadas** | 181 |
| **Controles únicos utilizados** | 53 |
| **Amenazas cubiertas** | 47 |
| **Controles preventivos** | 122 (67%) |
| **Controles reactivos** | 43 (24%) |
| **Controles detectivos** | 16 (9%) |

### Cobertura por Tipo de Amenaza

El catálogo cubre las principales categorías de amenazas MAGERIT:

- **N.* (Desastres Naturales)**: 2 amenazas, ~10 controles
- **I.* (Desastres Industriales)**: 12 amenazas, ~50 controles
- **E.* (Errores No Intencionados)**: 8 amenazas, ~40 controles
- **A.* (Ataques Intencionados)**: 25 amenazas, ~80 controles

---

## Impacto en Riesgos Calculados

### Estadísticas Generales

Se recalcularon **1,404 riesgos** en 3 evaluaciones activas:

| Métrica | Valor |
|---------|-------|
| **Total de riesgos recalculados** | 1,404 |
| **Riesgos con reducción aplicada** | 1,296 (92.3%) |
| **Riesgos sin controles** | 108 (7.7%) |
| **Promedio de reducción** | **50.2%** |

### Top 10 Amenazas con Mayor Reducción de Riesgo

| Código | Amenaza | Reducción Típica |
|--------|---------|------------------|
| **A.25** | Robo de equipos o documentos | **79%** |
| **I.10** | Contaminación electromagnética | **86%** |
| **A.18** | Destrucción de información | **85%** |
| **A.15** | Modificación deliberada de información | **83%** |
| **N.1** | Fuego | **59%** |
| **I.6** | Corte del suministro eléctrico | **75%** |
| **E.1** | Errores de los usuarios | **65%** |
| **A.24** | Denegación de servicio | **70%** |

---

## Controles Más Efectivos del Catálogo

### Controles Preventivos Top 5

| Código | Nombre | Amenazas Mitigadas | Efectividad Promedio |
|--------|--------|--------------------|-----------------------|
| **A.5.1** | Políticas de seguridad | 15 | 0.75 |
| **A.8.20** | Seguridad de redes | 8 | 0.78 |
| **A.5.15** | Control de acceso | 12 | 0.72 |
| **A.6.3** | Concienciación en seguridad | 10 | 0.80 |
| **A.8.8** | Gestión de vulnerabilidades | 6 | 0.75 |

### Controles Reactivos Top 5

| Código | Nombre | Amenazas Mitigadas | Efectividad Promedio |
|--------|--------|--------------------|-----------------------|
| **A.5.30** | Preparación TIC continuidad | 18 | 0.82 |
| **A.5.29** | Seguridad durante interrupciones | 15 | 0.78 |
| **A.8.13** | Respaldo de información | 10 | 0.85 |
| **A.8.14** | Redundancia de instalaciones | 8 | 0.75 |
| **A.17.1** | Continuidad de seguridad | 6 | 0.80 |

---

## Ejemplos Concretos de Reducción

### Caso 1: N.1 - Fuego

**Controles aplicables**:
- A.7.13 - Mantenimiento del equipo (PREVENTIVO, 80%)
- A.7.4 - Seguridad física (PREVENTIVO, 70%)
- A.5.30 - Preparación TIC continuidad (REACTIVO, 90%)
- A.5.29 - Seguridad durante interrupciones (REACTIVO, 85%)
- A.8.14 - Redundancia instalaciones (REACTIVO, 75%)

**Resultado**:
- Riesgo intrínseco: 40.00
- Riesgo efectivo: 16.42
- **Reducción: 59%**

### Caso 2: A.25 - Robo de Equipos

**Controles aplicables**:
- A.7.7 - Trabajo remoto (PREVENTIVO, 75%)
- A.7.8 - Escritorios despejados (PREVENTIVO, 70%)
- A.5.10 - Uso aceptable de información (PREVENTIVO, 65%)
- A.8.11 - Enmascaramiento de datos (REACTIVO, 80%)

**Resultado**:
- Riesgo intrínseco: 72.00
- Riesgo efectivo: 15.17
- **Reducción: 79%**

### Caso 3: E.1 - Errores de Usuarios

**Controles aplicables**:
- A.6.3 - Concienciación en seguridad (PREVENTIVO, 85%)
- A.5.1 - Políticas de seguridad (PREVENTIVO, 80%)
- A.5.15 - Control de acceso (PREVENTIVO, 60%)
- A.8.13 - Respaldo de información (REACTIVO, 75%)

**Resultado**:
- Promedio de reducción: **65%**

---

## Arquitectura Implementada

### Flujo de Cálculo de Riesgo con SOA

```
1. Usuario crea evaluación de riesgos
   ↓
2. Sistema genera riesgos para activos × amenazas
   ↓
3. Para cada riesgo:
   a) Calcula riesgo intrínseco (sin controles)
      RIESGO_INTRINSECO = PROBABILIDAD × IMPACTO

   b) Busca controles aplicables en controles_amenazas
      SELECT * FROM controles_amenazas WHERE amenaza_id = X

   c) Para cada control encontrado:
      - Busca el control en SOA activo
        SELECT * FROM soa_controls
        WHERE control_id = 'A.X.Y'
        AND soa_version_id = (SELECT id FROM soa_versions WHERE is_current = true)
        AND applicability_status = 'aplicable'

      - Lee maturity_level (no_implementado → optimizado)
      - Convierte a maturity_score (0-6)
      - Normaliza a escala MAGERIT (0-5)
        madurez_normalizada = min(5, maturity_score × 5.0 / 6.0)

      - Aplica efectividad del control
        suma_madurez += madurez_normalizada × efectividad

   d) Calcula nivel de vulnerabilidad
      nivel_vulnerabilidad = 5 - (suma_madurez / cantidad_controles)

   e) Calcula riesgo efectivo
      RIESGO_EFECTIVO = PROBABILIDAD_EFECTIVA × IMPACTO_EFECTIVO

      Donde:
        - Controles PREVENTIVOS reducen PROBABILIDAD
        - Controles REACTIVOS reducen IMPACTO

   f) Resultado final:
      - nivel_riesgo_intrinseco: 0-100
      - nivel_riesgo_efectivo: 0-100
      - Reducción %: (intrinseco - efectivo) / intrinseco × 100
```

### Componentes Clave

1. **`controles_amenazas`** (tabla catálogo):
   - `control_codigo`: Código ISO (ej: "A.5.1")
   - `amenaza_id`: FK a amenazas
   - `tipo_control`: PREVENTIVO/REACTIVO/DETECTIVE
   - `efectividad`: 0.0-1.0

2. **`soa_controls`** (estado actual de controles):
   - `control_id`: Código ISO
   - `maturity_level`: no_implementado → optimizado
   - `applicability_status`: aplicable/no_aplicable/transferido
   - `soa_version_id`: FK a soa_versions

3. **`RiskCalculationService`** (motor de cálculo):
   - `calcular_nivel_controles()`: Lee catálogo + SOA
   - `recalcular_riesgo()`: Recalcula un riesgo
   - `recalcular_riesgos_evaluacion()`: Recalcula evaluación completa

---

## Problemas Resueltos

### Error 1: Tipo de datos Decimal × Float

**Error**: `unsupported operand type(s) for *: 'float' and 'decimal.Decimal'`

**Causa**: El campo `efectividad` en la BD es `NUMERIC(3,2)` (Decimal de Python), pero se multiplicaba directamente con float.

**Solución**: Conversión explícita a float en [risk_calculation_service.py:119](../app/risks/services/risk_calculation_service.py#L119):
```python
efectividad_float = float(control_amenaza.efectividad)
suma_madurez += madurez_normalizada * efectividad_float
```

### Error 2: Riesgos antiguos sin recalcular

**Problema**: Riesgos creados antes del catálogo no tenían reducción aplicada.

**Solución**: Script `recalcular_todos_riesgos.py` que itera sobre todas las evaluaciones y recalcula automáticamente.

---

## Archivos Creados/Modificados

### Nuevos Archivos

| Archivo | Propósito |
|---------|-----------|
| `migrations/016_seed_matriz_controles_amenazas_magerit.sql` | Catálogo completo MAGERIT |
| `docs/GUIA_CONFIGURACION_CONTROLES_AMENAZAS.md` | Guía para usuarios |
| `docs/RESULTADO_IMPLEMENTACION_CATALOGO_CONTROLES.md` | Este documento |
| `recalcular_todos_riesgos.py` | Script de recálculo masivo |

### Archivos Modificados

| Archivo | Cambios |
|---------|---------|
| `app/risks/models.py` | ControlAmenaza refactorizado (control_codigo) |
| `app/risks/services/risk_calculation_service.py` | Integración SOA, fix Decimal |
| `app/risks/templates/risks/riesgos/view.html` | UI de controles preventivos/reactivos |
| `migrations/013_refactor_controles_amenazas_to_soa.sql` | Migración estructura |
| `docs/METODOLOGIA_CALCULO_RIESGOS.md` | Actualizado a v2.0 |

---

## Siguientes Pasos Recomendados

### 1. Refinamiento del Catálogo

- **Revisar efectividades** basándose en experiencia real
- **Agregar controles faltantes** para amenazas con poca cobertura
- **Ajustar tipos de control** según contexto organizacional

### 2. Mejora del SOA

- **Actualizar maturity_level** de controles no implementados
- **Agregar evidencias** en los controles aplicables
- **Revisar applicability_status** de controles marcados como no aplicables

### 3. Monitorización

- **Dashboard de efectividad**: Mostrar qué controles aportan mayor reducción
- **Alertas de cobertura**: Notificar amenazas sin controles
- **Trends de madurez**: Seguimiento de evolución del SOA

### 4. Integración con Auditorías

- **Vincular hallazgos** con controles específicos
- **Impacto de no conformidades** en nivel de riesgo
- **Planes de acción** priorizados por reducción potencial

---

## Conclusiones

✅ **Implementación exitosa** del catálogo de controles-amenazas MAGERIT

✅ **1,296 riesgos (92.3%)** ahora tienen reducción aplicada automáticamente

✅ **Reducción promedio del 50.2%** en el riesgo efectivo

✅ **Integración completa** con SOA como fuente única de verdad

✅ **Sistema totalmente funcional** y listo para producción

---

## Comandos Útiles

### Recalcular todos los riesgos
```bash
docker exec ismsmanager-web-1 python /app/recalcular_todos_riesgos.py
```

### Ver estadísticas del catálogo
```sql
SELECT
    tipo_control,
    COUNT(*) AS cantidad,
    ROUND(AVG(efectividad), 2) AS efectividad_promedio
FROM controles_amenazas
GROUP BY tipo_control;
```

### Identificar amenazas sin controles
```sql
SELECT
    a.codigo,
    a.nombre,
    COUNT(ca.id) AS controles_asociados
FROM amenazas a
LEFT JOIN controles_amenazas ca ON ca.amenaza_id = a.id
GROUP BY a.id
HAVING COUNT(ca.id) = 0;
```

### Ver top controles más usados
```sql
SELECT
    ca.control_codigo,
    sc.title,
    COUNT(*) AS amenazas_mitigadas,
    ROUND(AVG(ca.efectividad), 2) AS efectividad_promedio
FROM controles_amenazas ca
LEFT JOIN soa_controls sc ON sc.control_id = ca.control_codigo
WHERE sc.soa_version_id = (SELECT id FROM soa_versions WHERE is_current = true)
GROUP BY ca.control_codigo, sc.title
ORDER BY amenazas_mitigadas DESC
LIMIT 10;
```

---

**Documento**: RESULTADO_IMPLEMENTACION_CATALOGO_CONTROLES.md
**Versión**: 1.0
**Fecha**: 2025-10-25
**Sistema**: ISMS Manager - Módulo de Gestión de Riesgos
**Autor**: Implementación técnica - Integración SOA + MAGERIT
