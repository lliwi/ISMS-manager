-- Migración 016: Matriz de Controles-Amenazas basada en MAGERIT 3.2 e ISO 27002:2022
--
-- Este script establece las relaciones estándar entre amenazas MAGERIT y controles
-- ISO 27002:2022, incluyendo tipo de control (preventivo/reactivo) y efectividad.
--
-- IMPORTANTE: Este es un catálogo de referencia que debe ajustarse según el contexto
-- específico de cada organización.

-- ====================================================================
-- AMENAZAS DE TIPO [N.*] - DESASTRES NATURALES
-- ====================================================================

INSERT INTO controles_amenazas (control_codigo, amenaza_id, tipo_control, efectividad)
SELECT control, a.id, tipo, efectividad
FROM (VALUES
    -- N.1 - Fuego
    ('A.7.4', 'N.1', 'PREVENTIVO', 0.70),   -- Seguridad física y monitorización
    ('A.7.13', 'N.1', 'PREVENTIVO', 0.80),  -- Mantenimiento del equipo (detección incendios)
    ('A.5.29', 'N.1', 'REACTIVO', 0.85),    -- Seguridad durante interrupciones
    ('A.5.30', 'N.1', 'REACTIVO', 0.90),    -- Preparación TIC para continuidad
    ('A.8.14', 'N.1', 'REACTIVO', 0.75),    -- Redundancia de instalaciones

    -- N.2 - Daños por agua
    ('A.7.4', 'N.2', 'PREVENTIVO', 0.65),
    ('A.7.13', 'N.2', 'PREVENTIVO', 0.70),
    ('A.5.29', 'N.2', 'REACTIVO', 0.80),
    ('A.5.30', 'N.2', 'REACTIVO', 0.90),
    ('A.8.14', 'N.2', 'REACTIVO', 0.75)
) AS v(control, amenaza_codigo, tipo, efectividad)
JOIN amenazas a ON a.codigo = v.amenaza_codigo
ON CONFLICT (control_codigo, amenaza_id) DO NOTHING;

-- ====================================================================
-- AMENAZAS DE TIPO [I.*] - DESASTRES INDUSTRIALES
-- ====================================================================

INSERT INTO controles_amenazas (control_codigo, amenaza_id, tipo_control, efectividad)
SELECT control, a.id, tipo, efectividad
FROM (VALUES
    -- I.1 - Fuego
    ('A.7.4', 'I.1', 'PREVENTIVO', 0.75),
    ('A.7.13', 'I.1', 'PREVENTIVO', 0.85),
    ('A.5.29', 'I.1', 'REACTIVO', 0.85),
    ('A.5.30', 'I.1', 'REACTIVO', 0.90),
    ('A.8.14', 'I.1', 'REACTIVO', 0.80),

    -- I.2 - Daños por agua
    ('A.7.4', 'I.2', 'PREVENTIVO', 0.70),
    ('A.7.13', 'I.2', 'PREVENTIVO', 0.75),
    ('A.5.29', 'I.2', 'REACTIVO', 0.80),
    ('A.5.30', 'I.2', 'REACTIVO', 0.90),

    -- I.5 - Avería de origen físico o lógico
    ('A.7.13', 'I.5', 'PREVENTIVO', 0.70),
    ('A.8.6', 'I.5', 'PREVENTIVO', 0.60),   -- Gestión de capacidad
    ('A.5.30', 'I.5', 'REACTIVO', 0.85),
    ('A.8.14', 'I.5', 'REACTIVO', 0.90),
    ('A.8.13', 'I.5', 'REACTIVO', 0.75),    -- Respaldo de información

    -- I.6 - Corte del suministro eléctrico
    ('A.7.13', 'I.6', 'PREVENTIVO', 0.60),
    ('A.8.1', 'I.6', 'PREVENTIVO', 0.50),
    ('A.5.29', 'I.6', 'REACTIVO', 0.85),
    ('A.5.30', 'I.6', 'REACTIVO', 0.90),
    ('A.8.14', 'I.6', 'REACTIVO', 0.70),

    -- I.7 - Condiciones inadecuadas de temperatura o humedad
    ('A.7.4', 'I.7', 'PREVENTIVO', 0.80),
    ('A.7.13', 'I.7', 'PREVENTIVO', 0.75),
    ('A.8.14', 'I.7', 'REACTIVO', 0.60),

    -- I.8 - Fallo de servicios de comunicaciones
    ('A.8.20', 'I.8', 'PREVENTIVO', 0.70),  -- Seguridad de redes
    ('A.8.22', 'I.8', 'PREVENTIVO', 0.65),  -- Segregación de redes
    ('A.5.30', 'I.8', 'REACTIVO', 0.85),
    ('A.8.14', 'I.8', 'REACTIVO', 0.80),

    -- I.9 - Interrupción de otros servicios
    ('A.5.20', 'I.9', 'PREVENTIVO', 0.60),  -- Seguridad de redes en servicios
    ('A.5.30', 'I.9', 'REACTIVO', 0.80),
    ('A.8.14', 'I.9', 'REACTIVO', 0.75),

    -- I.10 - Degradación de los soportes de almacenamiento
    ('A.7.13', 'I.10', 'PREVENTIVO', 0.70),
    ('A.8.11', 'I.10', 'PREVENTIVO', 0.75), -- Eliminación de datos
    ('A.8.13', 'I.10', 'REACTIVO', 0.95),   -- Respaldo de información

    -- I.11 - Emanaciones electromagnéticas
    ('A.7.4', 'I.11', 'PREVENTIVO', 0.65),
    ('A.7.7', 'I.11', 'PREVENTIVO', 0.70),  -- Trabajo en áreas seguras

    -- I.12 - Interrupción de servicios administrativos
    ('A.5.30', 'I.12', 'REACTIVO', 0.80),
    ('A.5.7', 'I.12', 'REACTIVO', 0.70)     -- Inteligencia de amenazas
) AS v(control, amenaza_codigo, tipo, efectividad)
JOIN amenazas a ON a.codigo = v.amenaza_codigo
ON CONFLICT (control_codigo, amenaza_id) DO NOTHING;

-- ====================================================================
-- AMENAZAS DE TIPO [E.*] - ERRORES Y FALLOS NO INTENCIONADOS
-- ====================================================================

INSERT INTO controles_amenazas (control_codigo, amenaza_id, tipo_control, efectividad)
SELECT control, a.id, tipo, efectividad
FROM (VALUES
    -- E.1 - Errores de los usuarios
    ('A.5.1', 'E.1', 'PREVENTIVO', 0.70),   -- Políticas de seguridad
    ('A.6.3', 'E.1', 'PREVENTIVO', 0.85),   -- Concienciación en seguridad
    ('A.5.15', 'E.1', 'PREVENTIVO', 0.60),  -- Control de accesos
    ('A.8.18', 'E.1', 'PREVENTIVO', 0.55),  -- Uso de programas utilitarios privilegiados
    ('A.5.30', 'E.1', 'REACTIVO', 0.60),
    ('A.8.13', 'E.1', 'REACTIVO', 0.75),

    -- E.2 - Errores del administrador
    ('A.5.1', 'E.2', 'PREVENTIVO', 0.75),
    ('A.6.3', 'E.2', 'PREVENTIVO', 0.80),
    ('A.8.18', 'E.2', 'PREVENTIVO', 0.70),
    ('A.8.32', 'E.2', 'PREVENTIVO', 0.65),  -- Gestión de cambios
    ('A.5.30', 'E.2', 'REACTIVO', 0.65),
    ('A.8.13', 'E.2', 'REACTIVO', 0.80),

    -- E.3 - Errores de monitorización
    ('A.8.15', 'E.3', 'PREVENTIVO', 0.80),  -- Registro de actividades
    ('A.8.16', 'E.3', 'PREVENTIVO', 0.85),  -- Monitorización de actividades
    ('A.6.8', 'E.3', 'DETECTIVE', 0.75),    -- Reporte de eventos

    -- E.4 - Errores de configuración
    ('A.8.9', 'E.4', 'PREVENTIVO', 0.80),   -- Gestión de configuración
    ('A.8.32', 'E.4', 'PREVENTIVO', 0.75),  -- Gestión de cambios
    ('A.8.34', 'E.4', 'PREVENTIVO', 0.70),  -- Pruebas de seguridad
    ('A.5.37', 'E.4', 'DETECTIVE', 0.65),   -- Procedimientos operacionales documentados

    -- E.7 - Deficiencias en la organización
    ('A.5.1', 'E.7', 'PREVENTIVO', 0.75),
    ('A.5.2', 'E.7', 'PREVENTIVO', 0.70),   -- Roles y responsabilidades
    ('A.5.3', 'E.7', 'PREVENTIVO', 0.65),   -- Segregación de tareas

    -- E.8 - Difusión de software dañino
    ('A.8.7', 'E.8', 'PREVENTIVO', 0.85),   -- Protección contra malware
    ('A.6.3', 'E.8', 'PREVENTIVO', 0.70),
    ('A.8.23', 'E.8', 'PREVENTIVO', 0.75),  -- Filtrado web
    ('A.5.19', 'E.8', 'DETECTIVE', 0.65),   -- Seguridad de la información en proveedores

    -- E.9 - Errores de [re]encaminamiento
    ('A.8.20', 'E.9', 'PREVENTIVO', 0.70),
    ('A.8.21', 'E.9', 'PREVENTIVO', 0.75),  -- Seguridad de servicios de red
    ('A.8.22', 'E.9', 'PREVENTIVO', 0.80),  -- Segregación de redes

    -- E.10 - Errores de secuencia
    ('A.8.32', 'E.10', 'PREVENTIVO', 0.70),
    ('A.8.34', 'E.10', 'PREVENTIVO', 0.75),

    -- E.15 - Alteración accidental de la información
    ('A.8.24', 'E.15', 'PREVENTIVO', 0.75), -- Uso de criptografía
    ('A.5.34', 'E.15', 'DETECTIVE', 0.70),  -- Privacidad y protección de datos
    ('A.8.13', 'E.15', 'REACTIVO', 0.85),

    -- E.18 - Destrucción de información
    ('A.8.11', 'E.18', 'PREVENTIVO', 0.65),
    ('A.8.13', 'E.18', 'REACTIVO', 0.90),
    ('A.5.30', 'E.18', 'REACTIVO', 0.80),

    -- E.19 - Fugas de información
    ('A.5.10', 'E.19', 'PREVENTIVO', 0.70), -- Uso aceptable de la información
    ('A.5.12', 'E.19', 'PREVENTIVO', 0.75), -- Clasificación de la información
    ('A.5.34', 'E.19', 'PREVENTIVO', 0.80),
    ('A.6.3', 'E.19', 'PREVENTIVO', 0.65),

    -- E.20 - Vulnerabilidades de los programas
    ('A.8.8', 'E.20', 'PREVENTIVO', 0.85),  -- Gestión de vulnerabilidades técnicas
    ('A.8.25', 'E.20', 'PREVENTIVO', 0.80), -- Ciclo de vida de desarrollo seguro
    ('A.8.31', 'E.20', 'PREVENTIVO', 0.75), -- Separación de entornos de desarrollo

    -- E.21 - Errores de mantenimiento / actualización de programas
    ('A.8.19', 'E.21', 'PREVENTIVO', 0.75), -- Instalación de software en sistemas operativos
    ('A.8.32', 'E.21', 'PREVENTIVO', 0.80),
    ('A.8.34', 'E.21', 'PREVENTIVO', 0.70),

    -- E.23 - Errores de mantenimiento / actualización de equipos
    ('A.7.13', 'E.23', 'PREVENTIVO', 0.75),
    ('A.8.32', 'E.23', 'PREVENTIVO', 0.70),

    -- E.24 - Caída del sistema por agotamiento de recursos
    ('A.8.6', 'E.24', 'PREVENTIVO', 0.80),
    ('A.8.16', 'E.24', 'PREVENTIVO', 0.70),
    ('A.5.30', 'E.24', 'REACTIVO', 0.75),

    -- E.25 - Pérdida de equipos
    ('A.7.8', 'E.25', 'PREVENTIVO', 0.65),  -- Pantallas y escritorios despejados
    ('A.7.9', 'E.25', 'PREVENTIVO', 0.70),  -- Seguridad de activos fuera de las instalaciones
    ('A.8.13', 'E.25', 'REACTIVO', 0.85),
    ('A.5.30', 'E.25', 'REACTIVO', 0.75)
) AS v(control, amenaza_codigo, tipo, efectividad)
JOIN amenazas a ON a.codigo = v.amenaza_codigo
ON CONFLICT (control_codigo, amenaza_id) DO NOTHING;

-- ====================================================================
-- AMENAZAS DE TIPO [A.*] - ATAQUES INTENCIONADOS
-- ====================================================================

INSERT INTO controles_amenazas (control_codigo, amenaza_id, tipo_control, efectividad)
SELECT control, a.id, tipo, efectividad
FROM (VALUES
    -- A.3 - Manipulación de los registros de actividad (log)
    ('A.5.15', 'A.3', 'PREVENTIVO', 0.75),
    ('A.8.15', 'A.3', 'PREVENTIVO', 0.85),
    ('A.8.16', 'A.3', 'DETECTIVE', 0.80),
    ('A.6.8', 'A.3', 'DETECTIVE', 0.70),

    -- A.4 - Manipulación de la configuración
    ('A.5.15', 'A.4', 'PREVENTIVO', 0.80),
    ('A.8.9', 'A.4', 'PREVENTIVO', 0.85),
    ('A.8.32', 'A.4', 'PREVENTIVO', 0.75),
    ('A.6.8', 'A.4', 'DETECTIVE', 0.70),

    -- A.5 - Suplantación de la identidad del usuario
    ('A.5.17', 'A.5', 'PREVENTIVO', 0.85),  -- Información de autenticación
    ('A.5.18', 'A.5', 'PREVENTIVO', 0.80),  -- Derechos de acceso
    ('A.8.5', 'A.5', 'PREVENTIVO', 0.90),   -- Autenticación segura
    ('A.6.8', 'A.5', 'DETECTIVE', 0.70),

    -- A.6 - Abuso de privilegios de acceso
    ('A.5.15', 'A.6', 'PREVENTIVO', 0.85),
    ('A.5.18', 'A.6', 'PREVENTIVO', 0.80),
    ('A.8.2', 'A.6', 'PREVENTIVO', 0.75),   -- Derechos de acceso privilegiados
    ('A.8.16', 'A.6', 'DETECTIVE', 0.80),

    -- A.7 - Uso no previsto
    ('A.5.10', 'A.7', 'PREVENTIVO', 0.70),
    ('A.5.15', 'A.7', 'PREVENTIVO', 0.75),
    ('A.8.16', 'A.7', 'DETECTIVE', 0.75),
    ('A.6.8', 'A.7', 'DETECTIVE', 0.65),

    -- A.8 - Difusión de software dañino (malware)
    ('A.8.7', 'A.8', 'PREVENTIVO', 0.90),
    ('A.8.23', 'A.8', 'PREVENTIVO', 0.80),
    ('A.6.3', 'A.8', 'PREVENTIVO', 0.70),
    ('A.6.8', 'A.8', 'DETECTIVE', 0.75),

    -- A.9 - [Re]encaminamiento de mensajes
    ('A.8.20', 'A.9', 'PREVENTIVO', 0.75),
    ('A.8.21', 'A.9', 'PREVENTIVO', 0.80),
    ('A.8.22', 'A.9', 'PREVENTIVO', 0.85),

    -- A.11 - Acceso no autorizado
    ('A.5.15', 'A.11', 'PREVENTIVO', 0.85),
    ('A.5.16', 'A.11', 'PREVENTIVO', 0.80),  -- Gestión de identidades
    ('A.5.18', 'A.11', 'PREVENTIVO', 0.85),
    ('A.7.2', 'A.11', 'PREVENTIVO', 0.70),   -- Controles de entrada física
    ('A.8.3', 'A.11', 'PREVENTIVO', 0.75),   -- Restricción de acceso a la información

    -- A.15 - Modificación deliberada de la información
    ('A.5.15', 'A.15', 'PREVENTIVO', 0.80),
    ('A.8.24', 'A.15', 'PREVENTIVO', 0.85),
    ('A.8.16', 'A.15', 'DETECTIVE', 0.75),
    ('A.8.13', 'A.15', 'REACTIVO', 0.90),

    -- A.18 - Destrucción de información
    ('A.5.15', 'A.18', 'PREVENTIVO', 0.75),
    ('A.8.11', 'A.18', 'PREVENTIVO', 0.70),
    ('A.8.13', 'A.18', 'REACTIVO', 0.95),

    -- A.19 - Divulgación de información
    ('A.5.12', 'A.19', 'PREVENTIVO', 0.80),
    ('A.5.15', 'A.19', 'PREVENTIVO', 0.85),
    ('A.8.24', 'A.19', 'PREVENTIVO', 0.90),
    ('A.5.34', 'A.19', 'PREVENTIVO', 0.75),

    -- A.22 - Manipulación de programas
    ('A.5.15', 'A.22', 'PREVENTIVO', 0.80),
    ('A.8.25', 'A.22', 'PREVENTIVO', 0.85),
    ('A.8.28', 'A.22', 'PREVENTIVO', 0.75),  -- Codificación segura
    ('A.8.32', 'A.22', 'PREVENTIVO', 0.70),

    -- A.23 - Manipulación de los equipos
    ('A.7.2', 'A.23', 'PREVENTIVO', 0.75),
    ('A.7.4', 'A.23', 'PREVENTIVO', 0.80),
    ('A.7.9', 'A.23', 'PREVENTIVO', 0.70),

    -- A.24 - Denegación de servicio
    ('A.8.6', 'A.24', 'PREVENTIVO', 0.60),
    ('A.8.20', 'A.24', 'PREVENTIVO', 0.75),
    ('A.8.14', 'A.24', 'REACTIVO', 0.70),
    ('A.5.30', 'A.24', 'REACTIVO', 0.80),

    -- A.25 - Robo
    ('A.7.2', 'A.25', 'PREVENTIVO', 0.80),
    ('A.7.8', 'A.25', 'PREVENTIVO', 0.70),
    ('A.7.9', 'A.25', 'PREVENTIVO', 0.75),
    ('A.8.13', 'A.25', 'REACTIVO', 0.85),

    -- A.26 - Ataque destructivo
    ('A.7.2', 'A.26', 'PREVENTIVO', 0.70),
    ('A.7.4', 'A.26', 'PREVENTIVO', 0.75),
    ('A.5.29', 'A.26', 'REACTIVO', 0.80),
    ('A.5.30', 'A.26', 'REACTIVO', 0.85),
    ('A.8.13', 'A.26', 'REACTIVO', 0.90),

    -- A.27 - Ocupación enemiga
    ('A.7.2', 'A.27', 'PREVENTIVO', 0.60),
    ('A.7.4', 'A.27', 'PREVENTIVO', 0.65),
    ('A.5.29', 'A.27', 'REACTIVO', 0.75),

    -- A.28 - Indisponibilidad del personal
    ('A.6.1', 'A.28', 'PREVENTIVO', 0.70),   -- Investigación de antecedentes
    ('A.6.4', 'A.28', 'PREVENTIVO', 0.65),   -- Proceso disciplinario
    ('A.5.30', 'A.28', 'REACTIVO', 0.80),

    -- A.29 - Extorsión
    ('A.5.7', 'A.29', 'PREVENTIVO', 0.60),
    ('A.6.5', 'A.29', 'PREVENTIVO', 0.55),   -- Responsabilidades tras la finalización
    ('A.5.27', 'A.29', 'DETECTIVE', 0.70),   -- Aprendizaje de incidentes

    -- A.30 - Ingeniería social
    ('A.6.3', 'A.30', 'PREVENTIVO', 0.85),
    ('A.5.1', 'A.30', 'PREVENTIVO', 0.70),
    ('A.6.8', 'A.30', 'DETECTIVE', 0.65)
) AS v(control, amenaza_codigo, tipo, efectividad)
JOIN amenazas a ON a.codigo = v.amenaza_codigo
ON CONFLICT (control_codigo, amenaza_id) DO NOTHING;

-- ====================================================================
-- RESUMEN FINAL
-- ====================================================================

SELECT
    'Matriz de Controles-Amenazas MAGERIT' AS matriz,
    COUNT(*) AS total_relaciones,
    COUNT(DISTINCT control_codigo) AS controles_distintos,
    COUNT(DISTINCT amenaza_id) AS amenazas_cubiertas,
    SUM(CASE WHEN tipo_control = 'PREVENTIVO' THEN 1 ELSE 0 END) AS preventivos,
    SUM(CASE WHEN tipo_control = 'REACTIVO' THEN 1 ELSE 0 END) AS reactivos,
    SUM(CASE WHEN tipo_control = 'DETECTIVE' THEN 1 ELSE 0 END) AS detectivos
FROM controles_amenazas;

-- Distribución por tipo de amenaza
SELECT
    SUBSTRING(a.codigo FROM 1 FOR 1) AS tipo_amenaza,
    CASE
        WHEN a.codigo LIKE 'N.%' THEN 'Desastres Naturales'
        WHEN a.codigo LIKE 'I.%' THEN 'Desastres Industriales'
        WHEN a.codigo LIKE 'E.%' THEN 'Errores no Intencionados'
        WHEN a.codigo LIKE 'A.%' THEN 'Ataques Intencionados'
    END AS descripcion,
    COUNT(DISTINCT a.id) AS amenazas_configuradas,
    COUNT(ca.id) AS controles_asignados
FROM amenazas a
LEFT JOIN controles_amenazas ca ON ca.amenaza_id = a.id
WHERE a.codigo ~ '^[NIEA]\.'
GROUP BY SUBSTRING(a.codigo FROM 1 FOR 1)
ORDER BY tipo_amenaza;
