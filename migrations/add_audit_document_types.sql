-- Migración: Agregar tipos de documentos de auditoría al enum DocumentType
-- Fecha: 2025-10-19
-- Descripción: Agrega los valores necesarios para los documentos de auditoría según ISO 27001

-- Agregar valores de documentos de auditoría
ALTER TYPE documenttype ADD VALUE IF NOT EXISTS 'AUDIT_PLAN';
ALTER TYPE documenttype ADD VALUE IF NOT EXISTS 'AUDIT_REPORT';
ALTER TYPE documenttype ADD VALUE IF NOT EXISTS 'OPENING_MEETING';
ALTER TYPE documenttype ADD VALUE IF NOT EXISTS 'CLOSING_MEETING';
ALTER TYPE documenttype ADD VALUE IF NOT EXISTS 'CHECKLIST';

-- Verificar valores actuales
-- SELECT enum_range(NULL::documenttype);
