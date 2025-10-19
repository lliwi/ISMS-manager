#!/bin/bash
# Entrypoint script for ISMS Manager
# Waits for database before starting the application

set -e

echo "=== ISMS Manager Startup ==="
echo "Waiting for database to be ready..."

# Wait for PostgreSQL to be ready
while ! pg_isready -h db -U isms -d isms_db > /dev/null 2>&1; do
    echo "Waiting for PostgreSQL..."
    sleep 1
done

echo "✓ Database is ready"

# Change ownership of any files created
chown -R isms:isms /app

# Execute the main command (Gunicorn)
# Note: Database tables will be created automatically by application.py
# Note: Gunicorn will run as root but will set workers to run as isms user
echo "Starting application..."
exec "$@"
