-- Initial database setup for ISMS Manager
-- This file is executed when the PostgreSQL container starts

-- Note: Database creation is handled by docker-compose environment variables
-- POSTGRES_DB=isms_db creates the database automatically

-- ISO 27001 Annex A Controls
-- This will be populated when the application starts
-- The application will create and manage all tables via SQLAlchemy

-- Post-migration updates for existing installations
-- These will be executed safely only if tables exist

-- Update for SOA applicability status (safe for new installations)
DO $$
BEGIN
    -- Only execute if the table exists (for existing installations)
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_name = 'soa_controls'
    ) THEN
        -- Add applicability_status column if it doesn't exist
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'soa_controls'
            AND column_name = 'applicability_status'
        ) THEN
            ALTER TABLE soa_controls
            ADD COLUMN applicability_status VARCHAR(20) DEFAULT 'aplicable';

            -- Migrate existing data only if is_applicable column exists
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'soa_controls'
                AND column_name = 'is_applicable'
            ) THEN
                UPDATE soa_controls
                SET applicability_status = CASE
                    WHEN is_applicable = true THEN 'aplicable'
                    WHEN is_applicable = false THEN 'no_aplicable'
                    ELSE 'aplicable'
                END;
            END IF;
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
    END IF;

    -- If table doesn't exist, this is a new installation
    -- Tables will be created by Flask-Migrate

END $$;