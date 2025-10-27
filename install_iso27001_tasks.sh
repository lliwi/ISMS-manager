#!/bin/bash
###############################################################################
# Script de Instalación de Tareas Periódicas ISO/IEC 27001:2023
#
# Este script debe ejecutarse dentro del contenedor Docker de la aplicación
# para inicializar las plantillas de tareas recomendadas por ISO 27001
#
# Uso:
#   docker exec -it isms-manager bash
#   ./install_iso27001_tasks.sh
#
# O directamente:
#   docker exec -it isms-manager python init_iso27001_tasks.py
###############################################################################

set -e  # Salir si hay algún error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "================================================================================"
echo "  INSTALACIÓN DE PLANTILLAS DE TAREAS ISO/IEC 27001:2023"
echo "================================================================================"
echo -e "${NC}"

# Verificar que estamos en el directorio correcto
if [ ! -f "init_iso27001_tasks.py" ]; then
    echo -e "${RED}❌ Error: No se encuentra el archivo init_iso27001_tasks.py${NC}"
    echo "   Asegúrate de ejecutar este script desde el directorio raíz de la aplicación"
    exit 1
fi

# Verificar que existe la base de datos
if [ ! -f "instance/app.db" ]; then
    echo -e "${YELLOW}⚠️  Advertencia: No se encuentra la base de datos${NC}"
    echo "   ¿Deseas crear la base de datos primero? (s/N)"
    read -r response
    if [[ "$response" =~ ^([sS])$ ]]; then
        echo -e "${BLUE}🔨 Creando base de datos...${NC}"
        python -c "from application import app, db; app.app_context().push(); db.create_all()"
        echo -e "${GREEN}✅ Base de datos creada${NC}"
    else
        echo -e "${RED}❌ Operación cancelada${NC}"
        exit 1
    fi
fi

# Ejecutar script de inicialización
echo -e "${BLUE}🚀 Iniciando instalación de plantillas de tareas...${NC}"
echo

python init_iso27001_tasks.py

# Verificar resultado
if [ $? -eq 0 ]; then
    echo
    echo -e "${GREEN}"
    echo "================================================================================"
    echo "  ✅ INSTALACIÓN COMPLETADA EXITOSAMENTE"
    echo "================================================================================"
    echo -e "${NC}"
    echo
    echo -e "${BLUE}📌 Accede a tu aplicación ISMS Manager para comenzar:${NC}"
    echo "   🌐 http://localhost/tareas/templates"
    echo
else
    echo
    echo -e "${RED}"
    echo "================================================================================"
    echo "  ❌ ERROR EN LA INSTALACIÓN"
    echo "================================================================================"
    echo -e "${NC}"
    echo
    echo "Por favor revisa los errores anteriores y vuelve a intentar."
    exit 1
fi
