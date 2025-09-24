-- Initial database setup for ISMS Manager
-- This file is executed when the PostgreSQL container starts

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS isms_db;

-- ISO 27001 Annex A Controls
-- This will be populated when the application starts
-- The application will create and manage all tables via SQLAlchemy