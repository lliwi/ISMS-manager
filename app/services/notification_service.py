"""
Servicio de Notificaciones por Email
Gestiona el envío de notificaciones automáticas para tareas
"""
from datetime import datetime
from flask import current_app, render_template, url_for
from flask_mail import Mail, Message
from models import db
from app.models.task import Task, TaskNotificationLog, PeriodicTaskStatus


# Inicializar Flask-Mail
mail = Mail()


class NotificationService:
    """Servicio para envío de notificaciones de tareas"""

    @staticmethod
    def send_task_assignment_notification(task):
        """
        Envía notificación de asignación de tarea

        Args:
            task: Instancia de Task
        """
        if not task.assigned_to:
            return False

        subject = f"Nueva Tarea Asignada: {task.title}"

        html_body = render_template(
            'emails/task_assigned.html',
            task=task,
            user=task.assigned_to,
            task_url=url_for('tasks.view', id=task.id, _external=True)
        )

        text_body = f"""
Hola {task.assigned_to.first_name or task.assigned_to.username},

Se te ha asignado una nueva tarea en el Sistema de Gestión de Seguridad de la Información:

Tarea: {task.title}
Categoría: {task.category.value}
Prioridad: {task.priority.value}
Vencimiento: {task.due_date.strftime('%d/%m/%Y %H:%M')}
Control ISO: {task.iso_control or 'N/A'}

Descripción:
{task.description or 'Sin descripción'}

Por favor, accede al sistema para ver los detalles completos:
{url_for('tasks.view', id=task.id, _external=True)}

---
Sistema de Gestión de Seguridad de la Información
ISO/IEC 27001:2023
        """

        return NotificationService._send_email(
            recipient=task.assigned_to.email,
            subject=subject,
            text_body=text_body,
            html_body=html_body,
            task_id=task.id,
            notification_type='assigned'
        )

    @staticmethod
    def send_task_reminder(task, days_until_due):
        """
        Envía recordatorio de tarea próxima a vencer

        Args:
            task: Instancia de Task
            days_until_due: Días hasta el vencimiento
        """
        if not task.assigned_to:
            return False

        if days_until_due == 0:
            urgency = "VENCE HOY"
            subject = f"⚠️ URGENTE: Tarea vence hoy - {task.title}"
        elif days_until_due == 1:
            urgency = "vence mañana"
            subject = f"Recordatorio: Tarea vence mañana - {task.title}"
        else:
            urgency = f"vence en {days_until_due} días"
            subject = f"Recordatorio: Tarea {urgency} - {task.title}"

        html_body = render_template(
            'emails/task_reminder.html',
            task=task,
            user=task.assigned_to,
            days_until_due=days_until_due,
            urgency=urgency,
            task_url=url_for('tasks.view', id=task.id, _external=True)
        )

        text_body = f"""
Hola {task.assigned_to.first_name or task.assigned_to.username},

Tienes una tarea pendiente que {urgency}:

Tarea: {task.title}
Categoría: {task.category.value}
Prioridad: {task.priority.value}
Vencimiento: {task.due_date.strftime('%d/%m/%Y %H:%M')}
Días restantes: {days_until_due}

Progreso actual: {task.progress}%

Descripción:
{task.description or 'Sin descripción'}

Por favor, accede al sistema para completar esta tarea:
{url_for('tasks.view', id=task.id, _external=True)}

---
Sistema de Gestión de Seguridad de la Información
ISO/IEC 27001:2023
        """

        return NotificationService._send_email(
            recipient=task.assigned_to.email,
            subject=subject,
            text_body=text_body,
            html_body=html_body,
            task_id=task.id,
            notification_type='reminder'
        )

    @staticmethod
    def send_task_overdue_notification(task):
        """
        Envía notificación de tarea vencida

        Args:
            task: Instancia de Task
        """
        if not task.assigned_to:
            return False

        days_overdue = abs(task.days_until_due)

        subject = f"🔴 TAREA VENCIDA: {task.title}"

        html_body = render_template(
            'emails/task_overdue.html',
            task=task,
            user=task.assigned_to,
            days_overdue=days_overdue,
            task_url=url_for('tasks.view', id=task.id, _external=True)
        )

        text_body = f"""
Hola {task.assigned_to.first_name or task.assigned_to.username},

ATENCIÓN: Tienes una tarea VENCIDA en el SGSI:

Tarea: {task.title}
Categoría: {task.category.value}
Prioridad: {task.priority.value}
Venció el: {task.due_date.strftime('%d/%m/%Y %H:%M')}
Días de retraso: {days_overdue}

Estado: {task.status.value}
Progreso: {task.progress}%

Esta tarea requiere atención inmediata. Por favor, complétala lo antes posible o contacta con tu supervisor.

Accede al sistema para más detalles:
{url_for('tasks.view', id=task.id, _external=True)}

---
Sistema de Gestión de Seguridad de la Información
ISO/IEC 27001:2023
        """

        # También notificar al supervisor/creador
        cc_emails = []
        if task.created_by and task.created_by.email != task.assigned_to.email:
            cc_emails.append(task.created_by.email)

        return NotificationService._send_email(
            recipient=task.assigned_to.email,
            subject=subject,
            text_body=text_body,
            html_body=html_body,
            task_id=task.id,
            notification_type='overdue',
            cc=cc_emails
        )

    @staticmethod
    def send_task_completed_notification(task):
        """
        Envía notificación de tarea completada

        Args:
            task: Instancia de Task
        """
        recipients = []

        # Notificar al creador
        if task.created_by:
            recipients.append(task.created_by.email)

        # Si requiere aprobación, notificar al aprobador
        if task.requires_approval and task.approved_by:
            recipients.append(task.approved_by.email)

        if not recipients:
            return False

        subject = f"✓ Tarea Completada: {task.title}"

        html_body = render_template(
            'emails/task_completed.html',
            task=task,
            task_url=url_for('tasks.view', id=task.id, _external=True)
        )

        text_body = f"""
Se ha completado la siguiente tarea del SGSI:

Tarea: {task.title}
Categoría: {task.category.value}
Completada por: {task.updated_by.username if task.updated_by else 'N/A'}
Fecha de completado: {task.completion_date.strftime('%d/%m/%Y %H:%M') if task.completion_date else 'N/A'}

Resultado:
{task.result or 'Sin resultado documentado'}

Observaciones:
{task.observations or 'Sin observaciones'}

{'Esta tarea requiere aprobación antes de cerrarse.' if task.requires_approval else ''}

Ver detalles:
{url_for('tasks.view', id=task.id, _external=True)}

---
Sistema de Gestión de Seguridad de la Información
ISO/IEC 27001:2023
        """

        success = True
        for recipient in recipients:
            result = NotificationService._send_email(
                recipient=recipient,
                subject=subject,
                text_body=text_body,
                html_body=html_body,
                task_id=task.id,
                notification_type='completed'
            )
            success = success and result

        return success

    @staticmethod
    def send_weekly_summary(user):
        """
        Envía resumen semanal de tareas a un usuario

        Args:
            user: Instancia de User
        """
        from app.services.task_service import TaskService

        pending_tasks = TaskService.get_pending_tasks(user_id=user.id)
        overdue_tasks = TaskService.get_overdue_tasks(user_id=user.id)
        due_soon = TaskService.get_tasks_due_soon(days=7, user_id=user.id)

        subject = f"Resumen Semanal de Tareas - {datetime.now().strftime('%d/%m/%Y')}"

        html_body = render_template(
            'emails/weekly_summary.html',
            user=user,
            pending_tasks=pending_tasks,
            overdue_tasks=overdue_tasks,
            due_soon=due_soon,
            dashboard_url=url_for('tasks.dashboard', _external=True)
        )

        text_body = f"""
Hola {user.first_name or user.username},

Este es tu resumen semanal de tareas del SGSI:

TAREAS VENCIDAS: {len(overdue_tasks)}
{chr(10).join([f'  - {t.title} (venció {t.due_date.strftime("%d/%m/%Y")})' for t in overdue_tasks[:5]])}

TAREAS QUE VENCEN PRÓXIMAMENTE (7 días): {len(due_soon)}
{chr(10).join([f'  - {t.title} (vence {t.due_date.strftime("%d/%m/%Y")})' for t in due_soon[:5]])}

TAREAS PENDIENTES: {len(pending_tasks)}

Accede al dashboard para ver todas tus tareas:
{url_for('tasks.dashboard', _external=True)}

---
Sistema de Gestión de Seguridad de la Información
ISO/IEC 27001:2023
        """

        return NotificationService._send_email(
            recipient=user.email,
            subject=subject,
            text_body=text_body,
            html_body=html_body,
            task_id=None,
            notification_type='weekly_summary'
        )

    @staticmethod
    def process_pending_notifications():
        """
        Procesa todas las notificaciones pendientes
        Debe ejecutarse periódicamente (cada 30 minutos)

        Returns:
            dict: Resumen de notificaciones enviadas
        """
        from app.services.task_service import TaskService

        sent_count = {
            'reminders': 0,
            'overdue': 0,
            'errors': 0
        }

        # Obtener todas las tareas activas
        active_tasks = Task.query.filter(
            Task.status.in_([PeriodicTaskStatus.PENDIENTE, PeriodicTaskStatus.EN_PROGRESO, PeriodicTaskStatus.VENCIDA])
        ).all()

        for task in active_tasks:
            try:
                # Verificar si debe enviarse notificación
                if task.should_send_notification():
                    if task.is_overdue:
                        # Tarea vencida
                        NotificationService.send_task_overdue_notification(task)
                        sent_count['overdue'] += 1
                    else:
                        # Recordatorio normal
                        days_until = task.days_until_due
                        NotificationService.send_task_reminder(task, days_until)
                        sent_count['reminders'] += 1

                    # Actualizar timestamp de última notificación
                    task.last_notification_sent = datetime.utcnow()
                    task.notification_count += 1
                    db.session.commit()

            except Exception as e:
                print(f"Error enviando notificación para tarea {task.id}: {e}")
                sent_count['errors'] += 1
                continue

        return sent_count

    @staticmethod
    def _send_email(recipient, subject, text_body, html_body=None, task_id=None, notification_type='general', cc=None):
        """
        Envía un email y registra el envío

        Args:
            recipient: Email del destinatario
            subject: Asunto del email
            text_body: Cuerpo en texto plano
            html_body: Cuerpo en HTML (opcional)
            task_id: ID de la tarea relacionada
            notification_type: Tipo de notificación
            cc: Lista de emails en copia (opcional)

        Returns:
            bool: True si se envió correctamente
        """
        # Verificar si las notificaciones están habilitadas
        if not current_app.config.get('TASK_NOTIFICATION_ENABLED', True):
            print(f"Notificaciones deshabilitadas - no se envía: {subject}")
            return False

        try:
            msg = Message(
                subject=subject,
                recipients=[recipient],
                body=text_body,
                html=html_body,
                sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'sgsi@empresa.com')
            )

            if cc:
                msg.cc = cc

            mail.send(msg)

            # Registrar envío exitoso
            if task_id:
                log = TaskNotificationLog(
                    task_id=task_id,
                    recipient_email=recipient,
                    notification_type=notification_type,
                    subject=subject,
                    body=text_body[:500],  # Primeros 500 caracteres
                    was_successful=True
                )
                db.session.add(log)
                db.session.commit()

            return True

        except Exception as e:
            error_msg = str(e)
            print(f"Error enviando email a {recipient}: {error_msg}")

            # Registrar error
            if task_id:
                log = TaskNotificationLog(
                    task_id=task_id,
                    recipient_email=recipient,
                    notification_type=notification_type,
                    subject=subject,
                    body=text_body[:500],
                    was_successful=False,
                    error_message=error_msg
                )
                db.session.add(log)
                db.session.commit()

            return False
