-- Script de prueba: crear relaciones control-amenaza para testing
-- Esto permite probar el cálculo de riesgos con la nueva estructura

-- Verificar que existe el SOA activo
DO $$
DECLARE
    soa_id INTEGER;
BEGIN
    SELECT id INTO soa_id FROM soa_versions WHERE is_current = true LIMIT 1;

    IF soa_id IS NULL THEN
        RAISE EXCEPTION 'No existe SOA activo. Primero debes crear un SOA.';
    END IF;

    RAISE NOTICE 'SOA activo encontrado con ID: %', soa_id;
END $$;

-- Obtener las primeras amenazas para testing
SELECT
    id,
    codigo,
    nombre
FROM amenazas
LIMIT 5;

-- Insertar algunas relaciones de ejemplo
-- Control A.5.1 (Políticas de seguridad) aplica a múltiples amenazas
INSERT INTO controles_amenazas (control_codigo, amenaza_id, tipo_control, efectividad)
SELECT
    'A.5.1',
    id,
    'PREVENTIVO',
    0.80
FROM amenazas
WHERE codigo IN ('E.1', 'E.2', 'E.24', 'E.25')  -- Amenazas de tipo error/daño
ON CONFLICT (control_codigo, amenaza_id) DO NOTHING;

-- Control A.8.1 (Dispositivos de usuario final) para amenazas de hardware
INSERT INTO controles_amenazas (control_codigo, amenaza_id, tipo_control, efectividad)
SELECT
    'A.8.1',
    id,
    'PREVENTIVO',
    0.90
FROM amenazas
WHERE codigo IN ('I.1', 'I.2', 'I.5')  -- Amenazas de tipo desastre/industrial
ON CONFLICT (control_codigo, amenaza_id) DO NOTHING;

-- Control A.6.8 (Gestión de activos) para amenazas varias
INSERT INTO controles_amenazas (control_codigo, amenaza_id, tipo_control, efectividad)
SELECT
    'A.6.8',
    id,
    'DETECTIVE',
    0.70
FROM amenazas
WHERE codigo LIKE 'A.%'  -- Amenazas de tipo ataque
LIMIT 5
ON CONFLICT (control_codigo, amenaza_id) DO NOTHING;

-- Verificar datos insertados
SELECT
    'Relaciones control-amenaza creadas' AS status,
    COUNT(*) AS total_relaciones,
    COUNT(DISTINCT control_codigo) AS controles_distintos,
    COUNT(DISTINCT amenaza_id) AS amenazas_cubiertas
FROM controles_amenazas;

-- Mostrar detalle
SELECT
    ca.control_codigo,
    sc.title AS control_nombre,
    a.codigo AS amenaza_codigo,
    a.nombre AS amenaza_nombre,
    ca.tipo_control,
    ca.efectividad
FROM controles_amenazas ca
JOIN amenazas a ON ca.amenaza_id = a.id
LEFT JOIN soa_controls sc ON sc.control_id = ca.control_codigo
    AND sc.soa_version_id = (SELECT id FROM soa_versions WHERE is_current = true LIMIT 1)
ORDER BY ca.control_codigo, a.codigo
LIMIT 20;
