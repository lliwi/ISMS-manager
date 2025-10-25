-- Migración 013: Refactorizar controles_amenazas para usar SOA como referencia única
--
-- OBJETIVO:
-- - Eliminar dependencia de controles_iso27002
-- - Usar control_codigo (string) en vez de control_id (integer FK)
-- - Agregar tipo_control a la relación control-amenaza
-- - Esto permite que el sistema sobreviva a cambios de versión ISO/SOA
--
-- IMPORTANTE: Esta migración es IDEMPOTENTE y segura para:
-- - Instalaciones existentes (migra de estructura antigua a nueva)
-- - Instalaciones nuevas (no hace nada si ya tiene la estructura correcta)

DO $$
DECLARE
    tiene_control_id BOOLEAN;
    tiene_control_codigo BOOLEAN;
    count_old INTEGER;
    count_new INTEGER;
BEGIN
    -- ====================================================================
    -- VERIFICACIÓN: Solo ejecutar si la tabla tiene la estructura antigua
    -- ====================================================================

    -- Verificar si la tabla tiene la columna antigua (control_id)
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'controles_amenazas'
        AND column_name = 'control_id'
    ) INTO tiene_control_id;

    -- Verificar si la tabla ya tiene la columna nueva (control_codigo)
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'controles_amenazas'
        AND column_name = 'control_codigo'
    ) INTO tiene_control_codigo;

    -- Si ya tiene la estructura nueva, no hacer nada
    IF tiene_control_codigo AND NOT tiene_control_id THEN
        RAISE NOTICE 'La tabla controles_amenazas ya tiene la estructura nueva. Migración 013 omitida.';
        RETURN;
    END IF;

    -- Si no tiene la estructura antigua, tampoco hacer nada
    IF NOT tiene_control_id THEN
        RAISE NOTICE 'La tabla controles_amenazas no existe o tiene estructura desconocida. Migración 013 omitida.';
        RETURN;
    END IF;

    -- Si llegamos aquí, tenemos la estructura antigua y debemos migrar
    RAISE NOTICE 'Estructura antigua detectada en controles_amenazas. Procediendo con migración 013...';

    -- ====================================================================
    -- PASO 1: Crear tabla temporal con nueva estructura
    -- ====================================================================

    CREATE TABLE controles_amenazas_new (
        id SERIAL PRIMARY KEY,
        control_codigo VARCHAR(10) NOT NULL,
        amenaza_id INTEGER NOT NULL REFERENCES amenazas(id),
        tipo_control VARCHAR(20) NOT NULL DEFAULT 'PREVENTIVO',
        efectividad NUMERIC(3, 2) DEFAULT 1.00,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT uq_control_amenaza_new UNIQUE (control_codigo, amenaza_id)
    );

    CREATE INDEX idx_controles_amenazas_new_control ON controles_amenazas_new(control_codigo);
    CREATE INDEX idx_controles_amenazas_new_tipo ON controles_amenazas_new(tipo_control);

    RAISE NOTICE 'Tabla temporal controles_amenazas_new creada';

    -- ====================================================================
    -- PASO 2: Migrar datos existentes (si los hay)
    -- ====================================================================

    -- Convertir los registros existentes de control_id (FK a controles_iso27002)
    -- a control_codigo (string como "A.5.1")
    INSERT INTO controles_amenazas_new (control_codigo, amenaza_id, tipo_control, efectividad, created_at)
    SELECT
        'A.' || ci.codigo AS control_codigo,  -- Convertir "5.1" -> "A.5.1"
        ca.amenaza_id,
        ci.tipo_control,
        ca.efectividad,
        ca.created_at
    FROM controles_amenazas ca
    JOIN controles_iso27002 ci ON ca.control_id = ci.id
    WHERE ci.codigo IS NOT NULL;

    -- ====================================================================
    -- PASO 3: Verificar migración
    -- ====================================================================

    SELECT COUNT(*) INTO count_old FROM controles_amenazas;
    SELECT COUNT(*) INTO count_new FROM controles_amenazas_new;

    RAISE NOTICE 'Registros en controles_amenazas (antigua): %', count_old;
    RAISE NOTICE 'Registros en controles_amenazas_new (nueva): %', count_new;

    IF count_old > 0 AND count_new = 0 THEN
        RAISE EXCEPTION 'MIGRACIÓN FALLIDA: No se migraron datos';
    END IF;

    -- ====================================================================
    -- PASO 4: Reemplazar tabla antigua con nueva
    -- ====================================================================

    -- Eliminar constraint de la tabla antigua que podría bloquear el DROP
    BEGIN
        EXECUTE 'ALTER TABLE controles_amenazas DROP CONSTRAINT IF EXISTS uq_control_amenaza';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Constraint uq_control_amenaza no existe o ya fue eliminado';
    END;

    -- Eliminar tabla antigua
    DROP TABLE IF EXISTS controles_amenazas CASCADE;
    RAISE NOTICE 'Tabla antigua controles_amenazas eliminada';

    -- Renombrar tabla nueva
    ALTER TABLE controles_amenazas_new RENAME TO controles_amenazas;
    RAISE NOTICE 'Tabla controles_amenazas_new renombrada a controles_amenazas';

    -- Renombrar constraint
    ALTER TABLE controles_amenazas RENAME CONSTRAINT uq_control_amenaza_new TO uq_control_amenaza;

    -- Renombrar índices
    ALTER INDEX idx_controles_amenazas_new_control RENAME TO idx_controles_amenazas_control;
    ALTER INDEX idx_controles_amenazas_new_tipo RENAME TO idx_controles_amenazas_tipo;

    RAISE NOTICE '✅ Migración 013 completada exitosamente';
    RAISE NOTICE 'Total controles_amenazas migrados: %', count_new;

END $$;

-- ====================================================================
-- VERIFICACIÓN FINAL (siempre se ejecuta)
-- ====================================================================

SELECT
    'Migración 013: Verificación final' AS status,
    COUNT(*) AS total_controles_amenazas,
    COUNT(DISTINCT control_codigo) AS controles_unicos,
    COUNT(DISTINCT amenaza_id) AS amenazas_con_controles
FROM controles_amenazas;
