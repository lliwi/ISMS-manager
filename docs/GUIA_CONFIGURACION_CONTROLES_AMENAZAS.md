# Guía de Configuración: Relaciones Control-Amenaza

## Fecha
2025-10-25

## Propósito
Este documento explica cómo establecer las relaciones entre controles del SOA y amenazas para que el sistema pueda calcular la reducción del riesgo efectivo.

---

## ¿Por Qué Son Necesarias?

Las relaciones **control-amenaza** son fundamentales para el cálculo de riesgos porque:

1. **Definen qué controles mitigan qué amenazas**
2. **Especifican la efectividad** de cada control contra cada amenaza
3. **Clasifican el tipo de control** (preventivo o reactivo)
4. **Permiten calcular el riesgo efectivo** (residual) después de aplicar controles

Sin estas relaciones:
- ❌ Riesgo efectivo = Riesgo intrínseco (sin reducción)
- ❌ Los controles del SOA no tienen efecto en el cálculo
- ❌ No se puede medir la eficacia de los controles implementados

---

## Estructura de la Tabla `controles_amenazas`

```sql
CREATE TABLE controles_amenazas (
    id SERIAL PRIMARY KEY,
    control_codigo VARCHAR(10) NOT NULL,      -- Código del control SOA (ej: "A.5.1")
    amenaza_id INTEGER NOT NULL,              -- ID de la amenaza
    tipo_control VARCHAR(20) NOT NULL,        -- PREVENTIVO, REACTIVO, DETECTIVE, DISUASORIO
    efectividad NUMERIC(3,2) DEFAULT 1.00,    -- 0.0 - 1.0
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_control_amenaza UNIQUE (control_codigo, amenaza_id)
);
```

### Campos Explicados

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| **control_codigo** | VARCHAR(10) | Código del control en el SOA | "A.5.1", "A.8.8", "A.17.1" |
| **amenaza_id** | INTEGER | ID de la amenaza en la tabla `amenazas` | 15 |
| **tipo_control** | VARCHAR(20) | Tipo de control | "PREVENTIVO" o "REACTIVO" |
| **efectividad** | NUMERIC(3,2) | Qué tan efectivo es el control (0.0-1.0) | 0.80 (80% efectivo) |

---

## Tipos de Control

### PREVENTIVO
Reduce la **probabilidad** de que ocurra la amenaza.

**Ejemplos**:
- A.5.1 - Políticas de seguridad
- A.5.15 - Control de accesos
- A.8.8 - Gestión de vulnerabilidades técnicas

**Efecto**: Disminuye la frecuencia con que puede materializarse la amenaza.

### REACTIVO
Reduce el **impacto** si la amenaza se materializa.

**Ejemplos**:
- A.5.29 - Seguridad durante interrupciones
- A.5.30 - Preparación de TIC para continuidad
- A.17.1 - Continuidad de seguridad de la información

**Efecto**: Disminuye el daño causado cuando ocurre la amenaza.

### DETECTIVE (opcional)
Detecta cuando ocurre la amenaza.

**Ejemplos**:
- A.6.8 - Reporte de eventos de seguridad
- A.8.16 - Monitorización de actividades

### DISUASORIO (opcional)
Disuade a potenciales atacantes.

**Ejemplos**:
- A.5.18 - Derechos de acceso
- A.7.8 - Pantallas y escritorios despejados

---

## Efectividad (0.0 - 1.0)

La efectividad representa **qué tan bien el control mitiga la amenaza específica**.

| Valor | Significado | Cuándo usar |
|-------|-------------|-------------|
| **1.0** | Totalmente efectivo (100%) | El control elimina completamente la amenaza |
| **0.8-0.9** | Altamente efectivo | El control reduce significativamente la amenaza |
| **0.5-0.7** | Moderadamente efectivo | El control reduce parcialmente la amenaza |
| **0.3-0.4** | Poco efectivo | El control tiene un efecto limitado |
| **0.1-0.2** | Mínimamente efectivo | El control apenas mitiga la amenaza |
| **0.0** | No efectivo | No usar (eliminar la relación) |

### Ejemplos Prácticos

**Amenaza: E.1 - Errores de los usuarios**

| Control | Tipo | Efectividad | Justificación |
|---------|------|-------------|---------------|
| A.5.1 - Políticas de seguridad | PREVENTIVO | 0.70 | Las políticas educan y guían, pero no eliminan todos los errores |
| A.6.3 - Concienciación en seguridad | PREVENTIVO | 0.85 | La capacitación reduce significativamente errores humanos |
| A.5.30 - Continuidad TIC | REACTIVO | 0.60 | Permite recuperarse de errores, pero no los previene |

**Amenaza: A.40 - Denegación de servicio**

| Control | Tipo | Efectividad | Justificación |
|---------|------|-------------|---------------|
| A.8.20 - Seguridad de redes | PREVENTIVO | 0.80 | Firewalls y filtrado previenen muchos ataques DDoS |
| A.8.6 - Gestión de capacidad | PREVENTIVO | 0.50 | Sobredimensionar ayuda, pero no previene ataques dirigidos |
| A.5.29 - Seguridad durante interrupciones | REACTIVO | 0.75 | Permite mantener servicios mínimos durante ataque |

---

## Cómo Establecer las Relaciones

### Opción 1: SQL Directo (Recomendado para Bulk)

```sql
-- Obtener el ID de la amenaza
SELECT id, codigo, nombre FROM amenazas WHERE codigo = 'E.1';
-- Resultado: id = 15, codigo = 'E.1', nombre = 'Errores de los usuarios'

-- Insertar relaciones control-amenaza
INSERT INTO controles_amenazas (control_codigo, amenaza_id, tipo_control, efectividad)
VALUES
  -- Controles preventivos
  ('A.5.1', 15, 'PREVENTIVO', 0.70),   -- Políticas de seguridad
  ('A.6.3', 15, 'PREVENTIVO', 0.85),   -- Concienciación en seguridad
  ('A.5.15', 15, 'PREVENTIVO', 0.60),  -- Control de accesos

  -- Controles reactivos
  ('A.5.30', 15, 'REACTIVO', 0.60),    -- Continuidad TIC
  ('A.5.29', 15, 'REACTIVO', 0.50);    -- Seguridad durante interrupciones
```

### Opción 2: Python/Flask Shell

```python
from app.risks.models import ControlAmenaza, Amenaza
from models import db

# Buscar la amenaza
amenaza = Amenaza.query.filter_by(codigo='E.1').first()

# Crear relaciones
controles = [
    ControlAmenaza(
        control_codigo='A.5.1',
        amenaza_id=amenaza.id,
        tipo_control='PREVENTIVO',
        efectividad=0.70
    ),
    ControlAmenaza(
        control_codigo='A.6.3',
        amenaza_id=amenaza.id,
        tipo_control='PREVENTIVO',
        efectividad=0.85
    ),
]

db.session.add_all(controles)
db.session.commit()
```

### Opción 3: Script de Migración (Para Datos Iniciales)

Crear archivo `migrations/015_seed_controles_amenazas_magerit.sql`:

```sql
-- Relaciones para amenazas de tipo Error (E.*)
INSERT INTO controles_amenazas (control_codigo, amenaza_id, tipo_control, efectividad)
SELECT
    control,
    a.id,
    tipo,
    efectividad
FROM (VALUES
    ('A.5.1', 'E.1', 'PREVENTIVO', 0.70),
    ('A.6.3', 'E.1', 'PREVENTIVO', 0.85),
    ('A.5.1', 'E.2', 'PREVENTIVO', 0.75),
    ('A.6.3', 'E.2', 'PREVENTIVO', 0.80)
) AS v(control, amenaza_codigo, tipo, efectividad)
JOIN amenazas a ON a.codigo = v.amenaza_codigo
ON CONFLICT (control_codigo, amenaza_id) DO NOTHING;
```

---

## Verificación de las Relaciones

### Consultar controles de una amenaza específica

```sql
SELECT
    ca.control_codigo,
    ca.tipo_control,
    ca.efectividad,
    sc.title AS control_nombre,
    sc.maturity_score AS madurez_soa
FROM controles_amenazas ca
JOIN amenazas a ON ca.amenaza_id = a.id
LEFT JOIN soa_controls sc ON sc.control_id = ca.control_codigo
    AND sc.soa_version_id = (SELECT id FROM soa_versions WHERE is_current = true)
WHERE a.codigo = 'E.1'
ORDER BY ca.tipo_control, ca.efectividad DESC;
```

### Resultado esperado:

```
 control_codigo | tipo_control | efectividad |           control_nombre            | madurez_soa
----------------+--------------+-------------+-------------------------------------+-------------
 A.6.3          | PREVENTIVO   |        0.85 | Concienciación en seguridad         |           4
 A.5.1          | PREVENTIVO   |        0.70 | Políticas de seguridad              |           5
 A.5.15         | PREVENTIVO   |        0.60 | Control de accesos                  |           3
 A.5.30         | REACTIVO     |        0.60 | Continuidad TIC                     |           2
 A.5.29         | REACTIVO     |        0.50 | Seguridad durante interrupciones    |           3
```

---

## Visualización en la Aplicación

Una vez configuradas las relaciones, al acceder a un riesgo específico (`/riesgos/riesgos/<id>`), verás:

### Con controles configurados:

**Controles Preventivos** (columna izquierda):
- Lista de controles con su código
- Efectividad en porcentaje
- Nivel de madurez del SOA
- Estado de aplicabilidad

**Controles Reactivos** (columna derecha):
- Lista de controles con su código
- Efectividad en porcentaje
- Nivel de madurez del SOA
- Estado de aplicabilidad

### Sin controles configurados:

Aparecerá una guía con:
- Alertas indicando que no hay controles
- Instrucciones SQL para crearlos
- Link al SOA para consultar controles disponibles
- Explicación de los campos necesarios

---

## Estrategia de Implementación

### Fase 1: Controles Críticos (Semana 1)

Establecer relaciones para las 10 amenazas más frecuentes:

```sql
-- Amenazas críticas típicas
SELECT codigo, nombre, COUNT(r.id) AS riesgos_asociados
FROM amenazas a
LEFT JOIN riesgos r ON r.amenaza_id = a.id
GROUP BY a.id
ORDER BY riesgos_asociados DESC
LIMIT 10;
```

Para cada una, definir al menos:
- 2 controles preventivos (alta efectividad)
- 1 control reactivo

### Fase 2: Cobertura Completa (Mes 1)

Expandir a todas las amenazas del catálogo MAGERIT (88 amenazas).

**Referencia**: Usar matriz de controles-amenazas MAGERIT como guía.

### Fase 3: Refinamiento (Mes 2-3)

Ajustar efectividades basándose en:
- Experiencia real
- Resultados de auditorías
- Incidentes históricos

---

## Referencias y Recursos

### Consultar Controles Disponibles en el SOA

```sql
SELECT
    control_id,
    title,
    category,
    maturity_score,
    applicability_status
FROM soa_controls
WHERE soa_version_id = (SELECT id FROM soa_versions WHERE is_current = true)
  AND applicability_status = 'aplicable'
ORDER BY control_id;
```

### Consultar Amenazas del Catálogo

```sql
SELECT
    codigo,
    nombre,
    tipo_amenaza,
    afecta_c,
    afecta_i,
    afecta_d
FROM amenazas
ORDER BY codigo;
```

### Matriz de Ejemplo: Controles vs Tipos de Amenaza

| Tipo de Amenaza | Controles Preventivos Recomendados | Controles Reactivos Recomendados |
|-----------------|-------------------------------------|----------------------------------|
| **E.* (Errores)** | A.5.1, A.6.3, A.5.15 | A.5.30, A.5.29 |
| **I.* (Desastres)** | A.7.13, A.8.1 | A.5.29, A.5.30, A.17.1 |
| **A.* (Ataques)** | A.5.15, A.8.8, A.8.20 | A.6.8, A.5.24, A.5.29 |

---

## Troubleshooting

### Problema: Los controles no aparecen en la vista del riesgo

**Causa**: No hay relaciones en `controles_amenazas` para esa amenaza.

**Solución**:
```sql
INSERT INTO controles_amenazas (control_codigo, amenaza_id, tipo_control, efectividad)
VALUES ('A.5.1', <amenaza_id>, 'PREVENTIVO', 0.75);
```

### Problema: El riesgo efectivo = riesgo intrínseco

**Causas posibles**:
1. No hay controles definidos → Crear relaciones
2. Controles con madurez = 0 en SOA → Actualizar maturity_score en SOA
3. Controles marcados como 'no_aplicable' → Cambiar applicability_status

**Verificación**:
```sql
SELECT
    ca.control_codigo,
    sc.maturity_score,
    sc.applicability_status
FROM controles_amenazas ca
JOIN amenazas a ON ca.amenaza_id = a.id
LEFT JOIN soa_controls sc ON sc.control_id = ca.control_codigo
WHERE a.id = <amenaza_id>;
```

### Problema: Efectividad muy baja no reduce el riesgo

**Causa**: Valor de efectividad demasiado bajo.

**Solución**: Ajustar efectividad a valores realistas (>= 0.5 para controles significativos).

---

## Conclusión

Las relaciones **control-amenaza** son el vínculo entre:
- El **SOA** (qué controles tienes y su nivel de madurez)
- Las **amenazas** (qué riesgos enfrenta la organización)
- El **cálculo de riesgo** (cuánto se reduce el riesgo con los controles)

**Siguientes pasos**:
1. Consultar SOA en http://localhost/soa/
2. Identificar controles aplicables
3. Crear relaciones usando SQL o Python
4. Verificar en vista de riesgo que aparecen
5. Recalcular riesgos y ver reducción

---

**Documento**: GUIA_CONFIGURACION_CONTROLES_AMENAZAS.md
**Versión**: 1.0
**Fecha**: 2025-10-25
**Sistema**: ISMS Manager - Módulo de Gestión de Riesgos
