"""
Modelos para el módulo de Gestión de Tareas Periódicas del SGSI
Basado en ISO/IEC 27001:2023 requisitos de seguimiento y control operacional
"""
from datetime import datetime, timedelta
from sqlalchemy import Enum
import enum
from models import db


# Tabla de asociación para la relación many-to-many entre Task y SOAControl
task_soa_controls = db.Table('task_soa_controls',
    db.Column('task_id', db.Integer, db.ForeignKey('tasks.id'), primary_key=True),
    db.Column('soa_control_id', db.Integer, db.ForeignKey('soa_controls.id'), primary_key=True)
)


class TaskFrequency(enum.Enum):
    """Frecuencia de ejecución de tareas según ISO 27001"""
    DIARIA = 'diaria'
    SEMANAL = 'semanal'
    QUINCENAL = 'quincenal'
    MENSUAL = 'mensual'
    BIMESTRAL = 'bimestral'
    TRIMESTRAL = 'trimestral'
    CUATRIMESTRAL = 'cuatrimestral'
    SEMESTRAL = 'semestral'
    ANUAL = 'anual'
    BIENAL = 'bienal'
    UNICA = 'unica'  # Tarea no recurrente


class PeriodicTaskStatus(enum.Enum):
    """Estados de las tareas periódicas del SGSI"""
    PENDIENTE = 'pendiente'
    EN_PROGRESO = 'en_progreso'
    COMPLETADA = 'completada'
    VENCIDA = 'vencida'
    CANCELADA = 'cancelada'
    REPROGRAMADA = 'reprogramada'


class TaskPriority(enum.Enum):
    """Prioridad de las tareas basada en criticidad de controles ISO 27001"""
    BAJA = 'baja'
    MEDIA = 'media'
    ALTA = 'alta'
    CRITICA = 'critica'


class TaskCategory(enum.Enum):
    """Categorías de tareas según ISO 27001"""
    REVISION_CONTROLES = 'revision_controles'  # 9.1 Seguimiento y medición
    AUDITORIA_INTERNA = 'auditoria_interna'  # 9.2 Auditoría interna
    EVALUACION_RIESGOS = 'evaluacion_riesgos'  # 8.2 Evaluación de riesgos
    REVISION_POLITICAS = 'revision_politicas'  # 5.1 Políticas
    FORMACION_CONCIENCIACION = 'formacion_concienciacion'  # 7.2 y 7.3 Competencia
    MANTENIMIENTO_SEGURIDAD = 'mantenimiento_seguridad'  # 7.13 Mantenimiento
    COPIAS_SEGURIDAD = 'copias_seguridad'  # 8.13 Copias de seguridad
    REVISION_ACCESOS = 'revision_accesos'  # 5.18 Derechos de acceso
    ACTUALIZACION_INVENTARIOS = 'actualizacion_inventarios'  # 5.9 Inventario
    REVISION_PROVEEDORES = 'revision_proveedores'  # 5.22 Seguimiento proveedores
    GESTION_VULNERABILIDADES = 'gestion_vulnerabilidades'  # 8.8 Vulnerabilidades
    REVISION_INCIDENTES = 'revision_incidentes'  # 5.27 Aprender de incidentes
    CONTINUIDAD_NEGOCIO = 'continuidad_negocio'  # 5.30 Continuidad TIC
    REVISION_LEGAL = 'revision_legal'  # 5.31 Requisitos legales
    REVISION_DIRECCION = 'revision_direccion'  # 9.3 Revisión por dirección
    PRUEBAS_RECUPERACION = 'pruebas_recuperacion'  # 8.14 Redundancia
    OTROS = 'otros'


class TaskTemplate(db.Model):
    """
    Plantillas de tareas periódicas
    Define tareas recurrentes del SGSI según ISO 27001
    """
    __tablename__ = 'task_templates'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(Enum(TaskCategory), nullable=False)
    frequency = db.Column(Enum(TaskFrequency), nullable=False)
    priority = db.Column(Enum(TaskPriority), default=TaskPriority.MEDIA)

    # Estimación de tiempo en horas
    estimated_hours = db.Column(db.Float)

    # Control ISO 27001 relacionado (Anexo A)
    iso_control = db.Column(db.String(20))  # Ej: "5.1", "9.2.1", "A.5.19/A.5.20"

    # Rol responsable por defecto
    default_role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    # Usuario responsable por defecto (opcional)
    default_assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Configuración de notificaciones (días antes del vencimiento)
    notify_days_before = db.Column(db.Integer, default=7)

    # Plantilla de lista de verificación (checklist) en JSON
    checklist_template = db.Column(db.JSON)

    # Requiere evidencia obligatoria
    requires_evidence = db.Column(db.Boolean, default=False)

    # Requiere aprobación
    requires_approval = db.Column(db.Boolean, default=False)

    # Activa/Inactiva
    is_active = db.Column(db.Boolean, default=True)

    # Auditoría
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Relaciones
    default_role = db.relationship('Role', foreign_keys=[default_role_id])
    default_assignee = db.relationship('User', foreign_keys=[default_assignee_id])
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    updated_by = db.relationship('User', foreign_keys=[updated_by_id])
    tasks = db.relationship('Task', back_populates='template', lazy='dynamic')

    def __repr__(self):
        return f'<TaskTemplate {self.title}>'

    def calculate_next_due_date(self, from_date=None):
        """Calcula la próxima fecha de vencimiento según frecuencia"""
        if from_date is None:
            from_date = datetime.utcnow()

        frequency_deltas = {
            TaskFrequency.DIARIA: timedelta(days=1),
            TaskFrequency.SEMANAL: timedelta(weeks=1),
            TaskFrequency.QUINCENAL: timedelta(weeks=2),
            TaskFrequency.MENSUAL: timedelta(days=30),
            TaskFrequency.BIMESTRAL: timedelta(days=60),
            TaskFrequency.TRIMESTRAL: timedelta(days=90),
            TaskFrequency.CUATRIMESTRAL: timedelta(days=120),
            TaskFrequency.SEMESTRAL: timedelta(days=180),
            TaskFrequency.ANUAL: timedelta(days=365),
            TaskFrequency.BIENAL: timedelta(days=730),
        }

        if self.frequency == TaskFrequency.UNICA:
            return None

        return from_date + frequency_deltas.get(self.frequency, timedelta(days=30))


class Task(db.Model):
    """
    Instancias de tareas del SGSI
    Tareas generadas desde plantillas o creadas manualmente
    """
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('task_templates.id'))

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(Enum(TaskCategory), nullable=False)
    status = db.Column(Enum(PeriodicTaskStatus), default=PeriodicTaskStatus.PENDIENTE, nullable=False)
    priority = db.Column(Enum(TaskPriority), default=TaskPriority.MEDIA)

    # Fechas
    due_date = db.Column(db.DateTime, nullable=False)
    start_date = db.Column(db.DateTime)
    completion_date = db.Column(db.DateTime)

    # Asignación
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    assigned_role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    # Información adicional
    estimated_hours = db.Column(db.Float)
    actual_hours = db.Column(db.Float)
    iso_control = db.Column(db.String(10))

    # Checklist (JSON)
    checklist = db.Column(db.JSON)

    # Progreso (0-100)
    progress = db.Column(db.Integer, default=0)

    # Observaciones del ejecutor
    observations = db.Column(db.Text)

    # Resultado de la tarea
    result = db.Column(db.Text)

    # Aprobación
    requires_approval = db.Column(db.Boolean, default=False)
    approved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    approval_date = db.Column(db.DateTime)
    approval_comments = db.Column(db.Text)

    # Control de notificaciones
    last_notification_sent = db.Column(db.DateTime)
    notification_count = db.Column(db.Integer, default=0)

    # Auditoría
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Relaciones
    template = db.relationship('TaskTemplate', back_populates='tasks')
    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id], backref='assigned_tasks')
    assigned_role = db.relationship('Role', foreign_keys=[assigned_role_id])
    approved_by = db.relationship('User', foreign_keys=[approved_by_id])
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    updated_by = db.relationship('User', foreign_keys=[updated_by_id])

    # Relación con controles SOA
    related_controls = db.relationship('SOAControl', secondary=task_soa_controls, backref='related_tasks')

    evidences = db.relationship('TaskEvidence', back_populates='task', cascade='all, delete-orphan')
    comments = db.relationship('TaskComment', back_populates='task', cascade='all, delete-orphan')
    history = db.relationship('TaskHistory', back_populates='task', cascade='all, delete-orphan', order_by='TaskHistory.created_at.desc()')
    notification_logs = db.relationship('TaskNotificationLog', back_populates='task', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Task {self.title}>'

    @property
    def is_overdue(self):
        """Verifica si la tarea está vencida"""
        return (self.status not in [PeriodicTaskStatus.COMPLETADA, PeriodicTaskStatus.CANCELADA] and
                self.due_date < datetime.utcnow())

    @property
    def days_until_due(self):
        """Días hasta el vencimiento"""
        if self.status in [PeriodicTaskStatus.COMPLETADA, PeriodicTaskStatus.CANCELADA]:
            return None
        delta = self.due_date - datetime.utcnow()
        return delta.days

    def complete(self, user, observations=None, result=None):
        """Marca la tarea como completada"""
        self.status = PeriodicTaskStatus.COMPLETADA
        self.completion_date = datetime.utcnow()
        self.progress = 100
        if observations:
            self.observations = observations
        if result:
            self.result = result
        self.updated_by_id = user.id

        # Crear historial
        history = TaskHistory(
            task_id=self.id,
            user_id=user.id,
            action='completed',
            details=f'Tarea completada. {observations or ""}'
        )
        db.session.add(history)

    def should_send_notification(self):
        """Determina si debe enviarse notificación"""
        if self.status in [PeriodicTaskStatus.COMPLETADA, PeriodicTaskStatus.CANCELADA]:
            return False

        days_until = self.days_until_due
        if days_until is None:
            return False

        # Notificar en: 7 días, 3 días, 1 día antes y al vencer
        notification_days = [7, 3, 1, 0]

        for notify_day in notification_days:
            if days_until == notify_day:
                # Verificar si ya se notificó hoy
                if self.last_notification_sent:
                    if self.last_notification_sent.date() == datetime.utcnow().date():
                        return False
                return True

        # Tareas vencidas - notificar diariamente
        if days_until < 0:
            if self.last_notification_sent:
                if self.last_notification_sent.date() == datetime.utcnow().date():
                    return False
            return True

        return False


class TaskEvidence(db.Model):
    """
    Evidencias adjuntas a las tareas
    Documentación de cumplimiento de controles
    """
    __tablename__ = 'task_evidences'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)

    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)  # En bytes
    mime_type = db.Column(db.String(100))

    description = db.Column(db.Text)

    # Auditoría
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Relaciones
    task = db.relationship('Task', back_populates='evidences')
    uploaded_by = db.relationship('User')

    def __repr__(self):
        return f'<TaskEvidence {self.original_filename}>'


class TaskComment(db.Model):
    """
    Comentarios en las tareas
    Comunicación entre responsables
    """
    __tablename__ = 'task_comments'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)

    comment = db.Column(db.Text, nullable=False)

    # Tipo de comentario
    comment_type = db.Column(db.String(50))  # 'general', 'question', 'answer', 'observation'

    # Auditoría
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Para marcar comentarios editados
    is_edited = db.Column(db.Boolean, default=False)
    edited_at = db.Column(db.DateTime)

    # Relaciones
    task = db.relationship('Task', back_populates='comments')
    created_by = db.relationship('User')

    def __repr__(self):
        return f'<TaskComment {self.id} for Task {self.task_id}>'


class TaskHistory(db.Model):
    """
    Historial de cambios en tareas
    Trazabilidad para auditoría
    """
    __tablename__ = 'task_history'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    action = db.Column(db.String(50), nullable=False)  # 'created', 'assigned', 'status_changed', 'completed', etc.
    old_value = db.Column(db.Text)
    new_value = db.Column(db.Text)
    details = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    task = db.relationship('Task', back_populates='history')
    user = db.relationship('User')

    def __repr__(self):
        return f'<TaskHistory {self.action} for Task {self.task_id}>'


class TaskNotificationLog(db.Model):
    """
    Registro de notificaciones enviadas
    Control de envíos de email
    """
    __tablename__ = 'task_notification_logs'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)

    recipient_email = db.Column(db.String(120), nullable=False)
    notification_type = db.Column(db.String(50))  # 'reminder', 'overdue', 'completed', 'assigned'

    subject = db.Column(db.String(200))
    body = db.Column(db.Text)

    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    was_successful = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text)

    # Relaciones
    task = db.relationship('Task', back_populates='notification_logs')

    def __repr__(self):
        return f'<TaskNotificationLog {self.notification_type} to {self.recipient_email}>'
