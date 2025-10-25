-- Migración 010: Eliminar recursos_informacion y simplificar modelo
-- Los recursos eran redundantes con los activos principales

-- Paso 1: Eliminar foreign key de riesgos a recursos_informacion
ALTER TABLE riesgos DROP CONSTRAINT IF EXISTS riesgos_recurso_id_fkey;

-- Paso 2: Eliminar columna recurso_id de riesgos
ALTER TABLE riesgos DROP COLUMN IF EXISTS recurso_id;

-- Paso 3: Eliminar columna importancia_tipologica (venía de recursos)
ALTER TABLE riesgos DROP COLUMN IF EXISTS importancia_tipologica;

-- Paso 4: Eliminar tabla activos_recursos (relación entre activos y recursos)
DROP TABLE IF EXISTS activos_recursos CASCADE;

-- Paso 5: Eliminar tabla recursos_informacion
DROP TABLE IF EXISTS recursos_informacion CASCADE;

-- Paso 6: Actualizar dashboard stats para eliminar referencia a recursos
-- (No se requiere SQL, se actualizará en el código)

COMMIT;
