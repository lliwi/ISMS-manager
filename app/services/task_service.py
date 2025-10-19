"""
Servicio de Lógica de Negocio para Gestión de Tareas
Implementa la lógica de negocio del módulo de tareas ISO 27001
"""
from datetime import datetime, timedelta
from sqlalchemy import and_, or_, func
from models import db
from app.models.task import (
    TaskTemplate, Task, TaskEvidence, TaskComment,
    TaskHistory, TaskNotificationLog,
    TaskStatus, TaskPriority, TaskCategory, TaskFrequency
)


class TaskService:
    """Servicio para gestión de tareas"""

    @staticmethod
    def create_task_from_template(template_id, user_id, due_date=None):
        """
        Crea una instancia de tarea desde una plantilla

        Args:
            template_id: ID de la plantilla
            user_id: ID del usuario que crea la tarea
            due_date: Fecha de vencimiento (opcional, se calcula automáticamente)

        Returns:
            Task: Instancia de tarea creada
        """
        template = TaskTemplate.query.get(template_id)
        if not template:
            raise ValueError(f"Plantilla {template_id} no encontrada")

        if not template.is_active:
            raise ValueError(f"Plantilla {template_id} está inactiva")

        # Calcular fecha de vencimiento
        if due_date is None:
            due_date = template.calculate_next_due_date()

        # Determinar asignado: si la plantilla no tiene asignado, asignar al creador
        assigned_to_id = template.default_assignee_id if template.default_assignee_id else user_id

        # Crear tarea
        task = Task(
            template_id=template.id,
            title=template.title,
            description=template.description,
            category=template.category,
            priority=template.priority,
            due_date=due_date,
            assigned_to_id=assigned_to_id,
            assigned_role_id=template.default_role_id,
            iso_control=template.iso_control,
            estimated_hours=template.estimated_hours,
            requires_approval=template.requires_approval,
            checklist=template.checklist_template,
            created_by_id=user_id
        )

        db.session.add(task)

        # Crear registro de historial
        history = TaskHistory(
            task=task,
            user_id=user_id,
            action='created',
            details=f'Tarea creada desde plantilla "{template.title}"'
        )
        db.session.add(history)

        db.session.commit()

        return task

    @staticmethod
    def create_manual_task(data, user_id):
        """
        Crea una tarea manualmente (sin plantilla)

        Args:
            data: Diccionario con datos de la tarea
            user_id: ID del usuario creador

        Returns:
            Task: Instancia de tarea creada
        """
        task = Task(
            title=data.get('title'),
            description=data.get('description'),
            category=data.get('category'),
            priority=data.get('priority', TaskPriority.MEDIA),
            due_date=data.get('due_date'),
            assigned_to_id=data.get('assigned_to_id'),
            assigned_role_id=data.get('assigned_role_id'),
            iso_control=data.get('iso_control'),
            estimated_hours=data.get('estimated_hours'),
            requires_approval=data.get('requires_approval', False),
            checklist=data.get('checklist'),
            created_by_id=user_id
        )

        db.session.add(task)

        # Crear historial
        history = TaskHistory(
            task=task,
            user_id=user_id,
            action='created',
            details='Tarea creada manualmente'
        )
        db.session.add(history)

        db.session.commit()

        return task

    @staticmethod
    def assign_task(task_id, assigned_to_id, user_id):
        """
        Asigna una tarea a un usuario

        Args:
            task_id: ID de la tarea
            assigned_to_id: ID del usuario asignado
            user_id: ID del usuario que asigna
        """
        task = Task.query.get(task_id)
        if not task:
            raise ValueError(f"Tarea {task_id} no encontrada")

        old_assignee = task.assigned_to_id
        task.assigned_to_id = assigned_to_id
        task.updated_by_id = user_id

        # Registrar en historial
        from models import User
        new_user = User.query.get(assigned_to_id)
        history = TaskHistory(
            task_id=task.id,
            user_id=user_id,
            action='assigned',
            old_value=str(old_assignee) if old_assignee else None,
            new_value=str(assigned_to_id),
            details=f'Tarea asignada a {new_user.username if new_user else "N/A"}'
        )
        db.session.add(history)

        db.session.commit()

        return task

    @staticmethod
    def update_task_status(task_id, new_status, user_id, observations=None, result=None):
        """
        Actualiza el estado de una tarea

        Args:
            task_id: ID de la tarea
            new_status: Nuevo estado (TaskStatus)
            user_id: ID del usuario que actualiza
            observations: Observaciones opcionales
            result: Resultado opcional
        """
        task = Task.query.get(task_id)
        if not task:
            raise ValueError(f"Tarea {task_id} no encontrada")

        old_status = task.status
        task.status = new_status
        task.updated_by_id = user_id

        if observations:
            task.observations = observations
        if result:
            task.result = result

        # Si se completa, registrar fecha
        if new_status == TaskStatus.COMPLETADA:
            task.completion_date = datetime.utcnow()
            task.progress = 100

        # Registrar en historial
        history = TaskHistory(
            task_id=task.id,
            user_id=user_id,
            action='status_changed',
            old_value=old_status.value,
            new_value=new_status.value,
            details=f'Estado cambiado de {old_status.value} a {new_status.value}'
        )
        db.session.add(history)

        db.session.commit()

        return task

    @staticmethod
    def complete_task(task_id, user_id, observations=None, result=None, actual_hours=None):
        """
        Marca una tarea como completada

        Args:
            task_id: ID de la tarea
            user_id: ID del usuario que completa
            observations: Observaciones
            result: Resultado de la tarea
            actual_hours: Horas reales empleadas
        """
        from models import User

        task = Task.query.get(task_id)
        if not task:
            raise ValueError(f"Tarea {task_id} no encontrada")

        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"Usuario {user_id} no encontrado")

        task.complete(
            user=user,
            observations=observations,
            result=result
        )

        if actual_hours:
            task.actual_hours = actual_hours

        db.session.commit()

        return task

    @staticmethod
    def add_comment(task_id, user_id, comment_text, comment_type='general'):
        """
        Agrega un comentario a una tarea

        Args:
            task_id: ID de la tarea
            user_id: ID del usuario
            comment_text: Texto del comentario
            comment_type: Tipo de comentario

        Returns:
            TaskComment: Comentario creado
        """
        comment = TaskComment(
            task_id=task_id,
            created_by_id=user_id,
            comment=comment_text,
            comment_type=comment_type
        )

        db.session.add(comment)
        db.session.commit()

        return comment

    @staticmethod
    def add_evidence(task_id, user_id, filename, original_filename, file_path, file_size, mime_type, description=None):
        """
        Agrega evidencia a una tarea

        Args:
            task_id: ID de la tarea
            user_id: ID del usuario
            filename: Nombre del archivo guardado
            original_filename: Nombre original del archivo
            file_path: Ruta del archivo
            file_size: Tamaño en bytes
            mime_type: Tipo MIME
            description: Descripción opcional

        Returns:
            TaskEvidence: Evidencia creada
        """
        evidence = TaskEvidence(
            task_id=task_id,
            uploaded_by_id=user_id,
            filename=filename,
            original_filename=original_filename,
            file_path=file_path,
            file_size=file_size,
            mime_type=mime_type,
            description=description
        )

        db.session.add(evidence)

        # Registrar en historial
        history = TaskHistory(
            task_id=task_id,
            user_id=user_id,
            action='evidence_added',
            details=f'Evidencia agregada: {original_filename}'
        )
        db.session.add(history)

        db.session.commit()

        return evidence

    @staticmethod
    def get_pending_tasks(user_id=None, role_id=None, limit=None):
        """
        Obtiene tareas pendientes

        Args:
            user_id: Filtrar por usuario (opcional)
            role_id: Filtrar por rol (opcional)
            limit: Límite de resultados (opcional)

        Returns:
            List[Task]: Lista de tareas pendientes
        """
        query = Task.query.filter(
            Task.status.in_([TaskStatus.PENDIENTE, TaskStatus.EN_PROGRESO])
        )

        if user_id:
            query = query.filter(Task.assigned_to_id == user_id)

        if role_id:
            query = query.filter(Task.assigned_role_id == role_id)

        query = query.order_by(Task.due_date.asc())

        if limit:
            query = query.limit(limit)

        return query.all()

    @staticmethod
    def get_overdue_tasks(user_id=None):
        """
        Obtiene tareas vencidas

        Args:
            user_id: Filtrar por usuario (opcional)

        Returns:
            List[Task]: Lista de tareas vencidas
        """
        query = Task.query.filter(
            and_(
                Task.status.in_([TaskStatus.PENDIENTE, TaskStatus.EN_PROGRESO, TaskStatus.VENCIDA]),
                Task.due_date < datetime.utcnow()
            )
        )

        if user_id:
            query = query.filter(Task.assigned_to_id == user_id)

        return query.order_by(Task.due_date.asc()).all()

    @staticmethod
    def get_tasks_due_soon(days=7, user_id=None):
        """
        Obtiene tareas que vencen pronto

        Args:
            days: Número de días hacia adelante
            user_id: Filtrar por usuario (opcional)

        Returns:
            List[Task]: Lista de tareas
        """
        future_date = datetime.utcnow() + timedelta(days=days)

        query = Task.query.filter(
            and_(
                Task.status.in_([TaskStatus.PENDIENTE, TaskStatus.EN_PROGRESO]),
                Task.due_date.between(datetime.utcnow(), future_date)
            )
        )

        if user_id:
            query = query.filter(Task.assigned_to_id == user_id)

        return query.order_by(Task.due_date.asc()).all()

    @staticmethod
    def get_task_statistics(user_id=None, start_date=None, end_date=None):
        """
        Obtiene estadísticas de tareas

        Args:
            user_id: Filtrar por usuario (opcional)
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)

        Returns:
            dict: Diccionario con estadísticas
        """
        query = Task.query

        if user_id:
            query = query.filter(Task.assigned_to_id == user_id)

        if start_date:
            query = query.filter(Task.created_at >= start_date)

        if end_date:
            query = query.filter(Task.created_at <= end_date)

        total = query.count()
        completed = query.filter(Task.status == TaskStatus.COMPLETADA).count()
        pending = query.filter(Task.status == TaskStatus.PENDIENTE).count()
        in_progress = query.filter(Task.status == TaskStatus.EN_PROGRESO).count()
        overdue = query.filter(
            and_(
                Task.status.in_([TaskStatus.PENDIENTE, TaskStatus.EN_PROGRESO, TaskStatus.VENCIDA]),
                Task.due_date < datetime.utcnow()
            )
        ).count()

        # Tasa de cumplimiento
        completion_rate = (completed / total * 100) if total > 0 else 0

        # Por categoría
        by_category = db.session.query(
            Task.category,
            func.count(Task.id)
        ).filter(
            Task.id.in_([t.id for t in query.all()])
        ).group_by(Task.category).all()

        # Por prioridad
        by_priority = db.session.query(
            Task.priority,
            func.count(Task.id)
        ).filter(
            Task.id.in_([t.id for t in query.all()])
        ).group_by(Task.priority).all()

        return {
            'total': total,
            'completed': completed,
            'pending': pending,
            'in_progress': in_progress,
            'overdue': overdue,
            'completion_rate': round(completion_rate, 2),
            'by_category': {cat.value: count for cat, count in by_category},
            'by_priority': {pri.value: count for pri, count in by_priority}
        }

    @staticmethod
    def generate_tasks_from_templates(force=False):
        """
        Genera tareas desde plantillas activas según su frecuencia

        Args:
            force: Forzar generación aunque ya existan tareas

        Returns:
            int: Número de tareas generadas
        """
        templates = TaskTemplate.query.filter_by(is_active=True).all()
        generated_count = 0

        for template in templates:
            # Verificar si toca generar tarea
            if TaskService._should_generate_task(template) or force:
                try:
                    # Crear tarea desde plantilla
                    task = TaskService.create_task_from_template(
                        template.id,
                        user_id=1  # Sistema
                    )
                    generated_count += 1
                except Exception as e:
                    print(f"Error generando tarea desde plantilla {template.id}: {e}")
                    continue

        return generated_count

    @staticmethod
    def _should_generate_task(template):
        """
        Determina si debe generarse una tarea desde una plantilla

        Args:
            template: Plantilla de tarea

        Returns:
            bool: True si debe generarse
        """
        if template.frequency == TaskFrequency.UNICA:
            # Verificar si ya existe una tarea de esta plantilla
            existing = Task.query.filter_by(template_id=template.id).first()
            return existing is None

        # Obtener la última tarea generada de esta plantilla
        last_task = Task.query.filter_by(
            template_id=template.id
        ).order_by(Task.created_at.desc()).first()

        if not last_task:
            return True  # No hay tareas previas

        # Calcular próxima fecha de generación
        next_due = template.calculate_next_due_date(last_task.due_date)

        if next_due is None:
            return False

        # Generar si la próxima fecha de vencimiento es hoy o antes
        return next_due.date() <= datetime.utcnow().date()

    @staticmethod
    def update_overdue_tasks():
        """
        Actualiza el estado de tareas vencidas

        Returns:
            int: Número de tareas actualizadas
        """
        overdue_tasks = Task.query.filter(
            and_(
                Task.status.in_([TaskStatus.PENDIENTE, TaskStatus.EN_PROGRESO]),
                Task.due_date < datetime.utcnow()
            )
        ).all()

        count = 0
        for task in overdue_tasks:
            task.status = TaskStatus.VENCIDA
            count += 1

        if count > 0:
            db.session.commit()

        return count
