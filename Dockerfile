# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=application.py \
    FLASK_ENV=production

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    python3-dev \
    libpq-dev \
    libreoffice \
    libreoffice-writer \
    libreoffice-calc \
    libreoffice-impress \
    curl \
    gosu \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Copy project files
COPY . .

# Create uploads directory
RUN mkdir -p uploads logs

# Create non-root user (but don't switch to it yet, entrypoint will do it)
RUN useradd -m -u 1000 isms && chown -R isms:isms /app

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Use entrypoint script
ENTRYPOINT ["/entrypoint.sh"]

# Start command (will be passed to entrypoint)
# Gunicorn will run workers as user 'isms' (uid 1000)
# Timeout aumentado a 600s para permitir operaciones largas como backup/restore
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "--timeout", "600", "--user", "1000", "--group", "1000", "wsgi:app"]