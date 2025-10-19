# Guía de Instalación: Módulo de Gestión de Tareas

## Para Nuevas Instalaciones

Esta guía explica cómo instalar el módulo de Gestión de Tareas en una instalación nueva del ISMS Manager.

### Prerrequisitos

- Docker y Docker Compose instalados
- PostgreSQL 13+
- Python 3.11+
- Git (opcional)

### Paso 1: Clonar o Preparar el Proyecto

```bash
# Si es una nueva instalación
cd /ruta/al/proyecto
```

### Paso 2: Configurar Variables de Entorno

Crear o editar el archivo `.env`:

```bash
# Base de datos
DATABASE_URL=postgresql://isms:isms_secure_password@db:5432/isms_db

# Email (MailHog para desarrollo)
MAIL_SERVER=mailhog
MAIL_PORT=1025
MAIL_USE_TLS=False
MAIL_USE_SSL=False
MAIL_DEFAULT_SENDER=sgsi@empresa.com
MAIL_MAX_EMAILS=100

# Gestión de Tareas
TASK_AUTO_GENERATION_ENABLED=True
TASK_NOTIFICATION_ENABLED=True

# Aplicación
FLASK_ENV=development
SECRET_KEY=tu-clave-secreta-aqui-cambiar-en-produccion
```

### Paso 3: Iniciar Servicios Docker

```bash
docker-compose up -d
```

Esto iniciará:
- PostgreSQL (base de datos)
- Flask Web Application
- MailHog (servidor SMTP de prueba)

### Paso 4: Verificar que los Contenedores Estén Corriendo

```bash
docker-compose ps
```

Deberías ver algo como:

```
NAME                    STATUS              PORTS
ismsmanager-db-1        running             5432/tcp
ismsmanager-web-1       running             0.0.0.0:5000->5000/tcp
ismsmanager-mailhog-1   running             0.0.0.0:1025->1025/tcp, 0.0.0.0:8025->8025/tcp
```

### Paso 5: Aplicar Migraciones de Base de Datos

```bash
# Aplicar todas las migraciones (incluida la de tareas)
docker-compose exec web flask db upgrade
```

**Verificar que la migración se aplicó:**

```bash
docker-compose exec db psql -U isms -d isms_db -c "\dt task*"
```

Deberías ver 6 tablas:
- `task_templates`
- `tasks`
- `task_evidences`
- `task_comments`
- `task_history`
- `task_notification_logs`

### Paso 6: Inicializar Plantillas de Tareas

```bash
# Copiar script de inicialización al contenedor
docker cp init_tasks_module.py ismsmanager-web-1:/app/init_tasks_module.py

# Ejecutar script de inicialización
docker-compose exec web python init_tasks_module.py
```

Deberías ver:

```
🚀 Iniciando creación de plantillas de tareas ISO 27001...
✅ Creada: 'Revisión Trimestral de Controles de Seguridad'
✅ Creada: 'Auditoría Interna del SGSI - Semestral'
...
🎉 Proceso completado!
📊 Plantillas creadas: 15
```

### Paso 7: Verificar la Instalación

**7.1. Verificar Scheduler:**

```bash
docker-compose logs web | grep -i scheduler
```

Deberías ver:

```
INFO:apscheduler.scheduler:Scheduler started
INFO:app.services.scheduler_service:🚀 Scheduler de tareas iniciado correctamente
INFO:app.services.scheduler_service:📅 Jobs programados: 5
```

**7.2. Verificar Salud del Servicio:**

```bash
curl http://localhost:5000/health
```

Respuesta esperada:

```json
{"status":"healthy","timestamp":"2025-10-19T..."}
```

**7.3. Acceder a la Aplicación:**

Abrir navegador en: `http://localhost/tareas`

Credenciales por defecto:
- **Usuario:** `admin`
- **Contraseña:** `admin123`

**7.4. Verificar MailHog:**

Abrir navegador en: `http://localhost:8025`

Aquí verás todos los emails de notificación enviados.

### Paso 8: Crear Usuarios Adicionales (Opcional)

```bash
docker-compose exec web flask shell
```

```python
from models import db, User, Role
from datetime import datetime

# Crear usuario CISO
role_ciso = Role.query.filter_by(name='ciso').first()
ciso_user = User(
    username='ciso',
    email='ciso@empresa.com',
    first_name='Responsable',
    last_name='de Seguridad',
    role_id=role_ciso.id,
    is_active=True
)
ciso_user.set_password('ciso123')
db.session.add(ciso_user)

# Crear usuario Auditor
role_auditor = Role.query.filter_by(name='auditor').first()
auditor_user = User(
    username='auditor',
    email='auditor@empresa.com',
    first_name='Auditor',
    last_name='Interno',
    role_id=role_auditor.id,
    is_active=True
)
auditor_user.set_password('auditor123')
db.session.add(auditor_user)

db.session.commit()
exit()
```

## Verificación Post-Instalación

### Checklist de Verificación

- [ ] Base de datos creada y migraciones aplicadas
- [ ] 6 tablas de tareas creadas (`task*`)
- [ ] 15 plantillas de tareas iniciales cargadas
- [ ] Scheduler iniciado con 5 jobs programados
- [ ] Flask-Mail configurado
- [ ] MailHog accesible en puerto 8025
- [ ] Endpoint `/tareas` accesible
- [ ] No hay errores en logs
- [ ] Usuario admin puede acceder

### Verificar Plantillas

```bash
docker-compose exec db psql -U isms -d isms_db -c "SELECT id, title, frequency, priority FROM task_templates LIMIT 5;"
```

### Verificar Jobs del Scheduler

```bash
docker-compose logs web 2>&1 | grep "Job configurado"
```

Deberías ver 5 jobs:
1. Generación diaria de tareas
2. Actualización de tareas vencidas
3. Procesamiento de notificaciones
4. Resumen semanal
5. Generación de tareas mensuales

## Solución de Problemas

### Problema: Tablas no se crearon

**Solución:**

```bash
# Verificar estado de migraciones
docker-compose exec web flask db current

# Si está en versión anterior a 009, aplicar:
docker-compose exec web flask db upgrade
```

### Problema: No hay plantillas de tareas

**Solución:**

```bash
# Ejecutar script de inicialización nuevamente
docker cp init_tasks_module.py ismsmanager-web-1:/app/init_tasks_module.py
docker-compose exec web python init_tasks_module.py
```

### Problema: Scheduler no inicia

**Solución:**

```bash
# Verificar que APScheduler esté instalado
docker-compose exec web pip list | grep APScheduler

# Si no está instalado:
docker-compose exec web pip install apscheduler

# Reiniciar contenedor
docker-compose restart web
```

### Problema: Error al acceder a /tareas

**Error común:** `column tasks.template_id does not exist`

**Solución:**

```bash
# Drop y recrear tabla tasks
docker-compose exec db psql -U isms -d isms_db -c "DROP TABLE IF EXISTS tasks CASCADE;"

# Volver a aplicar migración
docker-compose exec web flask db upgrade

# Reiniciar
docker-compose restart web
```

### Problema: No se envían emails

**Verificación:**

```bash
# Verificar que MailHog esté corriendo
docker-compose ps mailhog

# Verificar configuración de email
docker-compose exec web python -c "from application import app; print(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])"
```

Debería mostrar: `mailhog 1025`

## Configuración de Producción

### Variables de Entorno para Producción

```bash
# Email SMTP real
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu-email@empresa.com
MAIL_PASSWORD=tu-contraseña-app
MAIL_DEFAULT_SENDER=sgsi@empresa.com

# Seguridad
SECRET_KEY=clave-super-secreta-aleatoria-de-produccion
SESSION_COOKIE_SECURE=True

# Base de datos
DATABASE_URL=postgresql://usuario:contraseña@servidor:5432/base_datos

# Aplicación
FLASK_ENV=production
```

### Recomendaciones de Producción

1. **Usar servidor SMTP real** (Gmail, SendGrid, Mailgun, etc.)
2. **Cambiar SECRET_KEY** a valor aleatorio seguro
3. **Habilitar HTTPS** para cookies seguras
4. **Configurar backups** de base de datos
5. **Monitorizar logs** del scheduler
6. **Configurar alertas** para errores críticos
7. **Limitar acceso** a MailHog o deshabilitarlo

## Actualización desde Versión Anterior

Si ya tienes el ISMS Manager instalado y quieres agregar el módulo de tareas:

```bash
# 1. Detener servicios
docker-compose down

# 2. Actualizar código fuente
git pull origin main

# 3. Iniciar servicios
docker-compose up -d

# 4. Aplicar nueva migración
docker-compose exec web flask db upgrade

# 5. Instalar dependencias nuevas
docker-compose exec web pip install apscheduler flask-mail

# 6. Inicializar plantillas
docker cp init_tasks_module.py ismsmanager-web-1:/app/init_tasks_module.py
docker-compose exec web python init_tasks_module.py

# 7. Reiniciar
docker-compose restart web
```

## Comandos Útiles

### Ver Tareas en Base de Datos

```bash
docker-compose exec db psql -U isms -d isms_db -c "SELECT id, title, status, due_date FROM tasks ORDER BY due_date;"
```

### Ver Próximas Ejecuciones del Scheduler

```bash
docker-compose logs web 2>&1 | grep "Próximas ejecuciones"
```

### Generar Tareas Manualmente

```bash
docker-compose exec web python -c "
from application import app
from app.services.task_service import TaskService
with app.app_context():
    result = TaskService.generate_tasks_from_templates()
    print(f'Tareas generadas: {result}')
"
```

### Enviar Notificaciones Pendientes Manualmente

```bash
docker-compose exec web python -c "
from application import app
from app.services.notification_service import NotificationService
with app.app_context():
    result = NotificationService.process_pending_notifications()
    print(f'Notificaciones enviadas: {result}')
"
```

## Soporte

Para más información:

- **Documentación Técnica:** `docs/IMPLEMENTACION_COMPLETADA_TAREAS.md`
- **Guía de Usuario:** `docs/GUIA_USO_TAREAS.md`
- **Logs:** `docker-compose logs web -f`
- **Reportar Issues:** GitHub o contacto del proyecto

---

**Versión:** 1.0.0
**Última Actualización:** Octubre 2025
