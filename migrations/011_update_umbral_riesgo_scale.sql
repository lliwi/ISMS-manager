-- Migración: Actualizar escala de umbral_riesgo_objetivo de 0-25 a 0-100
-- Fecha: 2025-02-01
-- Descripción: Convertir los umbrales de riesgo existentes a la nueva escala normalizada

-- Actualizar todos los umbrales multiplicando por 4 (factor de conversión de escala 0-25 a 0-100)
UPDATE evaluaciones_riesgo
SET umbral_riesgo_objetivo = ROUND(umbral_riesgo_objetivo * 4.0, 2)
WHERE umbral_riesgo_objetivo IS NOT NULL;

-- Verificar resultados
-- SELECT id, nombre, umbral_riesgo_objetivo, fecha_inicio
-- FROM evaluaciones_riesgo
-- ORDER BY fecha_inicio DESC;
