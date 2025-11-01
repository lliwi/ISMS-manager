-- Seed data para servicios de prueba
-- Insertar servicios de ejemplo

-- Servicio 1: Portal Web Corporativo
INSERT INTO services (
    service_code, name, description, service_type, status,
    service_owner_id, criticality, required_availability,
    rto, rpo, operating_hours, department, annual_cost
) VALUES (
    'SRV-001',
    'Portal Web Corporativo',
    'Sitio web principal de la organización que proporciona información corporativa y acceso a servicios online',
    'APPLICATION',
    'ACTIVE',
    1,  -- Usuario admin
    8,  -- Alta criticidad
    99.5,
    0.02,  -- RTO: 0.02 días (~30 minutos)
    0.01,  -- RPO: 0.01 días (~15 minutos)
    '24/7',
    'IT',
    50000.00
);

-- Servicio 2: Sistema de Correo Electrónico
INSERT INTO services (
    service_code, name, description, service_type, status,
    service_owner_id, technical_manager_id, criticality, required_availability,
    rto, rpo, operating_hours, department, annual_cost
) VALUES (
    'SRV-002',
    'Sistema de Correo Electrónico',
    'Servicio de correo electrónico corporativo para toda la organización',
    'TECHNICAL',
    'ACTIVE',
    1,  -- Owner
    2,  -- Technical manager
    9,  -- Crítico
    99.9,
    0.01,  -- RTO: 0.01 días (~15 minutos)
    0.003,  -- RPO: 0.003 días (~5 minutos)
    '24/7',
    'IT',
    75000.00
);

-- Servicio 3: Red Corporativa
INSERT INTO services (
    service_code, name, description, service_type, status,
    service_owner_id, criticality, required_availability,
    rto, rpo, operating_hours, department
) VALUES (
    'SRV-003',
    'Red Corporativa',
    'Infraestructura de red que conecta todas las sedes y permite la comunicación',
    'INFRASTRUCTURE',
    'ACTIVE',
    1,
    10,  -- Crítico
    99.99,
    0.007,  -- RTO: 0.007 días (~10 minutos)
    0,   -- RPO: 0 días (no aplica pérdida de datos)
    '24/7',
    'IT'
);

-- Servicio 4: Sistema ERP
INSERT INTO services (
    service_code, name, description, service_type, status,
    service_owner_id, criticality, required_availability,
    rto, rpo, operating_hours, department, annual_cost
) VALUES (
    'SRV-004',
    'Sistema ERP',
    'Sistema integrado de gestión empresarial (finanzas, RRHH, operaciones)',
    'BUSINESS',
    'ACTIVE',
    1,
    9,
    99.5,
    0.04,  -- RTO: 0.04 días (~1 hora)
    0.02,  -- RPO: 0.02 días (~30 minutos)
    '8-20 L-V',
    'Operaciones',
    120000.00
);

-- Servicio 5: Backup y Recuperación
INSERT INTO services (
    service_code, name, description, service_type, status,
    service_owner_id, criticality, required_availability,
    rto, operating_hours, department, annual_cost
) VALUES (
    'SRV-005',
    'Backup y Recuperación',
    'Sistema de copias de seguridad y recuperación ante desastres',
    'SUPPORT',
    'ACTIVE',
    1,
    8,
    99.0,
    0.08,  -- RTO: 0.08 días (~2 horas)
    '24/7',
    'IT',
    30000.00
);

-- Servicio 6: VPN Corporativa (en planificación)
INSERT INTO services (
    service_code, name, description, service_type, status,
    service_owner_id, criticality, required_availability,
    operating_hours, department
) VALUES (
    'SRV-006',
    'VPN Corporativa',
    'Acceso remoto seguro a la red corporativa para empleados',
    'INFRASTRUCTURE',
    'PLANNED',
    1,
    7,
    98.0,
    '24/7',
    'IT'
);

-- Asociar activos a servicios (si existen activos)
-- Portal Web depende de servidor web y switch
INSERT INTO service_asset_association (service_id, asset_id, role)
SELECT 1, id, 'critical'
FROM assets
WHERE asset_code IN ('HW-00001', 'HW-00002')
ON CONFLICT DO NOTHING;

-- Crear dependencias entre servicios
-- Portal Web depende de Red Corporativa
INSERT INTO service_dependencies (service_id, depends_on_service_id, dependency_type, description)
VALUES (1, 3, 'required', 'El portal web requiere conectividad de red');

-- Sistema de Correo depende de Red Corporativa
INSERT INTO service_dependencies (service_id, depends_on_service_id, dependency_type, description)
VALUES (2, 3, 'required', 'El correo electrónico requiere red para funcionar');

-- ERP depende de Red Corporativa
INSERT INTO service_dependencies (service_id, depends_on_service_id, dependency_type, description)
VALUES (4, 3, 'required', 'El ERP necesita red para acceso de usuarios');

-- Portal Web se beneficia de Backup
INSERT INTO service_dependencies (service_id, depends_on_service_id, dependency_type, description)
VALUES (1, 5, 'enhances', 'El backup protege los datos del portal');

-- ERP se beneficia de Backup
INSERT INTO service_dependencies (service_id, depends_on_service_id, dependency_type, description)
VALUES (4, 5, 'required', 'El ERP requiere backup para continuidad de negocio');

-- Mostrar resumen
SELECT 'Servicios creados:' as info;
SELECT service_code, name, service_type, status, criticality FROM services ORDER BY service_code;

SELECT 'Dependencias creadas:' as info;
SELECT
    s1.service_code || ' → ' || s2.service_code as dependency,
    sd.dependency_type
FROM service_dependencies sd
JOIN services s1 ON sd.service_id = s1.id
JOIN services s2 ON sd.depends_on_service_id = s2.id
ORDER BY s1.service_code;
