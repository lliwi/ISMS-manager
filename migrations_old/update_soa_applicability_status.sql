-- Migración: Actualizar campos de aplicabilidad SOA
-- Fecha: 2025-09-28
-- Descripción: Agregar applicability_status y transfer_details, migrar datos existentes

-- 1. Agregar nueva columna applicability_status
ALTER TABLE soa_controls
ADD COLUMN IF NOT EXISTS applicability_status VARCHAR(20) DEFAULT 'aplicable';

-- 2. Agregar nueva columna transfer_details
ALTER TABLE soa_controls
ADD COLUMN IF NOT EXISTS transfer_details TEXT;

-- 3. Migrar datos existentes de is_applicable a applicability_status
UPDATE soa_controls
SET applicability_status = CASE
    WHEN is_applicable = true THEN 'aplicable'
    WHEN is_applicable = false THEN 'no_aplicable'
    ELSE 'aplicable'
END
WHERE applicability_status = 'aplicable'; -- Solo actualizar los que tienen el valor por defecto

-- 4. Actualizar implementation_status: 'pending' -> 'not_implemented'
UPDATE soa_controls
SET implementation_status = 'not_implemented'
WHERE implementation_status = 'pending';

-- 5. Actualizar controles no aplicables
UPDATE soa_controls
SET implementation_status = 'not_implemented',
    applicability_status = 'no_aplicable'
WHERE implementation_status = 'not_applicable';

-- Verificar resultados
SELECT 'Estadísticas de aplicabilidad:' as info;
SELECT
    applicability_status,
    COUNT(*) as count
FROM soa_controls
GROUP BY applicability_status
ORDER BY applicability_status;

SELECT 'Estadísticas de implementación:' as info;
SELECT
    implementation_status,
    COUNT(*) as count
FROM soa_controls
GROUP BY implementation_status
ORDER BY implementation_status;