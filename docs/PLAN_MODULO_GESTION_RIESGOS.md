# PLAN DEL MÓDULO DE GESTIÓN DE RIESGOS
## Sistema de Gestión de Seguridad de la Información (SGSI)

**Fecha**: 2025-10-23
**Versión**: 1.0
**Basado en**: ISO/IEC 27001:2023, ISO/IEC 27005:2022, ISO 31000:2018, MAGERIT 3.2

---

## 1. RESUMEN EJECUTIVO

El módulo de Gestión de Riesgos es un componente crítico del SGSI que permite identificar, evaluar, tratar y monitorizar los riesgos de seguridad de la información de manera sistemática y conforme a las normativas internacionales.

### Objetivos Principales:
- Cumplir con los requisitos de ISO 27001:2023 (apartados 6.1.2 y 6.1.3)
- Implementar metodología cuantitativa basada en MAGERIT 3.2
- Proporcionar cálculo automático de riesgos mediante fórmulas validadas
- Facilitar la toma de decisiones basada en datos sobre tratamiento de riesgos
- Generar trazabilidad completa del proceso de gestión de riesgos

---

## 2. MARCO NORMATIVO Y METODOLÓGICO

### 2.1 Requisitos Normativos (ISO 27001:2023)

#### Apartado 6.1.2 - Evaluación de Riesgos
La organización debe definir y aplicar un proceso que:
- Establezca criterios de aceptación y evaluación de riesgos
- Identifique riesgos relacionados con pérdida de C-I-D
- Identifique propietarios de riesgos
- Analice consecuencias potenciales
- Valore probabilidad de ocurrencia realista
- Determine niveles de riesgo
- Compare resultados con criterios establecidos
- Priorice riesgos para tratamiento

#### Apartado 6.1.3 - Tratamiento de Riesgos
El proceso debe:
- Seleccionar opciones de tratamiento adecuadas
- Determinar controles necesarios
- Comparar controles con Anexo A ISO 27001
- Elaborar Declaración de Aplicabilidad (SOA)
- Formular plan de tratamiento
- Obtener aprobación de propietarios de riesgos

### 2.2 Metodología de Cálculo (Basada en Documentos de Referencia)

#### Fórmula Principal del Riesgo
```
RIESGO = PROBABILIDAD × IMPACTO
```

#### Cálculo del IMPACTO
```
IMPACTO = IMPORTANCIA_ACTIVO × GRAVEDAD_VULNERABILIDAD × |V|

Donde:
- IMPORTANCIA_ACTIVO = Importancia_Propia (IP) × Importancia_Tipológica (IT)
- |V| = Módulo normalizador = √((IP² + IT²) / 50)
- GRAVEDAD_VULNERABILIDAD = f(Controles Reactivos)
```

**Importancia Propia (IP)**: Valoración C-I-D del activo (0-5)
- 0: No aplica
- 1: Baja
- 2: Media
- 3: Alta
- 4: Muy Alta
- 5: Crítica

**Importancia Tipológica (IT)**: Según tipo de recurso
- 1: Documentación, ubicaciones
- 2: Personas, organización
- 3: Software, redes
- 4: Hardware, equipamiento
- 5: Datos, información crítica

**Gravedad de Vulnerabilidad**:
```
GRAVEDAD = 5 - (∑ Controles_Reactivos_Aplicables × Madurez) / N_Controles_Reactivos

Si no hay controles: GRAVEDAD = 5
```

#### Cálculo de la PROBABILIDAD
```
PROBABILIDAD = FRECUENCIA_AMENAZA × FACILIDAD_EXPLOTACIÓN × |V|

Donde:
- FRECUENCIA_AMENAZA: Tasa anual de ocurrencia
- FACILIDAD_EXPLOTACIÓN = f(Controles Preventivos)
- |V| = √((FRECUENCIA² + FACILIDAD²) / 50)
```

**Frecuencia de Amenazas (FA)**:
- 0: No aplica
- 1: Muy baja (>10 años)
- 2: Baja (5-10 años)
- 3: Media (1-5 años)
- 4: Alta (meses)
- 5: Muy alta (días/semanas)

**Facilidad de Explotación**:
```
FACILIDAD = 5 - (∑ Controles_Preventivos_Aplicables × Madurez) / N_Controles_Preventivos

Si no hay controles: FACILIDAD = 5
```

#### Niveles de Madurez de Controles (CMM)
- 0: No existe
- 1: Inicial/Ad-hoc
- 2: Reproducible
- 3: Definido
- 4: Gestionado
- 5: Optimizado

### 2.3 Matriz de Riesgo

| Probabilidad / Impacto | **Bajo (1-5)** | **Medio (6-12)** | **Alto (13-25)** |
|------------------------|----------------|------------------|------------------|
| **Alto (13-25)**       | **Medio**      | **Alto**         | **Muy Alto**     |
| **Medio (6-12)**       | **Bajo**       | **Medio**        | **Alto**         |
| **Bajo (1-5)**         | **Muy Bajo**   | **Bajo**         | **Medio**        |

### 2.4 Catálogo de Amenazas (MAGERIT 3.2)

#### Grupo 1: Desastres Naturales
1.1 Fuego
1.2 Inundación
1.3 Fenómenos sísmicos
1.4 Contaminación mecánica
1.5 Contaminación electromagnética

#### Grupo 2: De Origen Industrial
1.6 Fallos en HW/SW
1.7 Interrupción de energía
1.8 Condiciones inadecuadas de humedad/temperatura
1.9 Fallo en comunicaciones

#### Grupo 3: Errores y Fallos No Intencionados
2.1 Error humano
2.2 Error de configuración
2.3 Error de monitorización
2.4 Deficiencias organizacionales
2.5 Difusión involuntaria de malware
2.10 Defectos en mantenimiento HW
2.11 Fallo en el sistema
2.12 Insuficiencia de personal

#### Grupo 4: Ataques Intencionados
3.1 Manipulación de configuración
3.2 Suplantación de identidad
3.3 Abuso de privilegios
3.4 Uso no autorizado
3.5 Difusión maliciosa de malware
3.6 Acceso no autorizado
3.7 Intercepción de información
3.8 Alteración de información
3.9 Destrucción de información
3.10 Divulgación de información
3.11 Manipulación de software
3.12 Denegación de servicio
3.13 Robo
3.14 Ingeniería social

---

## 3. MODELO DE DATOS

### 3.1 Diagrama Entidad-Relación

```
PROCESOS_NEGOCIO (1) ──< (N) ACTIVOS_INFORMACION (N) >── (M) RECURSOS_INFORMACION
                                    │
                                    │
                                    v
                            VALORACIONES_CIA
                                    │
                                    │
                                    v
                        RIESGOS ─< AMENAZAS_RECURSOS
                            │              │
                            │              v
                            │         AMENAZAS
                            │              │
                            v              v
                    TRATAMIENTOS    CONTROLES_ISO27002
                            │              │
                            v              v
                    PLAN_ACCION    SALVAGUARDAS_IMPLANTADAS
                                          │
                                          v
                                   EVALUACION_MADUREZ
```

### 3.2 Tablas Principales

#### 3.2.1 `procesos_negocio`
```sql
CREATE TABLE procesos_negocio (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    area_responsable VARCHAR(100),
    criticidad INTEGER CHECK (criticidad BETWEEN 1 AND 5),
    responsable_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_procesos_criticidad ON procesos_negocio(criticidad);
CREATE INDEX idx_procesos_responsable ON procesos_negocio(responsable_id);
```

#### 3.2.2 `activos_informacion`
```sql
CREATE TABLE activos_informacion (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    tipo_activo VARCHAR(20) NOT NULL, -- DAT, DOC, SW, HW, NET, PE, S, etc.
    funcion TEXT,
    ubicacion VARCHAR(200),
    propietario_id INTEGER REFERENCES users(id),
    estado VARCHAR(20) DEFAULT 'activo', -- activo, inactivo, retirado

    -- Valoración CIA (1-5)
    confidencialidad INTEGER CHECK (confidencialidad BETWEEN 0 AND 5),
    integridad INTEGER CHECK (integridad BETWEEN 0 AND 5),
    disponibilidad INTEGER CHECK (disponibilidad BETWEEN 0 AND 5),

    -- Justificación de la valoración
    justificacion_c TEXT,
    justificacion_i TEXT,
    justificacion_d TEXT,

    -- Importancia calculada
    importancia_propia DECIMAL(5,2), -- Máximo de C-I-D

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_tipo_activo CHECK (tipo_activo IN ('AP', 'CPD', 'CL', 'DAT', 'DOC', 'FW', 'HW', 'NET', 'OS', 'OT', 'PE', 'ST', 'SW', 'SU', 'TL', 'S', 'INST'))
);

CREATE INDEX idx_activos_tipo ON activos_informacion(tipo_activo);
CREATE INDEX idx_activos_propietario ON activos_informacion(propietario_id);
CREATE INDEX idx_activos_estado ON activos_informacion(estado);
```

#### 3.2.3 `activos_procesos` (Relación M:N)
```sql
CREATE TABLE activos_procesos (
    id SERIAL PRIMARY KEY,
    activo_id INTEGER REFERENCES activos_informacion(id) ON DELETE CASCADE,
    proceso_id INTEGER REFERENCES procesos_negocio(id) ON DELETE CASCADE,
    rol_raci VARCHAR(1) CHECK (rol_raci IN ('R', 'A', 'C', 'I')), -- RACI matrix
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(activo_id, proceso_id)
);

CREATE INDEX idx_actproc_activo ON activos_procesos(activo_id);
CREATE INDEX idx_actproc_proceso ON activos_procesos(proceso_id);
```

#### 3.2.4 `recursos_informacion`
```sql
CREATE TABLE recursos_informacion (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    tipo_recurso VARCHAR(20) NOT NULL, -- HW, SW, RED, PERSONAS, UBICACION, etc.
    importancia_tipologica INTEGER NOT NULL CHECK (importancia_tipologica BETWEEN 1 AND 5),
    responsable_id INTEGER REFERENCES users(id),
    ubicacion VARCHAR(200),
    estado VARCHAR(20) DEFAULT 'operativo',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_tipo_recurso CHECK (tipo_recurso IN ('HARDWARE', 'SOFTWARE', 'RED', 'PERSONAS', 'UBICACION', 'DATOS', 'SERVICIOS'))
);

CREATE INDEX idx_recursos_tipo ON recursos_informacion(tipo_recurso);
CREATE INDEX idx_recursos_responsable ON recursos_informacion(responsable_id);
```

#### 3.2.5 `activos_recursos` (Relación M:N)
```sql
CREATE TABLE activos_recursos (
    id SERIAL PRIMARY KEY,
    activo_id INTEGER REFERENCES activos_informacion(id) ON DELETE CASCADE,
    recurso_id INTEGER REFERENCES recursos_informacion(id) ON DELETE CASCADE,
    tipo_uso VARCHAR(50), -- almacena, procesa, transmite, accede
    criticidad INTEGER CHECK (criticidad BETWEEN 1 AND 5),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(activo_id, recurso_id)
);

CREATE INDEX idx_actrec_activo ON activos_recursos(activo_id);
CREATE INDEX idx_actrec_recurso ON activos_recursos(recurso_id);
```

#### 3.2.6 `amenazas`
```sql
CREATE TABLE amenazas (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL, -- ej: 1.1, 2.5, 3.14
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    grupo VARCHAR(50) NOT NULL, -- NATURALES, INDUSTRIALES, ERRORES, ATAQUES
    categoria MAGERIT VARCHAR(50),

    -- Aplicabilidad por dimensión
    afecta_confidencialidad BOOLEAN DEFAULT false,
    afecta_integridad BOOLEAN DEFAULT false,
    afecta_disponibilidad BOOLEAN DEFAULT false,

    -- Controles de aplicación
    es_preventiva BOOLEAN DEFAULT true,
    es_reactiva BOOLEAN DEFAULT false,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_grupo CHECK (grupo IN ('NATURALES', 'INDUSTRIALES', 'ERRORES', 'ATAQUES'))
);

CREATE INDEX idx_amenazas_grupo ON amenazas(grupo);
CREATE INDEX idx_amenazas_codigo ON amenazas(codigo);
```

#### 3.2.7 `amenazas_recursos_tipo` (Aplicabilidad)
```sql
CREATE TABLE amenazas_recursos_tipo (
    id SERIAL PRIMARY KEY,
    amenaza_id INTEGER REFERENCES amenazas(id) ON DELETE CASCADE,
    tipo_recurso VARCHAR(20) NOT NULL,

    -- Frecuencia de ocurrencia (0-5)
    frecuencia_base INTEGER CHECK (frecuencia_base BETWEEN 0 AND 5),

    dimension_afectada VARCHAR(1) CHECK (dimension_afectada IN ('C', 'I', 'D')),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(amenaza_id, tipo_recurso, dimension_afectada)
);

CREATE INDEX idx_amrectipo_amenaza ON amenazas_recursos_tipo(amenaza_id);
CREATE INDEX idx_amrectipo_tipo ON amenazas_recursos_tipo(tipo_recurso);
```

#### 3.2.8 `controles_iso27002`
```sql
CREATE TABLE controles_iso27002 (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL, -- A.5.1, A.8.23, etc.
    nombre VARCHAR(300) NOT NULL,
    descripcion TEXT,
    categoria VARCHAR(50) NOT NULL, -- Organizacionales, Personas, Físicos, Tecnológicos
    tipo_control VARCHAR(20) NOT NULL, -- PREVENTIVO, REACTIVO, DETECTIVE

    -- Referencias cruzadas
    codigo_iso27001_2013 VARCHAR(20), -- Mapeo con versión anterior
    codigo_tisax VARCHAR(20), -- Integración TISAX

    objetivo TEXT,
    guia_implementacion TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_categoria CHECK (categoria IN ('ORGANIZACIONALES', 'PERSONAS', 'FISICOS', 'TECNOLOGICOS')),
    CONSTRAINT valid_tipo CHECK (tipo_control IN ('PREVENTIVO', 'REACTIVO', 'DETECTIVE', 'DISUASORIO'))
);

CREATE INDEX idx_controles_categoria ON controles_iso27002(categoria);
CREATE INDEX idx_controles_tipo ON controles_iso27002(tipo_control);
CREATE INDEX idx_controles_codigo ON controles_iso27002(codigo);
```

#### 3.2.9 `controles_amenazas` (Aplicabilidad)
```sql
CREATE TABLE controles_amenazas (
    id SERIAL PRIMARY KEY,
    control_id INTEGER REFERENCES controles_iso27002(id) ON DELETE CASCADE,
    amenaza_id INTEGER REFERENCES amenazas(id) ON DELETE CASCADE,
    efectividad DECIMAL(3,2) DEFAULT 1.00, -- Factor de efectividad 0.0-1.0

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(control_id, amenaza_id)
);

CREATE INDEX idx_ctrlam_control ON controles_amenazas(control_id);
CREATE INDEX idx_ctrlam_amenaza ON controles_amenazas(amenaza_id);
```

#### 3.2.10 `salvaguardas_implantadas`
```sql
CREATE TABLE salvaguardas_implantadas (
    id SERIAL PRIMARY KEY,
    control_id INTEGER REFERENCES controles_iso27002(id),

    -- Nivel de madurez (CMM: 0-5)
    nivel_madurez INTEGER CHECK (nivel_madurez BETWEEN 0 AND 5),

    -- Detalles de implementación
    descripcion_implementacion TEXT,
    evidencias TEXT,
    responsable_id INTEGER REFERENCES users(id),
    fecha_implementacion DATE,
    fecha_ultima_revision DATE,

    -- Estado
    estado VARCHAR(20) DEFAULT 'implementado', -- planificado, en_progreso, implementado, verificado

    -- Aplicabilidad
    aplica BOOLEAN DEFAULT true,
    justificacion_no_aplica TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_estado CHECK (estado IN ('planificado', 'en_progreso', 'implementado', 'verificado', 'no_aplica'))
);

CREATE INDEX idx_salvag_control ON salvaguardas_implantadas(control_id);
CREATE INDEX idx_salvag_responsable ON salvaguardas_implantadas(responsable_id);
CREATE INDEX idx_salvag_estado ON salvaguardas_implantadas(estado);
```

#### 3.2.11 `evaluaciones_riesgo`
```sql
CREATE TABLE evaluaciones_riesgo (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE,
    estado VARCHAR(20) DEFAULT 'en_curso', -- planificada, en_curso, completada, aprobada

    -- Criterios de aceptación
    umbral_riesgo_objetivo DECIMAL(5,2) DEFAULT 12.00, -- Nivel por debajo se acepta

    -- Alcance
    alcance_descripcion TEXT,

    -- Responsables
    responsable_evaluacion_id INTEGER REFERENCES users(id),
    aprobador_id INTEGER REFERENCES users(id),
    fecha_aprobacion DATE,

    -- Versionado
    version VARCHAR(20),
    evaluacion_anterior_id INTEGER REFERENCES evaluaciones_riesgo(id),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_estado_eval CHECK (estado IN ('planificada', 'en_curso', 'completada', 'aprobada', 'obsoleta'))
);

CREATE INDEX idx_eval_estado ON evaluaciones_riesgo(estado);
CREATE INDEX idx_eval_responsable ON evaluaciones_riesgo(responsable_evaluacion_id);
CREATE INDEX idx_eval_fecha ON evaluaciones_riesgo(fecha_inicio);
```

#### 3.2.12 `riesgos`
```sql
CREATE TABLE riesgos (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL, -- R-2025-001
    evaluacion_id INTEGER REFERENCES evaluaciones_riesgo(id) ON DELETE CASCADE,

    -- Relaciones
    activo_id INTEGER REFERENCES activos_informacion(id),
    recurso_id INTEGER REFERENCES recursos_informacion(id),
    amenaza_id INTEGER REFERENCES amenazas(id),

    -- Dimensión afectada
    dimension VARCHAR(1) CHECK (dimension IN ('C', 'I', 'D')),

    -- Cálculos de RIESGO INTRÍNSECO (sin controles)
    importancia_propia DECIMAL(5,2),
    importancia_tipologica INTEGER,
    modulo_normalizador_impacto DECIMAL(5,4),

    frecuencia_amenaza INTEGER,
    modulo_normalizador_probabilidad DECIMAL(5,4),

    impacto_intrinseco DECIMAL(8,2),
    probabilidad_intrinseca DECIMAL(8,2),
    nivel_riesgo_intrinseco DECIMAL(10,2),

    -- Cálculos de RIESGO EFECTIVO (con controles actuales)
    gravedad_vulnerabilidad DECIMAL(5,2),
    facilidad_explotacion DECIMAL(5,2),
    num_controles_reactivos INTEGER DEFAULT 0,
    num_controles_preventivos INTEGER DEFAULT 0,

    impacto_efectivo DECIMAL(8,2),
    probabilidad_efectiva DECIMAL(8,2),
    nivel_riesgo_efectivo DECIMAL(10,2),

    -- Cálculos de RIESGO RESIDUAL (con controles planificados)
    impacto_residual DECIMAL(8,2),
    probabilidad_residual DECIMAL(8,2),
    nivel_riesgo_residual DECIMAL(10,2),

    -- Clasificación cualitativa
    clasificacion_intrinseca VARCHAR(20), -- MUY_BAJO, BAJO, MEDIO, ALTO, MUY_ALTO
    clasificacion_efectiva VARCHAR(20),
    clasificacion_residual VARCHAR(20),

    -- Propietario del riesgo
    propietario_riesgo_id INTEGER REFERENCES users(id),

    -- Observaciones
    observaciones TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_clasificacion CHECK (clasificacion_efectiva IN ('MUY_BAJO', 'BAJO', 'MEDIO', 'ALTO', 'MUY_ALTO'))
);

CREATE INDEX idx_riesgos_evaluacion ON riesgos(evaluacion_id);
CREATE INDEX idx_riesgos_activo ON riesgos(activo_id);
CREATE INDEX idx_riesgos_amenaza ON riesgos(amenaza_id);
CREATE INDEX idx_riesgos_nivel_efectivo ON riesgos(nivel_riesgo_efectivo);
CREATE INDEX idx_riesgos_propietario ON riesgos(propietario_riesgo_id);
```

#### 3.2.13 `tratamientos_riesgo`
```sql
CREATE TABLE tratamientos_riesgo (
    id SERIAL PRIMARY KEY,
    riesgo_id INTEGER REFERENCES riesgos(id) ON DELETE CASCADE,

    -- Decisión de tratamiento
    opcion_tratamiento VARCHAR(20) NOT NULL, -- ASUMIR, REDUCIR, TRANSFERIR, ELIMINAR
    justificacion TEXT NOT NULL,

    -- Controles a implementar (solo para REDUCIR)
    controles_adicionales INTEGER[], -- Array de IDs de controles_iso27002

    -- Detalles de transferencia
    tercero_receptor VARCHAR(200), -- Para TRANSFERIR
    poliza_seguro VARCHAR(100),
    coste_estimado DECIMAL(10,2),

    -- Plan de acción
    descripcion_accion TEXT,
    fecha_inicio_planificada DATE,
    fecha_fin_planificada DATE,

    -- Responsables
    responsable_implementacion_id INTEGER REFERENCES users(id),

    -- Estado
    estado VARCHAR(20) DEFAULT 'planificado', -- planificado, en_progreso, implementado, verificado
    progreso INTEGER DEFAULT 0 CHECK (progreso BETWEEN 0 AND 100),

    -- Aprobación
    aprobado_por_id INTEGER REFERENCES users(id),
    fecha_aprobacion DATE,

    -- Seguimiento
    fecha_ultima_revision DATE,
    proxima_revision DATE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_opcion CHECK (opcion_tratamiento IN ('ASUMIR', 'REDUCIR', 'TRANSFERIR', 'ELIMINAR')),
    CONSTRAINT valid_estado_trat CHECK (estado IN ('planificado', 'en_progreso', 'implementado', 'verificado', 'cancelado'))
);

CREATE INDEX idx_tratam_riesgo ON tratamientos_riesgo(riesgo_id);
CREATE INDEX idx_tratam_opcion ON tratamientos_riesgo(opcion_tratamiento);
CREATE INDEX idx_tratam_estado ON tratamientos_riesgo(estado);
CREATE INDEX idx_tratam_responsable ON tratamientos_riesgo(responsable_implementacion_id);
```

#### 3.2.14 `declaracion_aplicabilidad` (SOA - Statement of Applicability)
```sql
CREATE TABLE declaracion_aplicabilidad (
    id SERIAL PRIMARY KEY,
    evaluacion_id INTEGER REFERENCES evaluaciones_riesgo(id),
    control_id INTEGER REFERENCES controles_iso27002(id),

    -- Decisión de aplicabilidad
    aplica BOOLEAN NOT NULL,
    justificacion_inclusion TEXT,
    justificacion_exclusion TEXT,

    -- Estado de implementación
    implementado BOOLEAN DEFAULT false,
    nivel_implementacion INTEGER CHECK (nivel_implementacion BETWEEN 0 AND 5),
    salvaguarda_id INTEGER REFERENCES salvaguardas_implantadas(id),

    -- Seguimiento
    fecha_revision DATE,
    revisor_id INTEGER REFERENCES users(id),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(evaluacion_id, control_id)
);

CREATE INDEX idx_soa_evaluacion ON declaracion_aplicabilidad(evaluacion_id);
CREATE INDEX idx_soa_control ON declaracion_aplicabilidad(control_id);
CREATE INDEX idx_soa_aplica ON declaracion_aplicabilidad(aplica);
```

#### 3.2.15 `plan_tratamiento_riesgos`
```sql
CREATE TABLE plan_tratamiento_riesgos (
    id SERIAL PRIMARY KEY,
    evaluacion_id INTEGER REFERENCES evaluaciones_riesgo(id),

    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,

    -- Periodo de ejecución
    fecha_inicio DATE NOT NULL,
    fecha_fin_prevista DATE NOT NULL,
    fecha_fin_real DATE,

    -- Presupuesto
    presupuesto_estimado DECIMAL(12,2),
    presupuesto_ejecutado DECIMAL(12,2),

    -- Estado global
    estado VARCHAR(20) DEFAULT 'borrador', -- borrador, aprobado, en_ejecucion, completado
    progreso_global INTEGER DEFAULT 0,

    -- Aprobación
    aprobado_por_id INTEGER REFERENCES users(id),
    fecha_aprobacion DATE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_estado_plan CHECK (estado IN ('borrador', 'aprobado', 'en_ejecucion', 'completado', 'cancelado'))
);

CREATE INDEX idx_plan_evaluacion ON plan_tratamiento_riesgos(evaluacion_id);
CREATE INDEX idx_plan_estado ON plan_tratamiento_riesgos(estado);
```

#### 3.2.16 `historial_riesgos`
```sql
CREATE TABLE historial_riesgos (
    id SERIAL PRIMARY KEY,
    riesgo_id INTEGER REFERENCES riesgos(id) ON DELETE CASCADE,

    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_id INTEGER REFERENCES users(id),

    -- Snapshot de valores
    nivel_riesgo_efectivo_anterior DECIMAL(10,2),
    nivel_riesgo_efectivo_nuevo DECIMAL(10,2),

    clasificacion_anterior VARCHAR(20),
    clasificacion_nueva VARCHAR(20),

    -- Cambio realizado
    tipo_cambio VARCHAR(50), -- EVALUACION_INICIAL, IMPLEMENTACION_CONTROL, REEVALUACION, etc.
    descripcion_cambio TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_hist_riesgo ON historial_riesgos(riesgo_id);
CREATE INDEX idx_hist_fecha ON historial_riesgos(fecha_registro);
```

---

## 4. FLUJOS DE TRABAJO

### 4.1 Flujo de Apreciación de Riesgos

```
┌─────────────────────────┐
│  1. CREAR EVALUACIÓN    │
│  - Definir alcance      │
│  - Establecer criterios │
│  - Asignar responsable  │
└───────────┬─────────────┘
            │
            v
┌─────────────────────────┐
│  2. IDENTIFICAR ACTIVOS │
│  - Procesos críticos    │
│  - Activos información  │
│  - Recursos TI          │
│  - Valorar C-I-D        │
└───────────┬─────────────┘
            │
            v
┌─────────────────────────┐
│  3. IDENTIFICAR         │
│     AMENAZAS            │
│  - Por tipo recurso     │
│  - Aplicabilidad C-I-D  │
│  - Frecuencia ocurrencia│
└───────────┬─────────────┘
            │
            v
┌─────────────────────────┐
│  4. EVALUAR CONTROLES   │
│     EXISTENTES          │
│  - Identificar controles│
│  - Valorar madurez CMM  │
│  - Preventivos/Reactivos│
└───────────┬─────────────┘
            │
            v
┌─────────────────────────┐
│  5. CALCULAR RIESGOS    │
│  - Riesgo Intrínseco    │
│  - Riesgo Efectivo      │
│  - Clasificar niveles   │
└───────────┬─────────────┘
            │
            v
┌─────────────────────────┐
│  6. PRIORIZAR RIESGOS   │
│  - Comparar c/criterios │
│  - Ordenar por nivel    │
│  - Identificar críticos │
└───────────┬─────────────┘
            │
            v
┌─────────────────────────┐
│  7. GENERAR INFORMES    │
│  - Mapa de riesgos      │
│  - Top riesgos          │
│  - Por activo/proceso   │
└─────────────────────────┘
```

### 4.2 Flujo de Tratamiento de Riesgos

```
┌─────────────────────────┐
│  1. ANALIZAR RIESGOS    │
│     IDENTIFICADOS       │
│  - Revisar evaluación   │
│  - Filtrar por umbral   │
└───────────┬─────────────┘
            │
            v
┌─────────────────────────┐
│  2. DECIDIR OPCIÓN DE   │
│     TRATAMIENTO         │
│  ┌───────────────────┐  │
│  │ A) ASUMIR         │  │
│  │ B) REDUCIR        │  │
│  │ C) TRANSFERIR     │  │
│  │ D) ELIMINAR       │  │
│  └───────────────────┘  │
└───────────┬─────────────┘
            │
            ├─────────────────────┐
            │                     │
     (B) REDUCIR              OTRAS
            │                     │
            v                     v
┌─────────────────────────┐    ┌──────────────┐
│  3. SELECCIONAR         │    │ 6. DOCUMENTAR│
│     CONTROLES           │    │    DECISIÓN  │
│  - Catálogo ISO 27002   │    │ - Justificar │
│  - Controles adicionales│    │ - Aprobar    │
│  - Estimar coste        │    └──────────────┘
└───────────┬─────────────┘
            │
            v
┌─────────────────────────┐
│  4. COMPARAR CON        │
│     ANEXO A             │
│  - Verificar cobertura  │
│  - Justificar exclusión │
│  - Generar SOA          │
└───────────┬─────────────┘
            │
            v
┌─────────────────────────┐
│  5. ELABORAR PLAN DE    │
│     TRATAMIENTO         │
│  - Priorizar acciones   │
│  - Asignar responsables │
│  - Establecer plazos    │
│  - Presupuestar         │
└───────────┬─────────────┘
            │
            v
┌─────────────────────────┐
│  6. APROBAR PLAN        │
│  - Propietario riesgo   │
│  - Dirección            │
│  - Aceptar residual     │
└───────────┬─────────────┘
            │
            v
┌─────────────────────────┐
│  7. EJECUTAR Y          │
│     MONITORIZAR         │
│  - Seguimiento acciones │
│  - Actualizar progreso  │
│  - Recalcular riesgo    │
└─────────────────────────┘
```

### 4.3 Flujo de Recálculo Automático de Riesgos

```python
def calcular_riesgo(activo, recurso, amenaza, dimension):
    """
    Calcula el nivel de riesgo para una combinación específica
    """
    # 1. IMPORTANCIA DEL ACTIVO
    ip = getattr(activo, f'{dimension.lower()}')  # 0-5
    it = recurso.importancia_tipologica  # 1-5
    importancia = ip * it

    # Módulo normalizador de importancia
    modulo_v_impacto = math.sqrt((ip**2 + it**2) / 50)

    # 2. GRAVEDAD DE VULNERABILIDAD (controles reactivos)
    controles_reactivos = obtener_controles_reactivos(amenaza)
    if controles_reactivos:
        sum_madurez_reactiva = sum([
            c.salvaguarda.nivel_madurez
            for c in controles_reactivos
            if c.salvaguarda
        ])
        n_reactivos = len(controles_reactivos)
        gravedad = 5 - (sum_madurez_reactiva / n_reactivos)
    else:
        gravedad = 5

    # 3. IMPACTO
    impacto = importancia * gravedad * modulo_v_impacto

    # 4. FRECUENCIA DE LA AMENAZA
    frecuencia = obtener_frecuencia_amenaza(amenaza, recurso.tipo_recurso, dimension)

    # 5. FACILIDAD DE EXPLOTACIÓN (controles preventivos)
    controles_preventivos = obtener_controles_preventivos(amenaza)
    if controles_preventivos:
        sum_madurez_preventiva = sum([
            c.salvaguarda.nivel_madurez
            for c in controles_preventivos
            if c.salvaguarda
        ])
        n_preventivos = len(controles_preventivos)
        facilidad = 5 - (sum_madurez_preventiva / n_preventivos)
    else:
        facilidad = 5

    # Módulo normalizador de probabilidad
    modulo_v_prob = math.sqrt((frecuencia**2 + facilidad**2) / 50)

    # 6. PROBABILIDAD
    probabilidad = frecuencia * facilidad * modulo_v_prob

    # 7. RIESGO = IMPACTO × PROBABILIDAD
    riesgo = impacto * probabilidad

    # 8. CLASIFICACIÓN CUALITATIVA
    clasificacion = clasificar_riesgo(probabilidad, impacto)

    return {
        'impacto': round(impacto, 2),
        'probabilidad': round(probabilidad, 2),
        'nivel_riesgo': round(riesgo, 2),
        'clasificacion': clasificacion,
        'gravedad_vulnerabilidad': round(gravedad, 2),
        'facilidad_explotacion': round(facilidad, 2),
        'num_controles_reactivos': len(controles_reactivos),
        'num_controles_preventivos': len(controles_preventivos)
    }

def clasificar_riesgo(probabilidad, impacto):
    """
    Clasifica el riesgo según la matriz
    """
    # Definir rangos
    if probabilidad >= 13:
        nivel_prob = 'ALTO'
    elif probabilidad >= 6:
        nivel_prob = 'MEDIO'
    else:
        nivel_prob = 'BAJO'

    if impacto >= 13:
        nivel_imp = 'ALTO'
    elif impacto >= 6:
        nivel_imp = 'MEDIO'
    else:
        nivel_imp = 'BAJO'

    # Matriz de riesgo
    matriz = {
        ('ALTO', 'ALTO'): 'MUY_ALTO',
        ('ALTO', 'MEDIO'): 'ALTO',
        ('ALTO', 'BAJO'): 'MEDIO',
        ('MEDIO', 'ALTO'): 'ALTO',
        ('MEDIO', 'MEDIO'): 'MEDIO',
        ('MEDIO', 'BAJO'): 'BAJO',
        ('BAJO', 'ALTO'): 'MEDIO',
        ('BAJO', 'MEDIO'): 'BAJO',
        ('BAJO', 'BAJO'): 'MUY_BAJO'
    }

    return matriz.get((nivel_prob, nivel_imp), 'MEDIO')
```

---

## 5. FUNCIONALIDADES DEL MÓDULO

### 5.1 Gestión de Inventario de Activos

#### Características:
- Registro de procesos de negocio y su criticidad
- Catálogo de activos de información con valoración C-I-D
- Registro de recursos de información (HW, SW, personas, ubicaciones)
- Relación entre activos, procesos y recursos
- Matriz RACI para responsabilidades
- Importación/exportación desde Excel
- Versionado de inventario

#### Pantallas:
1. **Listado de Activos**: Filtros por tipo, propietario, criticidad
2. **Ficha de Activo**: Formulario de valoración C-I-D con justificación
3. **Mapa de Relaciones**: Visualización de activo→recursos→procesos
4. **Importación Masiva**: Carga desde plantilla Excel

### 5.2 Catálogo de Amenazas y Controles

#### Características:
- Catálogo completo MAGERIT 3.2 (precar gado)
- Catálogo ISO 27002:2022 (93 controles)
- Relación amenazas→controles aplicables
- Frecuencias de amenazas por tipo de recurso
- Clasificación preventivo/reactivo de controles
- Mapeo con TISAX, ISO 27001:2013

#### Pantallas:
1. **Catálogo de Amenazas**: Navegación por grupos
2. **Catálogo de Controles**: Filtros por categoría
3. **Matriz de Aplicabilidad**: Amenazas vs Controles

### 5.3 Evaluación de Riesgos

#### Características:
- Creación de evaluaciones con alcance definido
- Cálculo automático de riesgos (intrínseco, efectivo, residual)
- Valoración de madurez de controles (CMM 0-5)
- Identificación de propietarios de riesgos
- Generación automática de todos los riesgos posibles
- Recálculo en tiempo real al modificar controles

#### Pantallas:
1. **Dashboard de Evaluación**: KPIs principales, gráficos
2. **Matriz de Riesgos**: Visualización impacto vs probabilidad
3. **Listado de Riesgos**: Ordenable, filtrable, exportable
4. **Ficha de Riesgo**: Detalle completo con fórmulas
5. **Mapa de Calor**: Visualización por proceso/activo/amenaza

### 5.4 Tratamiento de Riesgos

#### Características:
- Decisión de tratamiento (4 opciones)
- Selección de controles adicionales
- Generación de Declaración de Aplicabilidad (SOA)
- Plan de tratamiento con plazos y presupuestos
- Seguimiento de acciones con indicador de progreso
- Recálculo de riesgo residual

#### Pantallas:
1. **Listado de Riesgos para Tratamiento**: Filtro por umbral
2. **Asistente de Tratamiento**: Wizard paso a paso
3. **Plan de Tratamiento**: Gantt chart, asignaciones
4. **SOA (Declaración de Aplicabilidad)**: Tabla de controles
5. **Seguimiento de Acciones**: Dashboard de implementación

### 5.5 Informes y Reporting

#### Tipos de Informes:
1. **Informe Ejecutivo de Riesgos**
   - Resumen por niveles de riesgo
   - Top 10 riesgos más críticos
   - Estado del tratamiento
   - Evolución temporal

2. **Informe de Apreciación de Riesgos**
   - Metodología aplicada
   - Inventario de activos
   - Catálogo de amenazas
   - Riesgos identificados con cálculos
   - Matriz de riesgos

3. **Declaración de Aplicabilidad (SOA)**
   - Listado de 93 controles ISO 27002:2022
   - Justificación de inclusión/exclusión
   - Estado de implementación

4. **Plan de Tratamiento de Riesgos**
   - Acciones planificadas
   - Responsables y plazos
   - Presupuesto
   - Cronograma

5. **Informe de Seguimiento**
   - Progreso de tratamientos
   - Riesgos cerrados vs abiertos
   - Indicadores de cumplimiento

#### Formatos de Export:
- PDF (informes formales)
- Excel (datos tabulares)
- CSV (integración con otras herramientas)
- JSON (API)

### 5.6 Dashboard y Analítica

#### KPIs Principales:
- **Nivel de Riesgo Global**: Suma ponderada de todos los riesgos
- **Distribución de Riesgos**: Por clasificación (Muy Alto, Alto, Medio, Bajo)
- **Riesgos por Umbral**: % riesgos sobre/bajo objetivo
- **Cobertura de Controles**: % controles implementados
- **Madurez Media**: Nivel CMM promedio
- **Eficacia del Tratamiento**: Reducción de riesgo lograda

#### Gráficos:
1. Mapa de calor (Probabilidad vs Impacto)
2. Distribución por tipo de amenaza
3. Riesgos por proceso de negocio
4. Evolución temporal del riesgo
5. Progreso de plan de tratamiento
6. Controles más efectivos

---

## 6. ARQUITECTURA TÉCNICA

### 6.1 Backend (Flask)

#### Estructura de Blueprints:
```
app/
├── risks/
│   ├── __init__.py
│   ├── routes.py              # Rutas principales
│   ├── models.py              # Modelos SQLAlchemy
│   ├── forms.py               # Formularios WTForms
│   ├── calculations.py        # Motor de cálculo de riesgos
│   ├── services/
│   │   ├── asset_service.py
│   │   ├── threat_service.py
│   │   ├── risk_service.py
│   │   └── treatment_service.py
│   ├── utils/
│   │   ├── excel_importer.py
│   │   ├── report_generator.py
│   │   └── validators.py
│   └── templates/
│       └── risks/
│           ├── dashboard.html
│           ├── assets/
│           ├── evaluations/
│           ├── treatments/
│           └── reports/
```

#### Servicios Principales:

```python
# app/risks/services/risk_service.py
class RiskCalculationService:
    """Servicio para cálculo de riesgos"""

    @staticmethod
    def calculate_intrinsic_risk(asset, resource, threat, dimension):
        """Calcula riesgo intrínseco (sin controles)"""
        pass

    @staticmethod
    def calculate_effective_risk(asset, resource, threat, dimension):
        """Calcula riesgo efectivo (con controles actuales)"""
        pass

    @staticmethod
    def calculate_residual_risk(asset, resource, threat, dimension, planned_controls):
        """Calcula riesgo residual (con controles planificados)"""
        pass

    @staticmethod
    def recalculate_all_risks(evaluation_id):
        """Recalcula todos los riesgos de una evaluación"""
        pass
```

```python
# app/risks/services/treatment_service.py
class TreatmentService:
    """Servicio para gestión de tratamientos"""

    @staticmethod
    def suggest_controls(risk_id):
        """Sugiere controles para un riesgo"""
        pass

    @staticmethod
    def generate_soa(evaluation_id):
        """Genera Declaración de Aplicabilidad"""
        pass

    @staticmethod
    def create_treatment_plan(evaluation_id, treatments):
        """Crea plan de tratamiento"""
        pass
```

### 6.2 Frontend

#### Tecnologías:
- **Base**: Flask templates (Jinja2)
- **CSS**: Bootstrap 5 + AdminLTE 3
- **JS**: jQuery, DataTables, Chart.js, Select2
- **Gráficos**: Chart.js, D3.js (para matriz de riesgos)

#### Componentes Reutilizables:
1. **Risk Matrix Component**: Visualización impacto vs probabilidad
2. **Risk Level Badge**: Etiqueta coloreada según nivel
3. **Control Maturity Slider**: Selector de madurez CMM
4. **SOA Table**: Tabla interactiva de controles
5. **Treatment Wizard**: Asistente paso a paso

### 6.3 Motor de Cálculo

#### Optimizaciones:
- Cálculos en batch para evaluaciones completas
- Caché de resultados intermedios
- Triggers de base de datos para recálculo automático
- Jobs asíncronos (Celery) para evaluaciones grandes

#### Triggers SQL:
```sql
-- Recalcular riesgo cuando cambia madurez de control
CREATE TRIGGER trg_recalc_risk_on_control_change
AFTER UPDATE ON salvaguardas_implantadas
FOR EACH ROW
WHEN (OLD.nivel_madurez <> NEW.nivel_madurez)
EXECUTE FUNCTION fn_recalculate_affected_risks();
```

---

## 7. PLAN DE IMPLEMENTACIÓN

### Fase 1: Fundamentos (Sprint 1-2) - 4 semanas
- [ ] Crear modelos de base de datos
- [ ] Migración inicial con Alembic
- [ ] Precarga de catálogos (amenazas MAGERIT, controles ISO 27002)
- [ ] CRUD básico de activos
- [ ] CRUD básico de recursos
- [ ] Relaciones activos-recursos

### Fase 2: Motor de Cálculo (Sprint 3-4) - 4 semanas
- [ ] Implementar fórmulas de cálculo de riesgo
- [ ] Servicio de cálculo de riesgo intrínseco
- [ ] Servicio de cálculo de riesgo efectivo
- [ ] Tests unitarios de fórmulas
- [ ] Validación con datos de ejemplo del Excel de referencia
- [ ] Optimización de consultas SQL

### Fase 3: Evaluación de Riesgos (Sprint 5-6) - 4 semanas
- [ ] CRUD de evaluaciones de riesgos
- [ ] Generación automática de riesgos
- [ ] Interfaz de valoración C-I-D de activos
- [ ] Interfaz de valoración de madurez de controles
- [ ] Dashboard de evaluación
- [ ] Matriz de riesgos interactiva
- [ ] Listado de riesgos con filtros

### Fase 4: Tratamiento de Riesgos (Sprint 7-8) - 4 semanas
- [ ] CRUD de tratamientos
- [ ] Asistente de selección de opción de tratamiento
- [ ] Selección de controles adicionales
- [ ] Generación de SOA
- [ ] Plan de tratamiento con Gantt
- [ ] Seguimiento de acciones
- [ ] Recálculo de riesgo residual

### Fase 5: Reporting (Sprint 9) - 2 semanas
- [ ] Generación de PDF con WeasyPrint/ReportLab
- [ ] Informe de Apreciación de Riesgos
- [ ] Informe de SOA
- [ ] Informe de Plan de Tratamiento
- [ ] Exportación a Excel
- [ ] Dashboard ejecutivo

### Fase 6: Integraciones (Sprint 10) - 2 semanas
- [ ] Importación desde Excel (plantilla de referencia)
- [ ] Integración con módulo de Auditorías
- [ ] Integración con módulo de No Conformidades
- [ ] Integración con módulo de Documentos
- [ ] API REST para consultas externas

### Fase 7: Testing y Refinamiento (Sprint 11-12) - 4 semanas
- [ ] Tests de integración
- [ ] Tests de carga (evaluaciones grandes)
- [ ] Validación con usuarios piloto
- [ ] Corrección de bugs
- [ ] Optimización de rendimiento
- [ ] Documentación de usuario

---

## 8. CRITERIOS DE ACEPTACIÓN

### 8.1 Funcionales

✅ **El sistema debe permitir**:
1. Registrar al menos 100 activos de información
2. Calcular automáticamente todos los riesgos posibles (activo × recurso × amenaza × dimensión)
3. Recalcular riesgos en < 5 segundos al cambiar madurez de un control
4. Generar matriz de riesgos visual actualizada en tiempo real
5. Exportar SOA completa con 93 controles ISO 27002:2022
6. Crear plan de tratamiento con al menos 50 acciones
7. Importar inventario desde Excel en < 1 minuto
8. Generar informe PDF ejecutivo en < 10 segundos

### 8.2 Calidad de Datos

✅ **Las fórmulas deben**:
1. Coincidir con los resultados del Excel de referencia (margen ±0.01)
2. Respetar rangos válidos (0-25 para riesgo)
3. Clasificar correctamente según matriz (5 niveles)
4. Propagar cambios a riesgos afectados automáticamente

### 8.3 Cumplimiento Normativo

✅ **El sistema debe**:
1. Cubrir todos los requisitos de ISO 27001:2023 apartados 6.1.2 y 6.1.3
2. Incluir los 93 controles de ISO 27002:2022
3. Generar evidencias documentales auditables
4. Mantener trazabilidad completa de cambios
5. Permitir aprobación formal de propietarios de riesgos

### 8.4 Usabilidad

✅ **La interfaz debe**:
1. Ser intuitiva para usuarios no técnicos
2. Mostrar ayuda contextual en formularios críticos
3. Validar datos en cliente antes de enviar
4. Proporcionar feedback visual de progreso
5. Ser responsiva (móvil, tablet, desktop)

---

## 9. INDICADORES DE ÉXITO (KPIs)

### 9.1 Métricas de Uso
- **Tasa de Adopción**: % usuarios objetivo que usan el módulo semanalmente
- **Completitud de Inventario**: % activos críticos registrados
- **Frecuencia de Evaluación**: Evaluaciones realizadas por trimestre
- **Tiempo de Evaluación**: Días promedio para completar una evaluación

### 9.2 Métricas de Calidad
- **Cobertura de Controles**: % controles ISO 27002 evaluados
- **Madurez Promedio**: Nivel CMM medio de la organización
- **Riesgos sobre Umbral**: % riesgos que superan nivel objetivo
- **Efectividad de Tratamiento**: % reducción de riesgo tras implementación

### 9.3 Métricas de Eficiencia
- **Tiempo de Cálculo**: ms por riesgo calculado
- **Tiempo de Generación de Informes**: segundos por informe
- **Tasa de Errores**: Errores de cálculo por 1000 riesgos
- **Disponibilidad del Sistema**: % uptime

---

## 10. RIESGOS DEL PROYECTO

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Complejidad de fórmulas de cálculo | Media | Alto | Validación exhaustiva con Excel de referencia, tests unitarios |
| Rendimiento con grandes volúmenes | Media | Medio | Optimización SQL, caché, jobs asíncronos |
| Resistencia al cambio de usuarios | Alta | Medio | Capacitación, interfaz intuitiva, importación de datos existentes |
| Integración con módulos existentes | Baja | Alto | Diseño modular, APIs bien definidas |
| Cambios normativos ISO 27001 | Baja | Medio | Diseño flexible, versionado de evaluaciones |

---

## 11. RECURSOS NECESARIOS

### 11.1 Humanos
- 1 Desarrollador Backend (Python/Flask)
- 1 Desarrollador Frontend (JS/HTML/CSS)
- 1 Consultor SGSI (validación normativa)
- 1 QA Tester

### 11.2 Tecnológicos
- Servidor de desarrollo/staging
- Base de datos PostgreSQL 14+
- Herramientas de generación PDF (WeasyPrint/ReportLab)
- Librería de gráficos (Chart.js, D3.js)

### 11.3 Conocimiento
- Normativa ISO 27001:2023, ISO 27005:2022
- Metodología MAGERIT 3.2
- Estadística y cálculo de riesgos
- Diseño de bases de datos relacionales

---

## 12. CONCLUSIONES

El módulo de Gestión de Riesgos representa el núcleo fundamental del SGSI, proporcionando:

1. **Cumplimiento Normativo**: Cobertura completa de ISO 27001:2023 apartados 6.1.2 y 6.1.3
2. **Rigor Metodológico**: Implementación de fórmulas validadas basadas en MAGERIT 3.2
3. **Automatización**: Cálculo automático de miles de riesgos en segundos
4. **Trazabilidad**: Historial completo de evaluaciones y tratamientos
5. **Toma de Decisiones**: Información visual y ejecutiva para la dirección

La implementación escalonada en 12 sprints (24 semanas) permitirá entregar valor incremental, validando cada fase antes de avanzar a la siguiente.

El éxito del proyecto se medirá por la adopción por parte de usuarios, la calidad de las evaluaciones de riesgo, y la reducción efectiva del nivel de riesgo organizacional mediante tratamientos basados en evidencia.

---

## ANEXOS

### Anexo A: Diccionario de Datos Completo
Ver sección 3.2 - Tablas Principales

### Anexo B: Casos de Uso Detallados
*(A desarrollar en fase de diseño detallado)*

### Anexo C: Mockups de Interfaz
*(A desarrollar con equipo de UX)*

### Anexo D: Plan de Capacitación
*(A desarrollar en fase de despliegue)*

### Anexo E: Manual de Usuario
*(A desarrollar en fase final)*

---

**Fin del Documento**

**Control de Versiones:**
| Versión | Fecha | Autor | Cambios |
|---------|-------|-------|---------|
| 1.0 | 2025-10-23 | Claude Code | Versión inicial |
