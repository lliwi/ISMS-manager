-- Migración 007: Agregar tablas de Servicios
-- Fecha: 2025-10-12
-- Descripción: Crear estructura para gestión de servicios y su relación con activos

-- Crear tipo ENUM para ServiceType
CREATE TYPE servicetype AS ENUM (
    'BUSINESS',
    'TECHNICAL',
    'INFRASTRUCTURE',
    'APPLICATION',
    'SUPPORT'
);

-- Crear tipo ENUM para ServiceStatus
CREATE TYPE servicestatus AS ENUM (
    'ACTIVE',
    'INACTIVE',
    'DEPRECATED',
    'PLANNED'
);

-- Crear tabla de servicios
CREATE TABLE services (
    id SERIAL PRIMARY KEY,
    service_code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,

    -- Clasificación
    service_type servicetype NOT NULL,
    status servicestatus DEFAULT 'ACTIVE',

    -- Responsables
    service_owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    technical_manager_id INTEGER REFERENCES users(id) ON DELETE SET NULL,

    -- Criticidad y disponibilidad
    criticality INTEGER DEFAULT 5 CHECK (criticality >= 1 AND criticality <= 10),
    required_availability FLOAT CHECK (required_availability >= 0 AND required_availability <= 100),
    rto INTEGER,  -- Recovery Time Objective en minutos
    rpo INTEGER,  -- Recovery Point Objective en minutos

    -- Información operativa
    operating_hours VARCHAR(100),
    max_users INTEGER,
    department VARCHAR(100),

    -- Costos
    annual_cost FLOAT,

    -- Auditoría
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by_id INTEGER REFERENCES users(id) ON DELETE SET NULL,

    notes TEXT
);

-- Índices para servicios
CREATE INDEX idx_services_code ON services(service_code);
CREATE INDEX idx_services_type ON services(service_type);
CREATE INDEX idx_services_status ON services(status);
CREATE INDEX idx_services_owner ON services(service_owner_id);
CREATE INDEX idx_services_department ON services(department);

-- Crear tabla de asociación service_asset
CREATE TABLE service_asset_association (
    service_id INTEGER NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    asset_id INTEGER NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    role VARCHAR(50),  -- critical, support, backup, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (service_id, asset_id)
);

-- Índices para asociación
CREATE INDEX idx_service_asset_service ON service_asset_association(service_id);
CREATE INDEX idx_service_asset_asset ON service_asset_association(asset_id);

-- Crear tabla de dependencias entre servicios
CREATE TABLE service_dependencies (
    id SERIAL PRIMARY KEY,
    service_id INTEGER NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    depends_on_service_id INTEGER NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    dependency_type VARCHAR(50),  -- required, optional, enhances
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraint para evitar auto-dependencias
    CONSTRAINT no_self_dependency CHECK (service_id != depends_on_service_id),

    -- Constraint para evitar dependencias duplicadas
    CONSTRAINT unique_dependency UNIQUE (service_id, depends_on_service_id)
);

-- Índices para dependencias
CREATE INDEX idx_service_deps_service ON service_dependencies(service_id);
CREATE INDEX idx_service_deps_depends_on ON service_dependencies(depends_on_service_id);

-- Comentarios en las tablas
COMMENT ON TABLE services IS 'Servicios de negocio y técnicos - ISO 27001 Control 5.9 y 8.1';
COMMENT ON TABLE service_asset_association IS 'Relación muchos a muchos entre servicios y activos';
COMMENT ON TABLE service_dependencies IS 'Dependencias entre servicios para análisis de impacto';

-- Comentarios en columnas importantes
COMMENT ON COLUMN services.rto IS 'Recovery Time Objective - Tiempo máximo aceptable de interrupción (minutos)';
COMMENT ON COLUMN services.rpo IS 'Recovery Point Objective - Máxima pérdida de datos aceptable (minutos)';
COMMENT ON COLUMN services.required_availability IS 'Disponibilidad requerida en porcentaje (ej: 99.9)';
COMMENT ON COLUMN service_asset_association.role IS 'Rol del activo en el servicio: critical, support, backup';
