-- Initial database setup for ISMS Manager
-- This file is executed when the PostgreSQL container starts

-- Note: Database creation is handled by docker-compose environment variables
-- POSTGRES_DB=isms_db creates the database automatically

-- ISO 27001 Annex A Controls
-- This will be populated when the application starts
-- The application will create and manage all tables via SQLAlchemy

-- Post-migration updates for existing installations
-- These will be executed safely with IF NOT EXISTS clauses

-- Update for SOA applicability status (safe for new installations)
DO $$
BEGIN
    -- Add applicability_status column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'soa_controls'
        AND column_name = 'applicability_status'
    ) THEN
        ALTER TABLE soa_controls
        ADD COLUMN applicability_status VARCHAR(20) DEFAULT 'aplicable';

        -- Migrate existing data
        UPDATE soa_controls
        SET applicability_status = CASE
            WHEN is_applicable = true THEN 'aplicable'
            WHEN is_applicable = false THEN 'no_aplicable'
            ELSE 'aplicable'
        END;
    END IF;

    -- Add transfer_details column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'soa_controls'
        AND column_name = 'transfer_details'
    ) THEN
        ALTER TABLE soa_controls
        ADD COLUMN transfer_details TEXT;
    END IF;

    -- Update implementation_status values if needed
    UPDATE soa_controls
    SET implementation_status = 'not_implemented'
    WHERE implementation_status = 'pending';

    UPDATE soa_controls
    SET implementation_status = 'not_implemented',
        applicability_status = 'no_aplicable'
    WHERE implementation_status = 'not_applicable';

    -- Update maturity_level default for new installations
    -- Note: We keep existing 'inicial' values for compatibility
    -- Only new controls will have 'no_gestionado' as default

END $$;