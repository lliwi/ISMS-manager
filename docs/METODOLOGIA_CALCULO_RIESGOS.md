# Metodología de Cálculo de Riesgos

## Introducción

Este documento describe la metodología empleada para el cálculo automatizado de riesgos de seguridad de la información implementada en el módulo de Gestión de Riesgos del ISMS Manager.

La metodología está basada en **MAGERIT 3.2** (Metodología de Análisis y Gestión de Riesgos de los Sistemas de Información) del CCN-CERT, adaptada para su integración con los controles de **ISO/IEC 27001:2023** (Anexo A - ISO/IEC 27002:2022).

## Conceptos Fundamentales

### Activos de Información
Son los elementos que tienen valor para la organización y requieren protección. Cada activo se valora según las tres dimensiones de seguridad:

- **Confidencialidad (C)**: Protección contra acceso no autorizado
- **Integridad (I)**: Protección contra modificación no autorizada
- **Disponibilidad (D)**: Garantía de acceso cuando se necesite

**Escala de valoración**: 0-5
- 0: No requiere protección
- 1: Muy bajo
- 2: Bajo
- 3: Medio
- 4: Alto
- 5: Crítico (Muy Alto)

### Recursos de Información
Son los componentes físicos o lógicos que soportan los activos de información:
- Hardware (servidores, equipos, dispositivos)
- Software (sistemas operativos, aplicaciones)
- Datos (bases de datos, ficheros)
- Comunicaciones (redes, enlaces)
- Servicios
- Personal
- Otros

Cada tipo de recurso tiene una **importancia tipológica** (1-5) que refleja su valor intrínseco.

### Amenazas
Eventos o acciones que pueden causar daño a los activos. Se clasifican según MAGERIT en grupos:
- **[N] Desastres naturales**: Terremotos, inundaciones, etc.
- **[I] De origen industrial**: Fallos eléctricos, contaminación
- **[E] Errores y fallos no intencionados**: Errores humanos, fallos técnicos
- **[A] Ataques intencionados**: Malware, hacking, sabotaje

Cada amenaza tiene:
- **Frecuencia de ocurrencia**: Probabilidad de que ocurra (0-5)
- **Dimensiones afectadas**: C, I, D (puede afectar a una o varias)

### Controles de Seguridad
Salvaguardas implementadas para mitigar los riesgos, basadas en ISO 27002:2022.

**Fuente de controles**: El sistema utiliza el **SOA (Statement of Applicability) activo** como única fuente de verdad para:
- Definir qué controles son aplicables a la organización
- Determinar el nivel de madurez de cada control implementado
- Obtener evidencias y justificaciones de implementación

Tipos de controles:
- **Preventivos**: Reducen la probabilidad de que ocurra la amenaza
- **Reactivos**: Reducen el impacto si la amenaza se materializa
- **Detectivos**: Permiten detectar cuando ocurre la amenaza
- **Disuasorios**: Desalientan a potenciales atacantes

**Nivel de madurez de los controles** (0-6, escala CMMI normalizada a 0-5 en cálculos):
- 0: No implementado
- 1: Inicial (Ad-hoc, no documentado)
- 2: Repetible (Proceso repetible pero no formal)
- 3: Definido (Proceso documentado y estandarizado)
- 4: Controlado (Proceso medido y controlado)
- 5: Cuantificado (Métricas cuantitativas establecidas)
- 6: Optimizado (Mejora continua basada en métricas)

**Normalización para cálculos**: Los niveles 0-6 del SOA se normalizan a escala 0-5 MAGERIT mediante la fórmula:
```
MADUREZ_NORMALIZADA = min(5, maturity_score × 5.0 / 6.0)
```

## Fórmulas de Cálculo

### Escalas de Valores

El sistema utiliza las siguientes escalas normalizadas:

- **Valores de entrada** (Importancia, Frecuencia, Gravedad, Facilidad): 0-5
- **Probabilidad calculada**: 0-10
- **Impacto calculado**: 0-10
- **Riesgo final**: 0-100 (Probabilidad × Impacto)

### 1. Riesgo Intrínseco

El **riesgo intrínseco** es el riesgo sin considerar ningún control de seguridad (situación de máxima vulnerabilidad).

#### 1.1 Impacto Intrínseco (Escala 0-10)

```
IMPACTO_INTRÍNSECO = ((IP + IT) / 2) × (GRAVₘₐₓ / 5) × 10
```

Donde:
- **IP** = Importancia Propia del activo en la dimensión (0-5)
- **IT** = Importancia Tipológica del recurso (1-5)
- **GRAVₘₐₓ** = 5 (máxima gravedad, sin controles reactivos)
- **Resultado**: Valor entre 0-10

**Ejemplo**: IP=5, IT=4 → Impacto = ((5+4)/2) × (5/5) × 10 = **10.0**

#### 1.2 Probabilidad Intrínseca (Escala 0-10)

```
PROBABILIDAD_INTRÍNSECA = ((FRECUENCIA + FACILₘₐₓ) / 2) × 2
```

Donde:
- **FRECUENCIA** = Frecuencia de ocurrencia de la amenaza (0-5)
- **FACILₘₐₓ** = 5 (máxima facilidad, sin controles preventivos)
- **Resultado**: Valor entre 0-10

**Ejemplo**: Frecuencia=3 → Probabilidad = ((3+5)/2) × 2 = **8.0**

#### 1.3 Nivel de Riesgo Intrínseco (Escala 0-100)

```
RIESGO_INTRÍNSECO = IMPACTO_INTRÍNSECO × PROBABILIDAD_INTRÍNSECA
```

**Ejemplo**: Impacto=10.0, Probabilidad=8.0 → Riesgo = 10 × 8 = **80.0**

### 2. Riesgo Efectivo

El **riesgo efectivo** considera los controles de seguridad actualmente implementados.

#### 2.1 Gravedad de la Vulnerabilidad (Escala 0-5)

La gravedad se reduce mediante controles **reactivos** (que minimizan el impacto):

```
GRAVEDAD = 5 - (Σ(Madurez_normalizada_i × Efectividad_i) / N_controles_reactivos)
```

Donde:
- **Madurez_normalizada_i** = Nivel de madurez del control i del SOA normalizado a escala 0-5
  - Se obtiene del campo `maturity_score` del SOA activo
  - Se normaliza: `min(5, maturity_score × 5.0 / 6.0)`
- **Efectividad_i** = Factor de efectividad del control sobre la amenaza (0.0-1.0)
- **N_controles_reactivos** = Número de controles reactivos aplicables encontrados en el SOA
- **Resultado**: Valor entre 0-5

**Búsqueda de controles**: El sistema busca en el SOA activo los controles:
- Que estén marcados como `applicability_status = 'aplicable'`
- Cuyo `control_id` coincida con los definidos en la relación control-amenaza
- Que tengan `tipo_control = 'REACTIVO'`

Si no hay controles reactivos aplicables: `GRAVEDAD = 5` (máxima vulnerabilidad)

**Ejemplo**:
- Control A.17.1.1 con maturity_score=4 del SOA → Normalizado: 4×5/6 = 3.33
- Efectividad sobre amenaza: 0.8
- Gravedad = 5 - (3.33×0.8/1) = **2.34**

#### 2.2 Facilidad de Explotación (Escala 0-5)

La facilidad se reduce mediante controles **preventivos** (que reducen la probabilidad):

```
FACILIDAD = 5 - (Σ(Madurez_normalizada_j × Efectividad_j) / N_controles_preventivos)
```

Donde:
- **Madurez_normalizada_j** = Nivel de madurez del control j del SOA normalizado a escala 0-5
  - Se obtiene del campo `maturity_score` del SOA activo
  - Se normaliza: `min(5, maturity_score × 5.0 / 6.0)`
- **Efectividad_j** = Factor de efectividad del control sobre la amenaza (0.0-1.0)
- **N_controles_preventivos** = Número de controles preventivos aplicables encontrados en el SOA
- **Resultado**: Valor entre 0-5

**Búsqueda de controles**: El sistema busca en el SOA activo los controles:
- Que estén marcados como `applicability_status = 'aplicable'`
- Cuyo `control_id` coincida con los definidos en la relación control-amenaza
- Que tengan `tipo_control = 'PREVENTIVO'`

Si no hay controles preventivos aplicables: `FACILIDAD = 5` (muy fácil de explotar)

**Ejemplo**:
- Control A.5.1 con maturity_score=5 del SOA → Normalizado: 5×5/6 = 4.17
- Efectividad sobre amenaza: 0.7
- Facilidad = 5 - (4.17×0.7/1) = **2.08**

#### 2.3 Impacto Efectivo (Escala 0-10)

```
IMPACTO_EFECTIVO = ((IP + IT) / 2) × (GRAVEDAD / 5) × 10
```

Donde:
- **IP** = Importancia Propia (0-5)
- **IT** = Importancia Tipológica (1-5)
- **GRAVEDAD** = Gravedad calculada (0-5)
- **Resultado**: Valor entre 0-10

**Ejemplo**: IP=5, IT=4, Gravedad=2.6 → Impacto = ((5+4)/2) × (2.6/5) × 10 = **4.68**

#### 2.4 Probabilidad Efectiva (Escala 0-10)

```
PROBABILIDAD_EFECTIVA = ((FRECUENCIA + FACILIDAD) / 2) × 2
```

Donde:
- **FRECUENCIA** = Frecuencia de la amenaza (0-5)
- **FACILIDAD** = Facilidad calculada (0-5)
- **Resultado**: Valor entre 0-10

**Ejemplo**: Frecuencia=3, Facilidad=2.2 → Probabilidad = ((3+2.2)/2) × 2 = **5.2**

#### 2.5 Nivel de Riesgo Efectivo (Escala 0-100)

```
RIESGO_EFECTIVO = IMPACTO_EFECTIVO × PROBABILIDAD_EFECTIVA
```

**Ejemplo**: Impacto=4.68, Probabilidad=5.2 → Riesgo = 4.68 × 5.2 = **24.34**

### 3. Riesgo Residual

El **riesgo residual** es el riesgo que permanecerá después de implementar controles adicionales planificados.

Se calcula igual que el riesgo efectivo, pero considerando:
- Controles actuales con su madurez real
- Controles planificados con su madurez objetivo esperada

El cálculo sigue las mismas fórmulas que el riesgo efectivo (escala 0-100).

## Matriz de Clasificación de Riesgos

Los riesgos se clasifican según una matriz bidimensional basada en Probabilidad e Impacto (ambos en escala 0-10):

### Umbrales de Clasificación

**Probabilidad (escala 0-10):**
- ALTA: ≥ 7
- MEDIA: 4 - 6.9
- BAJA: < 4

**Impacto (escala 0-10):**
- ALTO: ≥ 7
- MEDIO: 4 - 6.9
- BAJO: < 4

### Matriz de Clasificación

|                | **Impacto BAJO** | **Impacto MEDIO** | **Impacto ALTO** |
|----------------|------------------|-------------------|------------------|
| **Prob. ALTA** | MEDIO            | ALTO              | MUY ALTO         |
| **Prob. MEDIA**| BAJO             | MEDIO             | ALTO             |
| **Prob. BAJA** | MUY BAJO         | BAJO              | MEDIO            |

### Clasificaciones Resultantes

- **MUY ALTO**: Riesgo crítico - Requiere acción inmediata
- **ALTO**: Riesgo significativo - Requiere plan de tratamiento prioritario
- **MEDIO**: Riesgo moderado - Requiere evaluación y seguimiento
- **BAJO**: Riesgo tolerable - Puede aceptarse con seguimiento periódico
- **MUY BAJO**: Riesgo insignificante - Aceptable, seguimiento ocasional

## Proceso de Evaluación de Riesgos

### 1. Identificación de Riesgos

Para cada evaluación, se generan riesgos mediante la combinación de:

```
RIESGO = [Activo] × [Recurso] × [Amenaza] × [Dimensión]
```

**Condiciones de generación:**
- La amenaza debe afectar la dimensión considerada
- El activo debe requerir protección en esa dimensión (valoración > 0)
- Debe existir una relación Activo-Recurso

**Código de riesgo:**
```
R-{ID_EVALUACION}-{ID_ACTIVO}-{ID_RECURSO}-{ID_AMENAZA}-{DIMENSION}
```

Ejemplo: `R-1-5-3-12-C` (Evaluación 1, Activo 5, Recurso 3, Amenaza 12, Confidencialidad)

### 2. Análisis de Riesgos

Para cada riesgo identificado:

1. **Cálculo del riesgo intrínseco**
   - Determina el nivel base sin controles
   - Establece la línea base de referencia

2. **Identificación de controles aplicables**
   - Consulta la tabla `controles_amenazas` para encontrar qué controles (por código, ej: "A.5.1") están relacionados con la amenaza
   - Filtra por tipo: preventivos o reactivos
   - Obtiene el factor de efectividad de cada control sobre la amenaza específica

3. **Evaluación de la implementación de controles**
   - Busca cada control en el **SOA activo** por su `control_id`
   - Verifica que el control esté marcado como `applicability_status = 'aplicable'`
   - Obtiene el `maturity_score` (0-6) del SOA
   - Normaliza la madurez a escala MAGERIT (0-5)
   - Aplica la efectividad del control sobre la amenaza

4. **Cálculo del riesgo efectivo**
   - Aplicación de las fórmulas considerando los controles del SOA
   - Si no hay SOA activo, el riesgo efectivo = riesgo intrínseco (máxima vulnerabilidad)

5. **Clasificación del riesgo**
   - Asignación a categoría según matriz

### 3. Evaluación del Riesgo

Comparación del nivel de riesgo efectivo con el **umbral de riesgo objetivo** de la evaluación (valor por defecto: 50.0 en escala 0-100):

- **Riesgo > Umbral**: Requiere tratamiento
- **Riesgo ≤ Umbral**: Puede aceptarse (según contexto)

**Nota sobre el umbral**: El umbral por defecto es 50.0 (escala 0-100), que representa el 50% del riesgo máximo. Este valor se puede ajustar por evaluación según el apetito de riesgo de la organización.

### 4. Tratamiento del Riesgo

Opciones de tratamiento:
- **Reducir**: Implementar controles adicionales
- **Transferir**: Seguros, outsourcing
- **Evitar**: Eliminar la actividad o activo
- **Aceptar**: Documentar la aceptación formal

## Historial y Trazabilidad

El sistema registra automáticamente:

- **Cambios en el nivel de riesgo**: Cuando se recalcula
- **Cambios en controles**: Al modificar madurez o implementación
- **Cambios en activos**: Al modificar valoraciones
- **Usuario y timestamp**: De cada modificación

Tipos de eventos registrados:
- `CREACION`: Primer cálculo del riesgo
- `RECALCULO`: Recálculo automático programado
- `RECALCULO_MANUAL`: Recálculo solicitado por usuario
- `CAMBIO_CONTROL`: Modificación en controles
- `CAMBIO_ACTIVO`: Modificación en el activo

## Estadísticas y Métricas

### Métricas por Evaluación

- **Total de riesgos identificados**
- **Distribución por clasificación** (Muy Alto, Alto, Medio, Bajo, Muy Bajo)
- **Nivel de riesgo promedio**
- **Nivel de riesgo máximo**
- **Riesgos sobre el umbral objetivo**
- **Porcentaje sobre umbral**

### Métricas por Activo

- **Cantidad de riesgos por activo**
- **Promedio de nivel de riesgo**
- **Riesgos críticos por activo**

### Cobertura de Controles

- **Controles aplicables del SOA activo**: Total de controles marcados como `applicability_status = 'aplicable'`
- **Controles con madurez > 0**: Controles que tienen algún nivel de implementación
- **Nivel de madurez promedio**: Promedio del `maturity_score` de controles aplicables
- **Controles por categoría ISO 27002**: Distribución según la categoría del control
- **Efectividad global**: Porcentaje de reducción del riesgo gracias a los controles implementados

## Visualizaciones

### 1. Matriz de Riesgos (Heatmap)

Representa la distribución de riesgos en una matriz 5×5 de Probabilidad × Impacto.

Cada celda (P, I) contiene:
- Cantidad de riesgos
- Código de colores según nivel

### 2. Gráfico de Distribución

Gráfico tipo donut/pie mostrando:
- Porcentaje de riesgos por clasificación
- Código de colores:
  - Muy Alto: Rojo (#dc3545)
  - Alto: Naranja (#fd7e14)
  - Medio: Amarillo (#ffc107)
  - Bajo: Cyan (#17a2b8)
  - Muy Bajo: Verde (#28a745)

### 3. Top Riesgos Críticos

Listado ordenado descendente por nivel de riesgo efectivo con:
- Activo afectado
- Amenaza
- Dimensión
- Valores de probabilidad e impacto
- Clasificación
- Acciones disponibles

## Ejemplo de Cálculo Completo

### Datos de Entrada

**Activo**: Servidor de base de datos
**Valoración C/I/D**: 5 / 5 / 4

**Recurso**: Hardware - Servidor físico
**Importancia tipológica**: 4

**Amenaza**: [E.23] Errores de mantenimiento / actualización
**Frecuencia**: 3
**Afecta**: Disponibilidad (D)

**Controles aplicables** (del SOA activo):
- Control Preventivo: A.8.8 - Gestión de vulnerabilidades técnicas
  - Madurez SOA (maturity_score): 4 (Controlado)
  - Madurez normalizada: 4 × 5/6 = 3.33
  - Efectividad: 0.8
- Control Reactivo: A.5.29 - Seguridad de la información durante una interrupción
  - Madurez SOA (maturity_score): 3 (Definido)
  - Madurez normalizada: 3 × 5/6 = 2.5
  - Efectividad: 0.7

### Cálculo del Riesgo Intrínseco

```
IP = 4 (Disponibilidad del activo)
IT = 4 (Importancia tipológica)
GRAVₘₐₓ = 5 (sin controles)

IMPACTO_INTRÍNSECO = ((4 + 4) / 2) × (5 / 5) × 10 = 10.0

FRECUENCIA = 3
FACILₘₐₓ = 5 (sin controles)

PROBABILIDAD_INTRÍNSECA = ((3 + 5) / 2) × 2 = 8.0

RIESGO_INTRÍNSECO = 10.0 × 8.0 = 80.0
```

**Resultado**: Riesgo intrínseco = **80.0** (escala 0-100)

### Cálculo del Riesgo Efectivo

**Paso 1: Calcular gravedad con controles reactivos**
```
Madurez normalizada = 2.5 (del SOA)
GRAVEDAD = 5 - ((2.5 × 0.7) / 1) = 5 - 1.75 = 3.25
```

**Paso 2: Calcular impacto efectivo**
```
IMPACTO_EFECTIVO = ((4 + 4) / 2) × (3.25 / 5) × 10 = 6.5
```

**Paso 3: Calcular facilidad con controles preventivos**
```
Madurez normalizada = 3.33 (del SOA)
FACILIDAD = 5 - ((3.33 × 0.8) / 1) = 5 - 2.66 = 2.34
```

**Paso 4: Calcular probabilidad efectiva**
```
PROBABILIDAD_EFECTIVA = ((3 + 2.34) / 2) × 2 = 5.34
```

**Paso 5: Calcular riesgo efectivo**
```
RIESGO_EFECTIVO = 6.5 × 5.34 = 34.71
```

**Reducción del riesgo**: 80.0 → 34.71 (**56.6% de reducción**)

### Clasificación

```
PROBABILIDAD_EFECTIVA = 5.34 → Probabilidad MEDIA (4 ≤ 5.34 < 7)
IMPACTO_EFECTIVO = 6.5 → Impacto MEDIO (4 ≤ 6.5 < 7)

Según matriz: Probabilidad MEDIA + Impacto MEDIO = RIESGO MEDIO
```

### Interpretación

- **Riesgo intrínseco (80.0)**: Sin controles, el riesgo es crítico (MUY ALTO)
- **Riesgo efectivo (34.71)**: Los controles del SOA activo reducen el riesgo a un nivel MEDIO
- **Umbral objetivo (50.0)**: El riesgo efectivo está por debajo del umbral ✓
- **Decisión**: El riesgo puede ser **aceptado** dado que está por debajo del umbral y es de nivel MEDIO
- **Recomendación**: Mantener seguimiento periódico y considerar mejoras incrementales en la madurez de los controles para reducirlo aún más

## Integración con el SOA (Statement of Applicability)

### Arquitectura de Integración

El sistema de gestión de riesgos está completamente integrado con el SOA, que es el documento oficial de ISO 27001 que declara qué controles son aplicables a la organización.

#### Flujo de Datos

```
┌─────────────────────────┐
│   SOA Activo            │  ← Versión actual del SOA
│  (soa_versions)         │     (is_current = true)
│                         │
│  Controles (93):        │
│  - A.5.1, A.5.2, ...    │
│  - maturity_score (0-6) │
│  - applicability_status │
└─────────────────────────┘
         ↑
         │ Búsqueda por control_id
         │
┌─────────────────────────┐
│ controles_amenazas      │  ← Relación control-amenaza
│ ─────────────────────   │
│ control_codigo: "A.5.1" │
│ amenaza_id: FK          │
│ tipo_control: PREV/REAC │
│ efectividad: 0.0-1.0    │
└─────────────────────────┘
         │
         ↓
┌─────────────────────────┐
│  Cálculo de Riesgos     │
│  ─────────────────────  │
│  1. Obtener controles   │
│  2. Buscar en SOA       │
│  3. Normalizar madurez  │
│  4. Calcular riesgo     │
└─────────────────────────┘
```

#### Ventajas de esta Arquitectura

1. **SOA como única fuente de verdad**: No hay duplicación de información sobre implementación de controles
2. **Alineación ISO 27001**: El SOA es un requisito de la norma (cláusula 6.1.3)
3. **Flexibilidad de versiones**: Cambios en el SOA no rompen la estructura de riesgos
4. **Trazabilidad completa**: Cada cálculo de riesgo está vinculado a una versión específica del SOA
5. **Mantenimiento simplificado**: Actualizar la madurez de un control en el SOA actualiza automáticamente todos los cálculos de riesgo

#### Requisitos del Sistema

- **SOA activo obligatorio**: Si no existe un SOA marcado como `is_current = true`, el sistema asume máxima vulnerabilidad (riesgo efectivo = riesgo intrínseco)
- **Controles aplicables**: Solo se consideran controles con `applicability_status = 'aplicable'`
- **Madurez válida**: Controles con `maturity_score = 0` (no implementado) no reducen el riesgo

#### Relación Control-Amenaza

La tabla `controles_amenazas` define qué controles mitigan qué amenazas:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `control_codigo` | VARCHAR(10) | Código del control (ej: "A.5.1") |
| `amenaza_id` | INTEGER | ID de la amenaza |
| `tipo_control` | VARCHAR(20) | PREVENTIVO, REACTIVO, DETECTIVE, DISUASORIO |
| `efectividad` | NUMERIC(3,2) | Factor 0.0-1.0 de efectividad del control sobre esta amenaza |

**Ejemplo**: El control A.5.1 (Políticas de seguridad) es PREVENTIVO con efectividad 0.8 sobre la amenaza E.1 (Errores de usuarios).

### Gestión de Versiones del SOA

El sistema soporta múltiples versiones del SOA:

- **Versión activa**: Aquella con `is_current = true` (solo puede haber una)
- **Versiones históricas**: Versiones anteriores del SOA conservadas para trazabilidad
- **Versionado de riesgos**: Cada evaluación de riesgos puede asociarse a una versión específica del SOA

**Proceso de cambio de versión**:
1. Crear nueva versión del SOA (duplicando la actual o desde cero)
2. Modificar controles, madurez, aplicabilidad
3. Marcar nueva versión como activa (`is_current = true`)
4. El sistema automáticamente:
   - Usa la nueva versión para nuevos cálculos
   - Mantiene trazabilidad de qué versión del SOA se usó en cada evaluación histórica

### Niveles de Madurez CMMI

El SOA utiliza la escala CMMI (Capability Maturity Model Integration) de 7 niveles (0-6):

| Nivel | Nombre | Descripción | Normalización MAGERIT |
|-------|--------|-------------|-----------------------|
| 0 | No implementado | Control no existe | 0.00 |
| 1 | Inicial | Ad-hoc, sin documentación | 0.83 |
| 2 | Repetible | Proceso repetible | 1.67 |
| 3 | Definido | Documentado y estandarizado | 2.50 |
| 4 | Controlado | Medido y controlado | 3.33 |
| 5 | Cuantificado | Métricas cuantitativas | 4.17 |
| 6 | Optimizado | Mejora continua | 5.00 |

**Fórmula de normalización**: `MAGERIT = min(5, SOA_maturity × 5.0 / 6.0)`

Esta normalización permite que el nivel máximo del SOA (6) se traduzca al nivel máximo de MAGERIT (5), manteniendo la proporcionalidad.

## Referencias

- **MAGERIT v3.2**: Metodología de Análisis y Gestión de Riesgos de los Sistemas de Información (CCN-CERT)
- **ISO/IEC 27001:2023**: Sistemas de gestión de la seguridad de la información — Requisitos
- **ISO/IEC 27002:2022**: Código de prácticas para los controles de seguridad de la información
- **ISO 31000:2018**: Gestión del riesgo — Directrices
- **CMMI**: Capability Maturity Model Integration

---

**Documento**: METODOLOGIA_CALCULO_RIESGOS.md
**Versión**: 2.0
**Fecha**: 2025-10-25
**Sistema**: ISMS Manager - Módulo de Gestión de Riesgos
**Última actualización**: Integración con SOA como fuente única de controles
