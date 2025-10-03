# ISMS Manager

Sistema de Gestión de Seguridad de la Información conforme a ISO/IEC 27001.

## Descripción

ISMS Manager es una aplicación web desarrollada en Flask que ayuda a las organizaciones a gestionar su Sistema de Gestión de Seguridad de la Información (ISMS) de acuerdo con los requisitos de la norma ISO/IEC 27001.

### Funcionalidades Principales

- **Gestión del SOA (Statement of Applicability)**: Control de aplicabilidad de controles ISO 27001
- **Gestión de Riesgos**: Identificación, evaluación y tratamiento de riesgos
- **Gestión de Documentación**: Control de versiones y aprobaciones
- **Dashboard de Indicadores**: KPIs y métricas del sistema ISMS
- **Gestión de Incidentes**: Registro y seguimiento de incidentes de seguridad
- **Auditorías Internas**: Planificación y seguimiento de auditorías
- **No Conformidades**: Gestión de hallazgos y acciones correctivas
- **Tareas Periódicas**: Seguimiento de tareas del sistema
- **Formación y Concienciación**: Registro de sesiones de entrenamiento

## Requisitos

- Python 3.11+
- PostgreSQL 12+
- Docker y Docker Compose (opcional)

## Instalación y Configuración

### Opción 1: Con Docker (Recomendado)

1. Clona el repositorio:
```bash
git clone <repository-url>
cd "ISMS Manager"
```

2. Copia el archivo de configuración:
```bash
cp .env.example .env
```

3. Edita las variables de entorno en `.env`

4. Levanta los servicios con Docker Compose:
```bash
# Para desarrollo
docker-compose -f docker-compose.dev.yml up -d

# Para producción
docker-compose up -d
```

### Opción 2: Instalación Manual

1. Clona el repositorio y entra al directorio

2. Crea un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instala las dependencias:
```bash
pip install -r requirements.txt
```

4. Configura PostgreSQL y crea la base de datos:
```sql
CREATE DATABASE isms_db;
CREATE USER isms WITH PASSWORD 'isms123';
GRANT ALL PRIVILEGES ON DATABASE isms_db TO isms;
```

5. Configura las variables de entorno:
```bash
export DATABASE_URL="postgresql://isms:isms123@localhost/isms_db"
export SECRET_KEY="your-secret-key"
export FLASK_ENV="development"
```

6. Inicializa la base de datos:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

7. Ejecuta la aplicación:
```bash
python app.py
```

## Uso

1. Accede a la aplicación en `http://localhost:5000`
2. Inicia sesión con las credenciales por defecto:
   - **Usuario**: admin
   - **Contraseña**: admin123

3. Cambia la contraseña del administrador desde el panel de administración

## Estructura del Proyecto

```
ISMS Manager/
├── app.py                 # Aplicación principal Flask
├── config.py              # Configuración de la aplicación
├── models.py              # Modelos de base de datos
├── requirements.txt       # Dependencias Python
├── blueprints/           # Módulos de la aplicación
│   ├── auth.py           # Autenticación
│   ├── dashboard.py      # Dashboard principal
│   ├── soa.py            # Gestión SOA
│   ├── risks.py          # Gestión de riesgos
│   └── ...               # Otros módulos
├── templates/            # Plantillas HTML
├── static/               # Archivos estáticos
├── docker-compose.yml    # Configuración Docker producción
├── docker-compose.dev.yml # Configuración Docker desarrollo
└── README.md            # Este archivo
```

## Desarrollo

### Comandos Útiles

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar en modo desarrollo
python app.py

# Migraciones de base de datos
flask db migrate -m "Description"
flask db upgrade

# Ejecutar tests
pytest

# Linting
flake8 .
```

### Roles de Usuario

- **Administrador del Sistema**: Acceso completo
- **Responsable de Seguridad (CISO)**: Todos los módulos con permisos de aprobación
- **Auditor Interno**: Módulo de auditorías + lectura en otros
- **Propietario de Proceso**: Módulos específicos según responsabilidad
- **Usuario General**: Acceso limitado a funcionalidades básicas

## Configuración del Agente IA (Opcional)

ISMS Manager incluye un sistema de verificación automática de documentos usando Inteligencia Artificial. Este sistema analiza los documentos contra los controles SOA de ISO 27001 para validar su cumplimiento.

### Proveedores Soportados

#### 1. Ollama (Recomendado para uso local)

Ollama permite ejecutar modelos de IA localmente sin necesidad de API Keys ni conexión a internet.

**Instalación:**
```bash
# Descargar e instalar Ollama desde https://ollama.ai
curl https://ollama.ai/install.sh | sh

# Descargar un modelo (ejemplo: Llama 3)
ollama pull llama3:8b
```

**Configuración en `.env`:**
```bash
AI_VERIFICATION_ENABLED=True
AI_PROVIDER=ollama
AI_MODEL=llama3:8b
AI_BASE_URL=http://localhost:11434
AI_TIMEOUT=120
KNOWLEDGE_BASE_PATH=knowledge
```

**Modelos recomendados:**
- `llama3:8b` - Rápido, buen balance calidad/velocidad (requiere 8GB RAM)
- `llama3:70b` - Máxima calidad (requiere 64GB RAM)
- `mistral:7b` - Alternativa ligera (requiere 4GB RAM)
- `deepseek-coder:6.7b` - Optimizado para análisis técnico

#### 2. OpenAI (GPT-4, GPT-3.5)

Utiliza los modelos de OpenAI vía API (requiere API Key de pago).

**Configuración en `.env`:**
```bash
AI_VERIFICATION_ENABLED=True
AI_PROVIDER=openai
AI_MODEL=gpt-4
AI_API_KEY=sk-your-openai-api-key
AI_TIMEOUT=120
KNOWLEDGE_BASE_PATH=knowledge
```

**Modelos disponibles:**
- `gpt-4` - Máxima calidad (más costoso)
- `gpt-4-turbo` - Balance calidad/precio
- `gpt-3.5-turbo` - Económico y rápido

#### 3. DeepSeek

Alternativa económica a OpenAI con excelentes resultados.

**Configuración en `.env`:**
```bash
AI_VERIFICATION_ENABLED=True
AI_PROVIDER=deepseek
AI_MODEL=deepseek-chat
AI_API_KEY=your-deepseek-api-key
AI_BASE_URL=https://api.deepseek.com
AI_TIMEOUT=120
KNOWLEDGE_BASE_PATH=knowledge
```

### Base de Conocimiento

El sistema puede utilizar una base de conocimiento con los documentos de las normas ISO para mejorar la precisión de las verificaciones.

**Configuración:**

1. Crea el directorio `knowledge` en la raíz del proyecto
2. Coloca los PDFs de las normas ISO 27001, ISO 27002, etc.
3. El sistema extraerá automáticamente las primeras 10 páginas de cada documento

```bash
mkdir -p knowledge
# Copiar tus PDFs de normas ISO al directorio knowledge/
```

### Variables de Configuración

| Variable | Descripción | Valores | Por defecto |
|----------|-------------|---------|-------------|
| `AI_VERIFICATION_ENABLED` | Habilita/deshabilita el sistema IA | `True/False` | `False` |
| `AI_PROVIDER` | Proveedor de IA a utilizar | `ollama/openai/deepseek` | `ollama` |
| `AI_MODEL` | Modelo específico a usar | Según proveedor | `llama3:8b` |
| `AI_API_KEY` | API Key (solo OpenAI/DeepSeek) | String | - |
| `AI_BASE_URL` | URL base del servicio | URL | `http://localhost:11434` |
| `AI_TIMEOUT` | Timeout en segundos | Número | `120` |
| `KNOWLEDGE_BASE_PATH` | Ruta a la base de conocimiento | Path | `knowledge` |

### Uso del Sistema IA

1. Asegúrate de tener el proveedor de IA configurado y funcionando
2. Crea un documento y asócialo a uno o más controles SOA
3. En la vista del documento, haz clic en "Verificar con IA"
4. El sistema analizará el documento y generará un informe de cumplimiento

**El informe incluye:**
- Estado de cumplimiento (Cumple/Parcial/No cumple)
- Puntuación de 0-100
- Aspectos cubiertos del control
- Aspectos faltantes o insuficientes
- Citas del documento como evidencia
- Recomendaciones de mejora
- Sugerencia de nivel de madurez

### Troubleshooting

**Ollama no responde:**
```bash
# Verificar que Ollama está corriendo
systemctl status ollama  # Linux
# o
ollama serve  # Manual

# Verificar modelos instalados
ollama list
```

**Error de API Key (OpenAI/DeepSeek):**
- Verifica que el API Key es válido
- Asegúrate de tener créditos disponibles en tu cuenta

**Timeout en verificaciones:**
- Aumenta el valor de `AI_TIMEOUT`
- Usa un modelo más pequeño/rápido
- Verifica la carga del servidor de IA

## Configuración de Producción

1. Configura variables de entorno de producción
2. Usa un servidor web robusto (Nginx + Gunicorn)
3. Configura SSL/TLS
4. Implementa backups automáticos de la base de datos
5. Configura monitorización y logs

## Soporte

Para reportar problemas o sugerir mejoras, crea un issue en el repositorio del proyecto.

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo LICENSE para más detalles.