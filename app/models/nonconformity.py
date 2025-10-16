"""
Modelos para la gestión de no conformidades según ISO 27001:2023
Control 10.2 - No conformidad y acciones correctivas
Control 10.1 - Mejora continua
"""
from models import db
from datetime import datetime
from sqlalchemy import Enum
import enum


class NCOrigin(enum.Enum):
    """Origen de la no conformidad"""
    INTERNAL_AUDIT = "Auditoría interna"
    EXTERNAL_AUDIT = "Auditoría externa"
    MANAGEMENT_REVIEW = "Revisión por la dirección"
    INCIDENT = "Incidente de seguridad"
    CUSTOMER_COMPLAINT = "Queja de cliente"
    SELF_ASSESSMENT = "Auto-evaluación"
    MONITORING = "Monitorización"
    RISK_ASSESSMENT = "Evaluación de riesgos"
    SUPPLIER_ISSUE = "Problema con proveedor"
    OTHER = "Otro"


class NCSeverity(enum.Enum):
    """Severidad de la no conformidad"""
    MINOR = "Menor"
    MAJOR = "Mayor"
    CRITICAL = "Crítica"


class NCStatus(enum.Enum):
    """Estados del ciclo de vida de la NC (ISO 27001:2023 - 10.2)"""
    NEW = "Nueva"
    ANALYZING = "En análisis"
    ACTION_PLAN = "Plan de acción"
    IMPLEMENTING = "En implementación"
    VERIFYING = "En verificación"
    CLOSED = "Cerrada"
    REOPENED = "Reabierta"


class RCAMethod(enum.Enum):
    """Métodos de análisis de causa raíz"""
    FIVE_WHYS = "5 Porqués"
    ISHIKAWA = "Diagrama de Ishikawa"
    PARETO = "Análisis de Pareto"
    FTA = "Árbol de fallos (FTA)"
    BRAINSTORMING = "Lluvia de ideas"
    OTHER = "Otro"


class ActionType(enum.Enum):
    """Tipo de acción según ISO 27001"""
    CORRECTIVE = "Correctiva"
    PREVENTIVE = "Preventiva"
    IMPROVEMENT = "Mejora"


class ActionStatus(enum.Enum):
    """Estado de las acciones"""
    PENDING = "Pendiente"
    IN_PROGRESS = "En progreso"
    COMPLETED = "Completada"
    VERIFIED = "Verificada"
    CANCELLED = "Cancelada"


class NonConformity(db.Model):
    """
    Modelo principal de No Conformidades
    ISO 27001:2023 - Capítulo 10.2
    """
    __tablename__ = 'nonconformities'

    id = db.Column(db.Integer, primary_key=True)
    nc_number = db.Column(db.String(50), unique=True, nullable=False)  # NC-2025-001

    # Información básica (10.2.f - naturaleza de la no conformidad)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)

    # Clasificación
    origin = db.Column(Enum(NCOrigin), nullable=False)
    severity = db.Column(Enum(NCSeverity), nullable=False, default=NCSeverity.MINOR)
    status = db.Column(Enum(NCStatus), nullable=False, default=NCStatus.NEW)

    # Fechas del ciclo de vida
    detection_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    reported_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    analysis_start_date = db.Column(db.DateTime)  # Cuándo se inició análisis RCA
    action_plan_date = db.Column(db.DateTime)  # Cuándo se definió plan de acción
    implementation_start_date = db.Column(db.DateTime)  # Inicio implementación
    verification_date = db.Column(db.DateTime)  # Cuándo se verificó eficacia
    closure_date = db.Column(db.DateTime)  # Cierre formal
    target_closure_date = db.Column(db.Date)  # Fecha objetivo de cierre

    # Personas involucradas
    reported_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reported_by = db.relationship('User', foreign_keys=[reported_by_id], backref='reported_nonconformities')

    responsible_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    responsible = db.relationship('User', foreign_keys=[responsible_id], backref='responsible_nonconformities')

    verifier_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    verifier = db.relationship('User', foreign_keys=[verifier_id], backref='verified_nonconformities')

    # ISO 27001 - Controles afectados
    affected_controls = db.Column(db.JSON)  # Array de códigos: ["5.9", "8.1", ...]

    # Relación con auditorías (si procede de auditoría)
    audit_id = db.Column(db.Integer, db.ForeignKey('audits.id'))
    audit = db.relationship('Audit', backref='nonconformities')

    # Relación con incidentes (si procede de incidente)
    incident_id = db.Column(db.Integer, db.ForeignKey('incidents.id'))
    incident = db.relationship('Incident', backref='nonconformities')

    # 10.2.a - Acciones para controlar y corregir
    immediate_action = db.Column(db.Text)  # Acción inmediata tomada
    immediate_action_date = db.Column(db.DateTime)

    # 10.2.b - Análisis de causa raíz
    rca_method = db.Column(Enum(RCAMethod))  # Método utilizado
    root_cause_analysis = db.Column(db.Text)  # Análisis completo
    root_causes = db.Column(db.JSON)  # Causas raíz identificadas (array)
    contributing_factors = db.Column(db.JSON)  # Factores contribuyentes

    # 10.2.b.3 - No conformidades similares
    is_recurrent = db.Column(db.Boolean, default=False)
    related_nc_id = db.Column(db.Integer, db.ForeignKey('nonconformities.id'))
    related_nc = db.relationship('NonConformity', remote_side=[id], backref='recurrences')
    similar_nc_analysis = db.Column(db.Text)  # Análisis de NC similares

    # 10.2.d - Verificación de eficacia
    effectiveness_verification = db.Column(db.Text)  # Cómo se verificó
    effectiveness_criteria = db.Column(db.Text)  # Criterios de éxito
    is_effective = db.Column(db.Boolean)  # ¿Fue eficaz?

    # 10.2.e - Cambios al SGSI
    sgsi_changes_required = db.Column(db.Boolean, default=False)
    sgsi_changes_description = db.Column(db.Text)
    sgsi_changes_implemented = db.Column(db.Boolean, default=False)

    # Lecciones aprendidas (mejora continua 10.1)
    lessons_learned = db.Column(db.Text)
    preventive_measures = db.Column(db.JSON)  # Medidas preventivas sugeridas

    # Costos asociados (opcional)
    estimated_cost = db.Column(db.Float)
    actual_cost = db.Column(db.Float)

    # Metadatos
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_by = db.relationship('User', foreign_keys=[created_by_id])

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_by = db.relationship('User', foreign_keys=[updated_by_id])

    notes = db.Column(db.Text)  # Notas adicionales

    # Relaciones
    actions = db.relationship('CorrectiveAction', back_populates='nonconformity',
                            cascade='all, delete-orphan',
                            order_by='CorrectiveAction.due_date')

    timeline_events = db.relationship('NCTimeline', back_populates='nonconformity',
                                     cascade='all, delete-orphan',
                                     order_by='NCTimeline.timestamp.desc()')

    affected_assets = db.relationship('NCAsset', back_populates='nonconformity',
                                     cascade='all, delete-orphan')

    attachments = db.relationship('NCAttachment', back_populates='nonconformity',
                                 cascade='all, delete-orphan')

    def __repr__(self):
        return f'<NonConformity {self.nc_number}: {self.title}>'

    @staticmethod
    def generate_nc_number():
        """Genera número de NC único: NC-YYYY-MM-###"""
        from sqlalchemy import func

        now = datetime.utcnow()
        prefix = f"NC-{now.year}-{now.month:02d}-"

        # Obtener la última NC del mes
        last_nc = NonConformity.query.filter(
            NonConformity.nc_number.like(f"{prefix}%")
        ).order_by(NonConformity.nc_number.desc()).first()

        if last_nc:
            last_num = int(last_nc.nc_number.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"{prefix}{new_num:03d}"

    def calculate_days_open(self):
        """Calcula días que lleva abierta la NC"""
        if self.closure_date:
            delta = self.closure_date - self.reported_date
        else:
            delta = datetime.utcnow() - self.reported_date
        return delta.days

    def calculate_resolution_time(self):
        """Calcula tiempo de resolución en días"""
        if self.reported_date and self.closure_date:
            delta = self.closure_date - self.reported_date
            return delta.days
        return None

    def is_overdue(self):
        """Verifica si está vencida"""
        if self.target_closure_date and self.status != NCStatus.CLOSED:
            return datetime.now().date() > self.target_closure_date
        return False

    def get_progress_percentage(self):
        """Calcula porcentaje de progreso basado en acciones"""
        if not self.actions:
            return 0

        completed = sum(1 for action in self.actions
                       if action.status in [ActionStatus.COMPLETED, ActionStatus.VERIFIED])
        total = len(self.actions)

        return int((completed / total) * 100) if total > 0 else 0

    def to_dict(self):
        """Serializa la NC a diccionario"""
        return {
            'id': self.id,
            'nc_number': self.nc_number,
            'title': self.title,
            'description': self.description,
            'origin': self.origin.value if self.origin else None,
            'severity': self.severity.value if self.severity else None,
            'status': self.status.value if self.status else None,
            'detection_date': self.detection_date.isoformat() if self.detection_date else None,
            'reported_date': self.reported_date.isoformat() if self.reported_date else None,
            'target_closure_date': self.target_closure_date.isoformat() if self.target_closure_date else None,
            'closure_date': self.closure_date.isoformat() if self.closure_date else None,
            'reported_by': {
                'id': self.reported_by.id,
                'name': self.reported_by.name,
                'email': self.reported_by.email
            } if self.reported_by else None,
            'responsible': {
                'id': self.responsible.id,
                'name': self.responsible.name,
                'email': self.responsible.email
            } if self.responsible else None,
            'affected_controls': self.affected_controls,
            'is_recurrent': self.is_recurrent,
            'is_effective': self.is_effective,
            'days_open': self.calculate_days_open(),
            'resolution_time': self.calculate_resolution_time(),
            'is_overdue': self.is_overdue(),
            'progress_percentage': self.get_progress_percentage(),
            'actions_count': len(self.actions) if self.actions else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class CorrectiveAction(db.Model):
    """
    Acciones correctivas y preventivas
    ISO 27001:2023 - 10.2.c, 10.2.d
    """
    __tablename__ = 'corrective_actions'

    id = db.Column(db.Integer, primary_key=True)
    nonconformity_id = db.Column(db.Integer, db.ForeignKey('nonconformities.id'), nullable=False)
    nonconformity = db.relationship('NonConformity', back_populates='actions')

    action_type = db.Column(Enum(ActionType), nullable=False, default=ActionType.CORRECTIVE)
    description = db.Column(db.Text, nullable=False)

    # Detalles de implementación
    implementation_plan = db.Column(db.Text)  # Plan detallado
    resources_required = db.Column(db.Text)  # Recursos necesarios

    # Responsable y fechas
    responsible_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    responsible = db.relationship('User', foreign_keys=[responsible_id])

    status = db.Column(Enum(ActionStatus), nullable=False, default=ActionStatus.PENDING)

    due_date = db.Column(db.Date, nullable=False)
    start_date = db.Column(db.Date)
    completion_date = db.Column(db.Date)

    # Verificación de eficacia (10.2.d)
    verification_method = db.Column(db.Text)  # Cómo se verificará
    verification_criteria = db.Column(db.Text)  # Criterios de éxito
    verification_date = db.Column(db.Date)
    verification_result = db.Column(db.Text)  # Resultado de verificación
    is_effective = db.Column(db.Boolean)  # ¿Fue eficaz?

    verified_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    verified_by = db.relationship('User', foreign_keys=[verified_by_id])

    # Evidencia (10.2.g - resultados)
    evidence_description = db.Column(db.Text)
    evidence_path = db.Column(db.String(500))  # Ruta a archivos de evidencia

    # Costos
    estimated_cost = db.Column(db.Float)
    actual_cost = db.Column(db.Float)

    # Prioridad
    priority = db.Column(db.Integer, default=3)  # 1=Urgente, 5=Baja

    notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<CorrectiveAction {self.id} - {self.action_type.value}>'

    def is_overdue(self):
        """Verifica si está vencida"""
        if self.due_date and self.status not in [ActionStatus.COMPLETED, ActionStatus.VERIFIED]:
            return datetime.now().date() > self.due_date
        return False

    def calculate_days_remaining(self):
        """Calcula días restantes hasta vencimiento"""
        if self.due_date and self.status not in [ActionStatus.COMPLETED, ActionStatus.VERIFIED]:
            delta = self.due_date - datetime.now().date()
            return delta.days
        return None


class NCTimelineEventType(enum.Enum):
    """Tipos de eventos en el timeline"""
    CREATED = "Creada"
    STATUS_CHANGE = "Cambio de estado"
    ASSIGNED = "Asignada"
    COMMENT = "Comentario"
    ACTION_ADDED = "Acción añadida"
    ACTION_COMPLETED = "Acción completada"
    RCA_COMPLETED = "Análisis RCA completado"
    VERIFICATION_STARTED = "Inicio verificación"
    VERIFICATION_COMPLETED = "Verificación completada"
    CLOSURE = "Cierre"
    REOPENED = "Reabierta"
    SGSI_CHANGE = "Cambio en SGSI"
    ATTACHMENT_ADDED = "Archivo adjunto"


class NCTimeline(db.Model):
    """
    Timeline de eventos de la no conformidad
    Proporciona trazabilidad completa (Control 7.5.3)
    """
    __tablename__ = 'nc_timeline'

    id = db.Column(db.Integer, primary_key=True)
    nonconformity_id = db.Column(db.Integer, db.ForeignKey('nonconformities.id'), nullable=False)
    nonconformity = db.relationship('NonConformity', back_populates='timeline_events')

    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    event_type = db.Column(Enum(NCTimelineEventType), nullable=False)

    description = db.Column(db.Text, nullable=False)
    details = db.Column(db.JSON)  # Detalles adicionales en JSON

    # Usuario que realizó la acción
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User')

    # Estado anterior y nuevo (para cambios de estado)
    old_value = db.Column(db.String(100))
    new_value = db.Column(db.String(100))

    def __repr__(self):
        return f'<NCTimeline {self.nonconformity_id} - {self.event_type.value}>'


class NCAsset(db.Model):
    """Relación entre no conformidades y activos afectados"""
    __tablename__ = 'nc_assets'

    id = db.Column(db.Integer, primary_key=True)
    nonconformity_id = db.Column(db.Integer, db.ForeignKey('nonconformities.id'), nullable=False)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)

    nonconformity = db.relationship('NonConformity', back_populates='affected_assets')
    asset = db.relationship('Asset', backref='nonconformities')

    impact_description = db.Column(db.Text)  # Descripción del impacto

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('nonconformity_id', 'asset_id', name='unique_nc_asset'),
    )

    def __repr__(self):
        return f'<NCAsset NC:{self.nonconformity_id} Asset:{self.asset_id}>'


class NCAttachment(db.Model):
    """Archivos adjuntos a las no conformidades (evidencias, análisis, etc.)"""
    __tablename__ = 'nc_attachments'

    id = db.Column(db.Integer, primary_key=True)
    nonconformity_id = db.Column(db.Integer, db.ForeignKey('nonconformities.id'), nullable=False)
    nonconformity = db.relationship('NonConformity', back_populates='attachments')

    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)  # Bytes
    file_type = db.Column(db.String(100))  # MIME type

    description = db.Column(db.Text)
    attachment_type = db.Column(db.String(50))  # evidence, analysis, photo, document, etc.

    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    uploaded_by = db.relationship('User')

    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<NCAttachment {self.file_name}>'
