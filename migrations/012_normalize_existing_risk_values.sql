-- Migración: Normalizar valores de riesgos existentes
-- Fecha: 2025-02-01
-- Descripción: Dividir todos los valores de riesgo entre 5 para ajustarlos a la nueva fórmula normalizada

-- Los valores antiguos usaban multiplicador de 10, los nuevos usan multiplicador de 2
-- Factor de corrección: dividir entre 5 (10 / 2 = 5)

-- IMPORTANTE: Solo recalcular riesgos con valores > 100 (que están en la escala antigua)

-- Actualizar impacto intrínseco
UPDATE riesgos
SET impacto_intrinseco = ROUND(impacto_intrinseco / 5.0, 2)
WHERE impacto_intrinseco > 10;

-- Actualizar nivel de riesgo intrínseco
UPDATE riesgos
SET nivel_riesgo_intrinseco = ROUND(nivel_riesgo_intrinseco / 5.0, 2)
WHERE nivel_riesgo_intrinseco > 100;

-- Actualizar impacto efectivo
UPDATE riesgos
SET impacto_efectivo = ROUND(impacto_efectivo / 5.0, 2)
WHERE impacto_efectivo > 10;

-- Actualizar nivel de riesgo efectivo
UPDATE riesgos
SET nivel_riesgo_efectivo = ROUND(nivel_riesgo_efectivo / 5.0, 2)
WHERE nivel_riesgo_efectivo > 100;

-- Verificar resultados
SELECT
    COUNT(*) as total_riesgos,
    MAX(impacto_intrinseco) as max_impacto_intrinseco,
    MAX(nivel_riesgo_intrinseco) as max_riesgo_intrinseco,
    MAX(impacto_efectivo) as max_impacto_efectivo,
    MAX(nivel_riesgo_efectivo) as max_riesgo_efectivo
FROM riesgos;
