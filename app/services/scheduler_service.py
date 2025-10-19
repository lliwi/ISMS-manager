"""
Servicio de Scheduler para tareas automáticas
Gestiona la generación automática de tareas y envío de notificaciones
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import logging

from app.services.task_service import TaskService
from app.services.notification_service import NotificationService


# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskSchedulerService:
    """Servicio para programación de tareas automáticas"""

    def __init__(self, app=None):
        """
        Inicializa el scheduler

        Args:
            app: Instancia de Flask (opcional)
        """
        self.scheduler = BackgroundScheduler()
        self.app = app
        self.is_running = False

        if app:
            self.init_app(app)

    def init_app(self, app):
        """
        Inicializa el scheduler con la aplicación Flask

        Args:
            app: Instancia de Flask
        """
        self.app = app

        # Configurar jobs
        self._configure_jobs()

        # Iniciar scheduler si está configurado
        if app.config.get('TASK_AUTO_GENERATION_ENABLED', True):
            self.start()

    def _configure_jobs(self):
        """Configura todos los jobs programados"""

        # JOB 1: Generar tareas diarias desde plantillas - Todos los días a las 00:00
        self.scheduler.add_job(
            func=self._generate_tasks_job,
            trigger=CronTrigger(hour=0, minute=0),
            id='generate_daily_tasks',
            name='Generar tareas diarias desde plantillas',
            replace_existing=True,
            misfire_grace_time=3600  # 1 hora de gracia
        )
        logger.info("✅ Job configurado: Generación diaria de tareas (00:00)")

        # JOB 2: Actualizar tareas vencidas - Cada hora
        self.scheduler.add_job(
            func=self._update_overdue_tasks_job,
            trigger=IntervalTrigger(hours=1),
            id='update_overdue_tasks',
            name='Actualizar estado de tareas vencidas',
            replace_existing=True
        )
        logger.info("✅ Job configurado: Actualización de tareas vencidas (cada 1 hora)")

        # JOB 3: Procesar notificaciones pendientes - Cada 30 minutos
        self.scheduler.add_job(
            func=self._process_notifications_job,
            trigger=IntervalTrigger(minutes=30),
            id='process_notifications',
            name='Procesar notificaciones pendientes',
            replace_existing=True
        )
        logger.info("✅ Job configurado: Procesamiento de notificaciones (cada 30 minutos)")

        # JOB 4: Enviar resumen semanal - Lunes a las 09:00
        self.scheduler.add_job(
            func=self._send_weekly_summary_job,
            trigger=CronTrigger(day_of_week='mon', hour=9, minute=0),
            id='weekly_summary',
            name='Enviar resumen semanal de tareas',
            replace_existing=True,
            misfire_grace_time=3600
        )
        logger.info("✅ Job configurado: Resumen semanal (Lunes 09:00)")

        # JOB 5: Generar tareas mensuales - Día 1 de cada mes a las 00:00
        self.scheduler.add_job(
            func=self._generate_monthly_tasks_job,
            trigger=CronTrigger(day=1, hour=0, minute=0),
            id='generate_monthly_tasks',
            name='Generar tareas mensuales',
            replace_existing=True,
            misfire_grace_time=7200
        )
        logger.info("✅ Job configurado: Generación de tareas mensuales (día 1, 00:00)")

    def _generate_tasks_job(self):
        """Job: Generar tareas desde plantillas"""
        logger.info("🔄 Iniciando generación de tareas desde plantillas...")

        try:
            with self.app.app_context():
                generated_count = TaskService.generate_tasks_from_templates()
                logger.info(f"✅ Tareas generadas: {generated_count}")

                if generated_count > 0:
                    logger.info(f"📧 Se enviaron {generated_count} notificaciones de asignación")

        except Exception as e:
            logger.error(f"❌ Error generando tareas: {str(e)}")

    def _update_overdue_tasks_job(self):
        """Job: Actualizar tareas vencidas"""
        logger.info("🔄 Actualizando tareas vencidas...")

        try:
            with self.app.app_context():
                updated_count = TaskService.update_overdue_tasks()
                if updated_count > 0:
                    logger.info(f"✅ Tareas marcadas como vencidas: {updated_count}")

        except Exception as e:
            logger.error(f"❌ Error actualizando tareas vencidas: {str(e)}")

    def _process_notifications_job(self):
        """Job: Procesar notificaciones pendientes"""
        logger.info("🔄 Procesando notificaciones pendientes...")

        try:
            with self.app.app_context():
                result = NotificationService.process_pending_notifications()

                total_sent = result['reminders'] + result['overdue']
                if total_sent > 0:
                    logger.info(
                        f"✅ Notificaciones enviadas: "
                        f"{result['reminders']} recordatorios, "
                        f"{result['overdue']} vencidas"
                    )
                    if result['errors'] > 0:
                        logger.warning(f"⚠️  Errores en notificaciones: {result['errors']}")

        except Exception as e:
            logger.error(f"❌ Error procesando notificaciones: {str(e)}")

    def _send_weekly_summary_job(self):
        """Job: Enviar resumen semanal a todos los usuarios activos"""
        logger.info("🔄 Enviando resumen semanal de tareas...")

        try:
            with self.app.app_context():
                from models import User

                # Obtener todos los usuarios activos
                users = User.query.filter_by(is_active=True).all()

                sent_count = 0
                for user in users:
                    try:
                        # Solo enviar si el usuario tiene tareas asignadas
                        pending = TaskService.get_pending_tasks(user_id=user.id)
                        overdue = TaskService.get_overdue_tasks(user_id=user.id)

                        if pending or overdue:
                            NotificationService.send_weekly_summary(user)
                            sent_count += 1

                    except Exception as e:
                        logger.error(f"❌ Error enviando resumen a {user.username}: {str(e)}")
                        continue

                logger.info(f"✅ Resúmenes semanales enviados: {sent_count}")

        except Exception as e:
            logger.error(f"❌ Error en envío de resúmenes semanales: {str(e)}")

    def _generate_monthly_tasks_job(self):
        """Job: Generar tareas mensuales (primero de cada mes)"""
        logger.info("🔄 Generando tareas mensuales (inicio de mes)...")

        try:
            with self.app.app_context():
                # Forzar generación de tareas mensuales
                generated_count = TaskService.generate_tasks_from_templates(force=False)
                logger.info(f"✅ Tareas mensuales generadas: {generated_count}")

        except Exception as e:
            logger.error(f"❌ Error generando tareas mensuales: {str(e)}")

    def start(self):
        """Inicia el scheduler"""
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            logger.info("🚀 Scheduler de tareas iniciado correctamente")
            logger.info(f"📅 Jobs programados: {len(self.scheduler.get_jobs())}")

            # Mostrar próximas ejecuciones
            self._print_next_runs()

    def stop(self):
        """Detiene el scheduler"""
        if self.is_running:
            self.scheduler.shutdown(wait=False)
            self.is_running = False
            logger.info("⏹️  Scheduler de tareas detenido")

    def _print_next_runs(self):
        """Muestra las próximas ejecuciones programadas"""
        logger.info("\n📋 Próximas ejecuciones programadas:")
        for job in self.scheduler.get_jobs():
            next_run = job.next_run_time
            if next_run:
                logger.info(f"   • {job.name}: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")

    def get_job_status(self):
        """
        Obtiene el estado de todos los jobs

        Returns:
            dict: Estado de los jobs
        """
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            })

        return {
            'is_running': self.is_running,
            'jobs_count': len(jobs),
            'jobs': jobs
        }

    def run_job_now(self, job_id):
        """
        Ejecuta un job inmediatamente (útil para pruebas)

        Args:
            job_id: ID del job a ejecutar
        """
        job = self.scheduler.get_job(job_id)
        if job:
            logger.info(f"▶️  Ejecutando job manualmente: {job.name}")
            job.func()
            logger.info(f"✅ Job ejecutado: {job.name}")
        else:
            logger.error(f"❌ Job no encontrado: {job_id}")


# Instancia global del scheduler
task_scheduler = TaskSchedulerService()


# Funciones de conveniencia
def init_scheduler(app):
    """
    Inicializa el scheduler con la aplicación Flask

    Args:
        app: Instancia de Flask
    """
    task_scheduler.init_app(app)
    return task_scheduler


def get_scheduler():
    """
    Obtiene la instancia del scheduler

    Returns:
        TaskSchedulerService: Instancia del scheduler
    """
    return task_scheduler
