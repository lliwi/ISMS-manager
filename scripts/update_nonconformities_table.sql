-- Script para actualizar la tabla nonconformities con la nueva estructura
-- ISO 27001:2023 - Capítulo 10.2

-- Paso 1: Agregar nuevas columnas
ALTER TABLE nonconformities ADD COLUMN IF NOT EXISTS nc_number VARCHAR(50) UNIQUE;
ALTER TABLE nonconformities ADD COLUMN IF NOT EXISTS origin ncorigin;
ALTER TABLE nonconformities ADD COLUMN IF NOT EXISTS detection_date TIMESTAMP;
ALTER TABLE nonconformities ADD COLUMN IF NOT EXISTS reported_date TIMESTAMP DEFAULT NOW();
ALTER TABLE nonconformities ADD COLUMN IF NOT EXISTS analysis_start_date TIMESTAMP;
ALTER TABLE nonconformities ADD COLUMN IF NOT EXISTS action_plan_date TIMESTAMP;
ALTER TABLE nonconformities ADD COLUMN IF NOT EXISTS implementation_start_date TIMESTAMP;
ALTER TABLE nonconformities ADD COLUMN IF NOT EXISTS verification_date TIMESTAMP;
ALTER TABLE nonconformities ADD COLUMN IF NOT EXISTS target_closure_date DATE;
ALTER TABLE nonconformities ADD COLUMN IF NOT EXISTS reported_by_id INTEGER;
ALTER TABLE nonconformities ADD COLUMN IF NOT EXISTS affected_controls JSON;
ALTER TABLE nonconformities ADD COLUMN IF NOT EXISTS audit_id INTEGER;
ALTER TABLE nonconformities ADD COLUMN IF NOT EXISTS incident_id INTEGER;
ALTER TABLE nonconformities ADD COLUMN IF NOT EXISTS immediate_action TEXT;
ALTER TABLE nonconformities ADD COLUMN IF NOT EXISTS immediate_action_date TIMESTAMP;
ALTER TABLE nonconformities ADD COLUMN IF NOT EXISTS rca_method rcamethod;
ALTER TABLE nonconformities ADD COLUMN IF NOT EXISTS root_causes JSON;
ALTER TABLE nonconformities ADD COLUMN IF NOT EXISTS contributing_factors JSON;
ALTER TABLE nonconformities ADD COLUMN IF NOT EXISTS is_recurrent BOOLEAN DEFAULT FALSE;
ALTER TABLE nonconformities ADD COLUMN IF NOT EXISTS related_nc_id INTEGER;
ALTER TABLE nonconformities ADD COLUMN IF NOT EXISTS similar_nc_analysis TEXT;
ALTER TABLE nonconformities ADD COLUMN IF NOT EXISTS effectiveness_verification TEXT;
ALTER TABLE nonconformities ADD COLUMN IF NOT EXISTS effectiveness_criteria TEXT;
ALTER TABLE nonconformities ADD COLUMN IF NOT EXISTS is_effective BOOLEAN;
ALTER TABLE nonconformities ADD COLUMN IF NOT EXISTS sgsi_changes_required BOOLEAN DEFAULT FALSE;
ALTER TABLE nonconformities ADD COLUMN IF NOT EXISTS sgsi_changes_description TEXT;
ALTER TABLE nonconformities ADD COLUMN IF NOT EXISTS sgsi_changes_implemented BOOLEAN DEFAULT FALSE;
ALTER TABLE nonconformities ADD COLUMN IF NOT EXISTS lessons_learned TEXT;
ALTER TABLE nonconformities ADD COLUMN IF NOT EXISTS preventive_measures JSON;
ALTER TABLE nonconformities ADD COLUMN IF NOT EXISTS estimated_cost FLOAT;
ALTER TABLE nonconformities ADD COLUMN IF NOT EXISTS actual_cost FLOAT;
ALTER TABLE nonconformities ADD COLUMN IF NOT EXISTS created_by_id INTEGER;
ALTER TABLE nonconformities ADD COLUMN IF NOT EXISTS updated_by_id INTEGER;
ALTER TABLE nonconformities ADD COLUMN IF NOT EXISTS notes TEXT;

-- Paso 2: Convertir columnas existentes a los nuevos tipos ENUM
-- Necesitamos usar USING para la conversión

-- Convertir severity de VARCHAR a ncseverity enum
ALTER TABLE nonconformities ALTER COLUMN severity TYPE ncseverity
  USING CASE
    WHEN severity = 'minor' THEN 'MINOR'::ncseverity
    WHEN severity = 'major' THEN 'MAJOR'::ncseverity
    WHEN severity = 'critical' THEN 'CRITICAL'::ncseverity
    ELSE 'MINOR'::ncseverity
  END;

-- Convertir status de VARCHAR a ncstatus enum
ALTER TABLE nonconformities ALTER COLUMN status TYPE ncstatus
  USING CASE
    WHEN status = 'new' OR status = 'open' THEN 'NEW'::ncstatus
    WHEN status = 'in_progress' THEN 'ANALYZING'::ncstatus
    WHEN status = 'closed' THEN 'CLOSED'::ncstatus
    ELSE 'NEW'::ncstatus
  END;

-- Hacer status NOT NULL con valor por defecto
ALTER TABLE nonconformities ALTER COLUMN status SET NOT NULL;
ALTER TABLE nonconformities ALTER COLUMN status SET DEFAULT 'NEW'::ncstatus;

-- Convertir closure_date de DATE a TIMESTAMP
ALTER TABLE nonconformities ALTER COLUMN closure_date TYPE TIMESTAMP;

-- Paso 3: Migrar datos de columnas antiguas a nuevas (si tienen datos)
UPDATE nonconformities
SET origin = 'OTHER'::ncorigin
WHERE origin IS NULL;

UPDATE nonconformities
SET detection_date = created_at
WHERE detection_date IS NULL AND created_at IS NOT NULL;

UPDATE nonconformities
SET reported_date = created_at
WHERE reported_date IS NULL AND created_at IS NOT NULL;

UPDATE nonconformities
SET reported_by_id = responsible_id
WHERE reported_by_id IS NULL;

-- Generar nc_number para registros existentes
UPDATE nonconformities
SET nc_number = 'NC-' || TO_CHAR(COALESCE(created_at, NOW()), 'YYYY-MM') || '-' || LPAD(id::TEXT, 3, '0')
WHERE nc_number IS NULL;

-- Paso 4: Hacer NOT NULL las columnas requeridas
ALTER TABLE nonconformities ALTER COLUMN nc_number SET NOT NULL;
ALTER TABLE nonconformities ALTER COLUMN origin SET NOT NULL;
ALTER TABLE nonconformities ALTER COLUMN detection_date SET NOT NULL;
ALTER TABLE nonconformities ALTER COLUMN reported_date SET NOT NULL;
ALTER TABLE nonconformities ALTER COLUMN reported_by_id SET NOT NULL;

-- Paso 5: Crear foreign keys para las nuevas columnas
ALTER TABLE nonconformities
  ADD CONSTRAINT fk_nc_audit
  FOREIGN KEY (audit_id) REFERENCES audits(id);

ALTER TABLE nonconformities
  ADD CONSTRAINT fk_nc_created_by
  FOREIGN KEY (created_by_id) REFERENCES users(id);

ALTER TABLE nonconformities
  ADD CONSTRAINT fk_nc_updated_by
  FOREIGN KEY (updated_by_id) REFERENCES users(id);

ALTER TABLE nonconformities
  ADD CONSTRAINT fk_nc_reported_by
  FOREIGN KEY (reported_by_id) REFERENCES users(id);

ALTER TABLE nonconformities
  ADD CONSTRAINT fk_nc_incident
  FOREIGN KEY (incident_id) REFERENCES incidents(id);

ALTER TABLE nonconformities
  ADD CONSTRAINT fk_nc_related_nc
  FOREIGN KEY (related_nc_id) REFERENCES nonconformities(id);

-- Paso 6: Eliminar columnas antiguas que ya no se usan
ALTER TABLE nonconformities DROP COLUMN IF EXISTS source;
ALTER TABLE nonconformities DROP COLUMN IF EXISTS root_cause_method;
ALTER TABLE nonconformities DROP COLUMN IF EXISTS target_date;
ALTER TABLE nonconformities DROP COLUMN IF EXISTS corrective_action;

-- Paso 7: Crear índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_nc_number ON nonconformities(nc_number);
CREATE INDEX IF NOT EXISTS idx_nc_status ON nonconformities(status);
CREATE INDEX IF NOT EXISTS idx_nc_severity ON nonconformities(severity);
CREATE INDEX IF NOT EXISTS idx_nc_responsible ON nonconformities(responsible_id);
CREATE INDEX IF NOT EXISTS idx_nc_created_at ON nonconformities(created_at);
CREATE INDEX IF NOT EXISTS idx_nc_audit ON nonconformities(audit_id);
CREATE INDEX IF NOT EXISTS idx_nc_incident ON nonconformities(incident_id);

-- Verificar la estructura actualizada
\d nonconformities
