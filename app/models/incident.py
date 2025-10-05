"""
Modelos para la gestión de incidentes de seguridad según ISO 27001:2023
Controles 5.24, 5.25, 5.26, 5.27, 5.28 y 6.8
"""
from app import db
from datetime import datetime
from sqlalchemy import Enum
import enum


class IncidentCategory(enum.Enum):
    """Categorías de incidentes de seguridad"""
    UNAUTHORIZED_ACCESS = "Acceso no autorizado"
    MALWARE = "Malware"
    PHISHING = "Phishing"
    DATA_LOSS = "Pérdida de datos"
    DATA_BREACH = "Brecha de seguridad"
    DENIAL_OF_SERVICE = "Denegación de servicio"
    MISUSE = "Uso indebido"
    SOCIAL_ENGINEERING = "Ingeniería social"
    VULNERABILITY_EXPLOIT = "Explotación de vulnerabilidad"
    SYSTEM_FAILURE = "Fallo de sistema"
    HUMAN_ERROR = "Error humano"
    PHYSICAL_SECURITY = "Seguridad física"
    INSIDER_THREAT = "Amenaza interna"
    RANSOMWARE = "Ransomware"
    OTHER = "Otros"


class IncidentSeverity(enum.Enum):
    """Gravedad del incidente"""
    CRITICAL = "Crítica"
    HIGH = "Alta"
    MEDIUM = "Media"
    LOW = "Baja"


class IncidentPriority(enum.Enum):
    """Prioridad de atención"""
    URGENT = "Urgente"
    HIGH = "Alta"
    NORMAL = "Normal"
    LOW = "Baja"


class IncidentStatus(enum.Enum):
    """Estados del incidente en su ciclo de vida (Control 5.24)"""
    NEW = "Nuevo"
    EVALUATING = "En evaluación"
    CONFIRMED = "Confirmado"
    IN_PROGRESS = "En tratamiento"
    CONTAINED = "Contenido"
    RESOLVED = "Resuelto"
    CLOSED = "Cerrado"
    FALSE_POSITIVE = "Falso positivo"


class IncidentSource(enum.Enum):
    """Origen del incidente"""
    INTERNAL = "Interno"
    EXTERNAL = "Externo"
    UNKNOWN = "Desconocido"


class DetectionMethod(enum.Enum):
    """Método de detección"""
    USER_REPORT = "Reporte de usuario"
    MONITORING = "Monitorización"
    ANTIVIRUS = "Antivirus"
    IDS_IPS = "IDS/IPS"
    SIEM = "SIEM"
    AUDIT = "Auditoría"
    THIRD_PARTY = "Tercero"
    AUTOMATIC = "Automático"
    OTHER = "Otro"


class Incident(db.Model):
    """
    Modelo principal de Incidentes de Seguridad
    Control 5.24 - Planificación y preparación de la gestión de incidentes
    Control 5.25 - Evaluación y decisión sobre eventos de seguridad
    Control 5.26 - Respuesta a incidentes
    """
    __tablename__ = 'incidents'

    id = db.Column(db.Integer, primary_key=True)
    incident_number = db.Column(db.String(50), unique=True, nullable=False)  # INC-2025-001

    # Información básica
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)

    # Clasificación
    category = db.Column(Enum(IncidentCategory), nullable=False)
    severity = db.Column(Enum(IncidentSeverity), nullable=False, default=IncidentSeverity.MEDIUM)
    priority = db.Column(Enum(IncidentPriority), nullable=False, default=IncidentPriority.NORMAL)

    # Estado
    status = db.Column(Enum(IncidentStatus), nullable=False, default=IncidentStatus.NEW)

    # Fechas
    discovery_date = db.Column(db.DateTime, nullable=False)  # Cuándo se descubrió
    reported_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Cuándo se reportó
    start_date = db.Column(db.DateTime)  # Cuándo inició el incidente (estimado)
    containment_date = db.Column(db.DateTime)  # Cuándo se contuvo
    resolution_date = db.Column(db.DateTime)  # Cuándo se resolvió
    closure_date = db.Column(db.DateTime)  # Cuándo se cerró formalmente

    # Personas involucradas
    reported_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reported_by = db.relationship('User', foreign_keys=[reported_by_id], backref='reported_incidents')

    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id], backref='assigned_incidents')

    # Origen y detección
    source = db.Column(Enum(IncidentSource), default=IncidentSource.UNKNOWN)
    detection_method = db.Column(Enum(DetectionMethod), nullable=False)
    detection_details = db.Column(db.Text)

    # Impacto en CIA (Confidencialidad, Integridad, Disponibilidad)
    impact_confidentiality = db.Column(db.Boolean, default=False)
    impact_integrity = db.Column(db.Boolean, default=False)
    impact_availability = db.Column(db.Boolean, default=False)

    # Activos afectados (relación many-to-many)
    affected_assets = db.relationship('IncidentAsset', back_populates='incident', cascade='all, delete-orphan')

    # Controles ISO afectados
    affected_controls = db.Column(db.Text)  # JSON array de códigos de control (ej: ["5.24", "8.1"])

    # Análisis del incidente
    root_cause = db.Column(db.Text)  # Causa raíz
    contributing_factors = db.Column(db.Text)  # Factores contribuyentes

    # Resolución
    resolution = db.Column(db.Text)  # Descripción de la solución aplicada
    lessons_learned = db.Column(db.Text)  # Lecciones aprendidas (Control 5.27)

    # Indicadores para cumplimiento RGPD
    is_data_breach = db.Column(db.Boolean, default=False)  # ¿Es brecha de datos personales?
    requires_notification = db.Column(db.Boolean, default=False)  # ¿Requiere notificación?
    notification_date = db.Column(db.DateTime)  # Fecha de notificación (72h RGPD)

    # Estimaciones de impacto
    estimated_cost = db.Column(db.Float)
    affected_users_count = db.Column(db.Integer)
    downtime_minutes = db.Column(db.Integer)

    # Metadatos
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_by = db.relationship('User', foreign_keys=[created_by_id])

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_by = db.relationship('User', foreign_keys=[updated_by_id])

    # Relaciones
    timeline_events = db.relationship('IncidentTimeline', back_populates='incident',
                                     cascade='all, delete-orphan',
                                     order_by='IncidentTimeline.timestamp.desc()')

    actions = db.relationship('IncidentAction', back_populates='incident',
                            cascade='all, delete-orphan')

    evidences = db.relationship('IncidentEvidence', back_populates='incident',
                               cascade='all, delete-orphan')

    notifications = db.relationship('IncidentNotification', back_populates='incident',
                                   cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Incident {self.incident_number}: {self.title}>'

    @staticmethod
    def generate_incident_number():
        """Genera número de incidente único: INC-YYYY-MM-###"""
        from sqlalchemy import func

        now = datetime.utcnow()
        prefix = f"INC-{now.year}-{now.month:02d}-"

        # Obtener el último incidente del mes
        last_incident = Incident.query.filter(
            Incident.incident_number.like(f"{prefix}%")
        ).order_by(Incident.incident_number.desc()).first()

        if last_incident:
            last_num = int(last_incident.incident_number.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"{prefix}{new_num:03d}"

    def calculate_response_time(self):
        """Calcula tiempo de respuesta en minutos"""
        if self.reported_date and self.status != IncidentStatus.NEW:
            # Buscar el primer evento de cambio de estado
            first_action = IncidentTimeline.query.filter_by(
                incident_id=self.id,
                action_type='STATUS_CHANGE'
            ).order_by(IncidentTimeline.timestamp.asc()).first()

            if first_action:
                delta = first_action.timestamp - self.reported_date
                return int(delta.total_seconds() / 60)
        return None

    def calculate_resolution_time(self):
        """Calcula tiempo de resolución en horas"""
        if self.reported_date and self.resolution_date:
            delta = self.resolution_date - self.reported_date
            return round(delta.total_seconds() / 3600, 2)  # Horas
        return None

    @property
    def days_open(self):
        """Calcula días que el incidente ha estado abierto"""
        end_date = self.closure_date if self.closure_date else datetime.utcnow()
        if self.discovery_date:
            delta = end_date - self.discovery_date
            return delta.days
        return 0

    @property
    def is_72h_violation(self):
        """Verifica si se violó el plazo de 72 horas RGPD para notificación"""
        if self.is_data_breach and self.notification_date:
            delta = self.notification_date - self.discovery_date
            return delta.total_seconds() > (72 * 3600)  # 72 horas
        return False

    @property
    def resolution_summary(self):
        """Alias para resolution"""
        return self.resolution

    @resolution_summary.setter
    def resolution_summary(self, value):
        self.resolution = value

    @property
    def data_breach_details(self):
        """Detalles de la brecha de datos"""
        if self.is_data_breach:
            return self.description
        return None

    def to_dict(self):
        """Serializa el incidente a diccionario"""
        return {
            'id': self.id,
            'incident_number': self.incident_number,
            'title': self.title,
            'description': self.description,
            'category': self.category.value if self.category else None,
            'severity': self.severity.value if self.severity else None,
            'priority': self.priority.value if self.priority else None,
            'status': self.status.value if self.status else None,
            'discovery_date': self.discovery_date.isoformat() if self.discovery_date else None,
            'reported_date': self.reported_date.isoformat() if self.reported_date else None,
            'reported_by': {
                'id': self.reported_by.id,
                'name': self.reported_by.name,
                'email': self.reported_by.email
            } if self.reported_by else None,
            'assigned_to': {
                'id': self.assigned_to.id,
                'name': self.assigned_to.name,
                'email': self.assigned_to.email
            } if self.assigned_to else None,
            'source': self.source.value if self.source else None,
            'detection_method': self.detection_method.value if self.detection_method else None,
            'impact': {
                'confidentiality': self.impact_confidentiality,
                'integrity': self.impact_integrity,
                'availability': self.impact_availability
            },
            'is_data_breach': self.is_data_breach,
            'response_time': self.calculate_response_time(),
            'resolution_time': self.calculate_resolution_time(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class IncidentAsset(db.Model):
    """Relación entre incidentes y activos afectados"""
    __tablename__ = 'incident_assets'

    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incidents.id'), nullable=False)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)

    incident = db.relationship('Incident', back_populates='affected_assets')
    asset = db.relationship('Asset', backref='incidents')

    impact_description = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('incident_id', 'asset_id', name='unique_incident_asset'),
    )

    def __repr__(self):
        return f'<IncidentAsset Incident:{self.incident_id} Asset:{self.asset_id}>'


class ActionType(enum.Enum):
    """Tipos de acciones en el timeline"""
    CREATED = "Creado"
    STATUS_CHANGE = "Cambio de estado"
    ASSIGNED = "Asignado"
    COMMENT = "Comentario"
    EVIDENCE_ADDED = "Evidencia añadida"
    ACTION_ADDED = "Acción añadida"
    NOTIFICATION_SENT = "Notificación enviada"
    CONTAINMENT = "Contención realizada"
    ANALYSIS = "Análisis realizado"
    RESOLUTION = "Resolución aplicada"
    CLOSURE = "Cierre"
    REOPENED = "Reabierto"
    ESCALATED = "Escalado"


class IncidentTimeline(db.Model):
    """
    Timeline de eventos del incidente
    Proporciona trazabilidad completa (Control 7.5.3)
    """
    __tablename__ = 'incident_timeline'

    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incidents.id'), nullable=False)
    incident = db.relationship('Incident', back_populates='timeline_events')

    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    action_type = db.Column(Enum(ActionType), nullable=False)

    description = db.Column(db.Text, nullable=False)
    details = db.Column(db.Text)  # Detalles adicionales en texto o JSON

    # Usuario que realizó la acción
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User')

    # Archivos adjuntos
    attachments = db.Column(db.Text)  # JSON array de rutas de archivos

    def __repr__(self):
        return f'<IncidentTimeline {self.incident_id} - {self.action_type.value}>'


class ActionStatus(enum.Enum):
    """Estado de las acciones correctivas"""
    PENDING = "Pendiente"
    IN_PROGRESS = "En progreso"
    COMPLETED = "Completada"
    CANCELLED = "Cancelada"


class IncidentAction(db.Model):
    """
    Acciones correctivas y preventivas derivadas del incidente
    """
    __tablename__ = 'incident_actions'

    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incidents.id'), nullable=False)
    incident = db.relationship('Incident', back_populates='actions')

    action_type = db.Column(db.String(50))  # Correctiva, Preventiva, Mejora
    description = db.Column(db.Text, nullable=False)

    responsible_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    responsible = db.relationship('User')

    status = db.Column(Enum(ActionStatus), default=ActionStatus.PENDING)

    due_date = db.Column(db.Date)
    completion_date = db.Column(db.Date)

    notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    progress = db.Column(db.Integer, default=0)  # Progreso 0-100%

    @property
    def is_overdue(self):
        """Verifica si la acción está vencida"""
        if self.due_date and self.status != ActionStatus.COMPLETED:
            return datetime.utcnow().date() > self.due_date
        return False

    @property
    def assigned_to(self):
        """Alias para responsible"""
        return self.responsible

    @assigned_to.setter
    def assigned_to(self, value):
        self.responsible = value

    @property
    def assigned_to_id(self):
        """Alias para responsible_id"""
        return self.responsible_id

    @assigned_to_id.setter
    def assigned_to_id(self, value):
        self.responsible_id = value

    @property
    def created_date(self):
        """Alias para created_at"""
        return self.created_at

    @property
    def completed_date(self):
        """Alias para completion_date"""
        return self.completion_date

    def __repr__(self):
        return f'<IncidentAction {self.id} - {self.description[:50]}>'


class EvidenceType(enum.Enum):
    """Tipos de evidencia (Control 5.28)"""
    LOG_FILE = "Archivo de log"
    SCREENSHOT = "Captura de pantalla"
    NETWORK_CAPTURE = "Captura de red"
    EMAIL = "Correo electrónico"
    DOCUMENT = "Documento"
    PHOTO = "Fotografía"
    VIDEO = "Video"
    MEMORY_DUMP = "Volcado de memoria"
    DISK_IMAGE = "Imagen de disco"
    OTHER = "Otro"


class IncidentEvidence(db.Model):
    """
    Evidencias recopiladas del incidente
    Control 5.28 - Recopilación de evidencias
    """
    __tablename__ = 'incident_evidences'

    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incidents.id'), nullable=False)
    incident = db.relationship('Incident', back_populates='evidences')

    evidence_type = db.Column(Enum(EvidenceType), nullable=False)
    description = db.Column(db.Text, nullable=False)

    file_path = db.Column(db.String(500))  # Ruta al archivo de evidencia
    file_name = db.Column(db.String(255))
    file_size = db.Column(db.Integer)  # Tamaño en bytes
    hash_value = db.Column(db.String(128))  # Hash SHA-256 para integridad

    # Cadena de custodia
    collected_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    collected_by = db.relationship('User', foreign_keys=[collected_by_id])
    collection_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    chain_of_custody = db.Column(db.Text)  # Registro de custodia

    notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<IncidentEvidence {self.id} - {self.evidence_type.value}>'


class NotificationType(enum.Enum):
    """Tipos de notificación"""
    INTERNAL_TEAM = "Equipo interno"
    MANAGEMENT = "Dirección"
    DPO = "DPO (Protección de datos)"
    AUTHORITY = "Autoridad competente"
    AFFECTED_USERS = "Usuarios afectados"
    THIRD_PARTY = "Tercero"
    CUSTOMER = "Cliente"
    PROVIDER = "Proveedor"


class IncidentNotification(db.Model):
    """
    Notificaciones realizadas sobre el incidente
    Importante para cumplimiento RGPD (72h)
    """
    __tablename__ = 'incident_notifications'

    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incidents.id'), nullable=False)
    incident = db.relationship('Incident', back_populates='notifications')

    notification_type = db.Column(Enum(NotificationType), nullable=False)
    recipient = db.Column(db.String(200), nullable=False)
    recipient_email = db.Column(db.String(200))

    notification_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    method = db.Column(db.String(50))  # Email, Teléfono, Portal, etc.

    content = db.Column(db.Text)  # Contenido de la notificación

    sent_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    sent_by = db.relationship('User')

    acknowledgement_received = db.Column(db.Boolean, default=False)
    acknowledgement_date = db.Column(db.DateTime)

    notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<IncidentNotification {self.id} - {self.notification_type.value}>'
