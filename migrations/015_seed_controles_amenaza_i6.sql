-- Migración 015: Establecer controles para amenaza I.6 - Corte del suministro eléctrico
--
-- Esta migración define los controles ISO 27002 que mitigan la amenaza de
-- corte del suministro eléctrico, incluyendo tanto controles preventivos
-- como reactivos.

-- ====================================================================
-- Controles para Amenaza I.6 - Corte del suministro eléctrico
-- ====================================================================

INSERT INTO controles_amenazas (control_codigo, amenaza_id, tipo_control, efectividad)
VALUES
    -- Controles PREVENTIVOS (reducen la probabilidad de corte)
    ('A.7.13', 9, 'PREVENTIVO', 0.60),  -- Aseguramiento de la distribución de energía y telecomunicaciones
    ('A.8.1', 9, 'PREVENTIVO', 0.50),   -- Dispositivos de punto final de usuario (UPS locales)

    -- Controles REACTIVOS (reducen el impacto cuando ocurre)
    ('A.5.29', 9, 'REACTIVO', 0.85),    -- Seguridad de la información durante una interrupción
    ('A.5.30', 9, 'REACTIVO', 0.90),    -- Preparación de las TIC para la continuidad del negocio
    ('A.8.14', 9, 'REACTIVO', 0.70)     -- Redundancia de instalaciones de procesamiento de información

ON CONFLICT (control_codigo, amenaza_id) DO NOTHING;

-- ====================================================================
-- Verificación
-- ====================================================================

SELECT
    'Controles configurados para I.6' AS status,
    COUNT(*) AS total_controles,
    SUM(CASE WHEN tipo_control = 'PREVENTIVO' THEN 1 ELSE 0 END) AS preventivos,
    SUM(CASE WHEN tipo_control = 'REACTIVO' THEN 1 ELSE 0 END) AS reactivos
FROM controles_amenazas
WHERE amenaza_id = 9;

-- Mostrar detalle de los controles configurados
SELECT
    ca.control_codigo,
    sc.title AS control_nombre,
    ca.tipo_control,
    ca.efectividad,
    sc.maturity_score AS madurez_soa,
    sc.applicability_status
FROM controles_amenazas ca
LEFT JOIN soa_controls sc ON sc.control_id = ca.control_codigo
    AND sc.soa_version_id = (SELECT id FROM soa_versions WHERE is_current = true)
WHERE ca.amenaza_id = 9
ORDER BY ca.tipo_control, ca.efectividad DESC;
