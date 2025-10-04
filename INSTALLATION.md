# Guía de Instalación - ISMS Manager

Esta guía cubre la instalación completa del sistema ISMS Manager tanto para nuevas instalaciones como para actualizar instalaciones existentes.

## Requisitos Previos

- Docker y Docker Compose instalados
- Python 3.11+ (para desarrollo local)
- PostgreSQL 15+ (si no usas Docker)
- Git

## Instalación para Nuevas Instalaciones

### 1. Clonar el Repositorio

```bash
git clone <repository-url>
cd "ISMS Manager"
```

### 2. Configurar Variables de Entorno

Copiar el archivo de ejemplo y ajustar las variables:

```bash
cp .env.example .env
```

**Editar `.env` y configurar:**

```bash
# IMPORTANTE: Cambiar SECRET_KEY en producción
SECRET_KEY=tu-clave-secreta-muy-larga-y-aleatoria-aqui

# Base de datos
DATABASE_URL=postgresql://isms:tu_password_segura@db:5432/isms_db

# Entorno
FLASK_ENV=production  # o development para desarrollo

# Sesiones (configurar para HTTPS en producción)
SESSION_COOKIE_SECURE=True
PERMANENT_SESSION_LIFETIME=1800  # 30 minutos
```

### 3. Iniciar con Docker Compose

```bash
docker-compose up -d
```

Esto creará automáticamente:
- ✅ Base de datos PostgreSQL
- ✅ Servidor web con Gunicorn
- ✅ Nginx como reverse proxy
- ✅ Redis para caché/sesiones
- ✅ Tablas de base de datos
- ✅ Roles por defecto (admin, ciso, auditor, owner, user)
- ✅ Usuario administrador inicial

### 4. Verificar la Instalación

Acceder a: `http://localhost` o `https://localhost`

**Credenciales por defecto:**
- Usuario: `admin`
- Contraseña: `admin123`

⚠️ **IMPORTANTE**: El sistema forzará el cambio de contraseña en el primer login.

### 5. Primer Login

1. Acceder con las credenciales por defecto
2. El sistema te pedirá cambiar la contraseña
3. Usar una contraseña que cumpla con los requisitos:
   - Mínimo 8 caracteres
   - Al menos 1 mayúscula
   - Al menos 1 minúscula
   - Al menos 1 número
   - Al menos 1 carácter especial

## Actualización de Instalaciones Existentes

Si ya tienes una instalación previa y necesitas actualizar a la versión con las nuevas funciones de seguridad:

### Opción A: Actualización Automática con Docker

```bash
# Detener contenedores
docker-compose down

# Actualizar código
git pull

# Copiar script de migración al contenedor
docker-compose up -d
docker cp run_migration.py ismsmanager-web-1:/app/run_migration.py

# Ejecutar migración
docker exec ismsmanager-web-1 python run_migration.py

# Reiniciar contenedores
docker-compose restart web
```

### Opción B: Migración Manual (sin Docker)

```bash
# Activar entorno virtual
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Ejecutar script de migración
python run_migration.py

# Reiniciar aplicación
```

### Verificar Migración Exitosa

```bash
# Conectar a la base de datos
docker exec -it ismsmanager-db-1 psql -U isms -d isms_db

# Verificar columnas nuevas
\d users
\d audit_logs

# Debería mostrar todas las columnas de seguridad
```

## Estructura de Usuarios y Roles

El sistema crea automáticamente 5 roles con diferentes permisos:

| Rol | Código | Descripción | Permisos |
|-----|--------|-------------|----------|
| Administrador | `admin` | Control total del sistema | Todos los módulos + gestión de usuarios |
| CISO | `ciso` | Responsable de Seguridad | Todos los módulos + aprobaciones |
| Auditor | `auditor` | Auditor Interno | Auditorías + lectura en otros módulos |
| Propietario | `owner` | Dueño de Proceso | Módulos asignados |
| Usuario | `user` | Usuario General | Dashboard + Incidentes + Documentos |

## Características de Seguridad Implementadas

✅ **Autenticación y Contraseñas:**
- Hash PBKDF2-SHA256 con salt de 16 bytes
- Validación de complejidad obligatoria
- Prevención de contraseñas comunes
- Expiración automática a los 90 días
- Historial para prevenir reutilización

✅ **Protección de Cuentas:**
- Bloqueo automático tras 5 intentos fallidos (30 minutos)
- Desbloqueo manual por administrador
- Tracking de IP y user agent
- Forzar cambio de contraseña en primer login

✅ **Auditoría Completa:**
- Registro de todos los cambios en usuarios
- Logs de login exitoso/fallido
- Tracking de todas las acciones
- Almacenamiento de valores antiguos/nuevos
- Retención con índices optimizados

✅ **Control de Acceso:**
- RBAC (Role-Based Access Control)
- Decoradores `@role_required`
- Verificación por módulo
- Protección CSRF habilitada
- HttpOnly cookies

## Configuración de Seguridad Recomendada

### Producción

```env
# .env para producción
FLASK_ENV=production
SECRET_KEY=<generar-con-secrets.token_hex(32)>
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
PERMANENT_SESSION_LIFETIME=1800  # 30 minutos

# HTTPS obligatorio
# Configurar certificados SSL en nginx
```

### Generar SECRET_KEY Segura

```python
import secrets
print(secrets.token_hex(32))
```

Copiar el resultado a `.env`:

```env
SECRET_KEY=a1b2c3d4e5f6...
```

## Tareas Post-Instalación

### 1. Crear Usuarios Adicionales

1. Login como admin
2. Ir a `/admin/users`
3. Click en "Nuevo Usuario"
4. Llenar formulario
5. Asignar rol apropiado
6. Marcar "Debe cambiar contraseña en primer login"

### 2. Configurar Notificaciones por Email (Opcional)

Editar `.env`:

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu-email@gmail.com
MAIL_PASSWORD=tu-password-de-aplicacion
```

### 3. Revisar Logs de Auditoría

Acceder a `/admin/audit-logs` para ver:
- Intentos de login
- Cambios en usuarios
- Acciones del sistema

### 4. Configurar Backups Automáticos

```bash
# Ejemplo de script de backup
docker exec ismsmanager-db-1 pg_dump -U isms isms_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Agregar a crontab para ejecutar diariamente
0 2 * * * /ruta/al/script/backup.sh
```

## Solución de Problemas

### Error: "column users.phone does not exist"

Ejecutar migración:

```bash
docker cp run_migration.py ismsmanager-web-1:/app/
docker exec ismsmanager-web-1 python run_migration.py
docker-compose restart web
```

### Error: "SECRET_KEY not set"

Generar y agregar SECRET_KEY a `.env`

### No puedo acceder a /admin/users

Verificar que tu usuario tenga rol `admin` o `ciso`:

```sql
-- Conectar a DB
docker exec -it ismsmanager-db-1 psql -U isms -d isms_db

-- Ver usuarios y roles
SELECT u.username, r.name
FROM users u
JOIN roles r ON u.role_id = r.id;

-- Cambiar rol de un usuario
UPDATE users SET role_id = (SELECT id FROM roles WHERE name = 'admin')
WHERE username = 'tu_usuario';
```

### Cuenta bloqueada

Un administrador puede desbloquear desde:
`/admin/users/<user_id>` → Botón "Desbloquear Cuenta"

## Mantenimiento

### Ver Logs de la Aplicación

```bash
docker-compose logs -f web
```

### Ver Logs de Auditoría

Acceder a `/admin/audit-logs` en la aplicación

### Limpiar Logs Antiguos (opcional)

```sql
-- Eliminar logs de auditoría mayores a 1 año
DELETE FROM audit_logs
WHERE created_at < NOW() - INTERVAL '1 year';
```

## Arquitectura de Seguridad

```
┌─────────────────────────────────────────┐
│         Usuario / Navegador             │
└────────────────┬────────────────────────┘
                 │ HTTPS
┌────────────────▼────────────────────────┐
│         Nginx (Reverse Proxy)           │
│  - SSL/TLS                              │
│  - Rate Limiting                        │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│      Flask App (Gunicorn)               │
│  - CSRF Protection                      │
│  - Session Management                   │
│  - Role-Based Access Control            │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│         PostgreSQL Database             │
│  - Encrypted passwords (PBKDF2-SHA256)  │
│  - Audit logs                           │
│  - Foreign key constraints              │
└─────────────────────────────────────────┘
```

## Contacto y Soporte

Para reportar problemas de seguridad, contactar al equipo de desarrollo.

## Changelog de Seguridad

### Versión 1.1.0 (2025-10-04)

- ✅ Agregados campos de seguridad al modelo User
- ✅ Implementado bloqueo automático de cuentas
- ✅ Implementada expiración de contraseñas (90 días)
- ✅ Sistema completo de auditoría (AuditLog)
- ✅ Validadores de complejidad de contraseñas
- ✅ Control de acceso mejorado con decoradores
- ✅ Tracking de IP y user agent
- ✅ Gestión completa de usuarios (/admin/users)
