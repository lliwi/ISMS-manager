#!/bin/bash

# Script de verificación para nuevas instalaciones de ISMS Manager
# Verifica que todos los componentes estén correctamente configurados

echo "=================================================="
echo "  ISMS Manager - Verificación de Instalación"
echo "=================================================="
echo ""

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para verificar archivos
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 existe"
        return 0
    else
        echo -e "${RED}✗${NC} $1 NO ENCONTRADO"
        return 1
    fi
}

# Función para verificar directorios
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} Directorio $1 existe"
        return 0
    else
        echo -e "${RED}✗${NC} Directorio $1 NO ENCONTRADO"
        return 1
    fi
}

echo "1. Verificando archivos de configuración..."
check_file ".env" || echo -e "${YELLOW}  → Copiar .env.example a .env${NC}"
check_file "docker-compose.yml"
check_file "Dockerfile"
check_file "requirements.txt"
echo ""

echo "2. Verificando estructura de directorios..."
check_dir "blueprints"
check_dir "templates"
check_dir "static"
check_dir "migrations"
check_dir "utils"
check_dir "forms"
check_dir "services"
echo ""

echo "3. Verificando archivos principales..."
check_file "app.py"
check_file "models.py"
check_file "config.py"
echo ""

echo "4. Verificando módulos de utilidades..."
check_file "utils/__init__.py"
check_file "utils/decorators.py"
check_file "utils/validators.py"
check_file "utils/audit_helper.py"
echo ""

echo "5. Verificando formularios..."
check_file "forms/__init__.py"
check_file "forms/user_forms.py"
echo ""

echo "6. Verificando blueprints..."
check_file "blueprints/__init__.py"
check_file "blueprints/auth.py"
check_file "blueprints/admin.py"
check_file "blueprints/dashboard.py"
check_file "blueprints/soa.py"
check_file "blueprints/documents.py"
echo ""

echo "7. Verificando scripts de migración..."
check_file "migrations/versions/003_add_user_security_fields.py"
check_file "run_migration.py"
check_file "init_new_installation.py"
echo ""

echo "8. Verificando variables de entorno críticas..."
if [ -f ".env" ]; then
    if grep -q "SECRET_KEY=your-secret-key-here" .env || grep -q "SECRET_KEY=dev-secret-key-change-in-production" .env; then
        echo -e "${YELLOW}⚠${NC} SECRET_KEY usa valor por defecto - CAMBIAR EN PRODUCCIÓN"
    else
        echo -e "${GREEN}✓${NC} SECRET_KEY configurado"
    fi

    if grep -q "DATABASE_URL" .env; then
        echo -e "${GREEN}✓${NC} DATABASE_URL configurado"
    else
        echo -e "${RED}✗${NC} DATABASE_URL no configurado"
    fi
else
    echo -e "${RED}✗${NC} Archivo .env no encontrado"
fi
echo ""

echo "9. Verificando contenedores Docker..."
if command -v docker &> /dev/null; then
    if docker ps | grep -q "ismsmanager"; then
        echo -e "${GREEN}✓${NC} Contenedores Docker en ejecución"
        docker ps --format "table {{.Names}}\t{{.Status}}" | grep ismsmanager
    else
        echo -e "${YELLOW}⚠${NC} Contenedores Docker no están corriendo"
        echo "  → Ejecutar: docker-compose up -d"
    fi
else
    echo -e "${YELLOW}⚠${NC} Docker no instalado"
fi
echo ""

echo "10. Verificando Python y dependencias..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✓${NC} Python instalado: $PYTHON_VERSION"

    # Verificar versión mínima 3.11
    MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 11 ]; then
        echo -e "${GREEN}✓${NC} Versión de Python cumple requisitos (>= 3.11)"
    else
        echo -e "${YELLOW}⚠${NC} Python $PYTHON_VERSION detectado, se recomienda 3.11+"
    fi
else
    echo -e "${RED}✗${NC} Python no instalado"
fi
echo ""

echo "=================================================="
echo "  Verificación completada"
echo "=================================================="
echo ""
echo "Próximos pasos para nueva instalación:"
echo ""
echo "1. Configurar .env con valores de producción:"
echo "   - SECRET_KEY (generar con: python -c 'import secrets; print(secrets.token_hex(32))')"
echo "   - DATABASE_URL"
echo "   - SESSION_COOKIE_SECURE=True (para HTTPS)"
echo ""
echo "2. Iniciar contenedores:"
echo "   docker-compose up -d"
echo ""
echo "3. Verificar instalación:"
echo "   docker exec ismsmanager-web-1 python init_new_installation.py"
echo ""
echo "4. Acceder a la aplicación:"
echo "   http://localhost"
echo "   Usuario: admin / Contraseña: admin123"
echo ""
echo "5. Cambiar contraseña de admin en primer login"
echo ""
echo "=================================================="
