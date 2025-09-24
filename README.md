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