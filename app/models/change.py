"""
Modelos para la gestión de cambios según ISO 27001:2023
Control 6.3 - Planificación de cambios
Control 8.32 - Gestión de cambios
Controles relacionados: 5.8, 8.1, 8.19, 8.31
"""
from models import db
from datetime import datetime
from sqlalchemy import Enum
import enum


class ChangeType(enum.Enum):
    """Tipos de cambio en el SGSI"""
    INFRASTRUCTURE = "Infraestructura"
    APPLICATION = "Aplicación"
    NETWORK = "Red"
    SECURITY = "Seguridad"
    PROCESS = "Proceso"
    POLICY = "Política/Procedimiento"
    ORGANIZATIONAL = "Organizacional"
    HARDWARE = "Hardware"
    SOFTWARE = "Software"
    CONFIGURATION = "Configuración"
    OTHER = "Otro"


class ChangeCategory(enum.Enum):
    """Categoría del cambio según ITIL"""
    MINOR = "Menor"  # Bajo riesgo, bajo impacto
    STANDARD = "Estándar"  # Pre-autorizado, procedimiento conocido
    MAJOR = "Mayor"  # Alto impacto, requiere aprobación CAB
    EMERGENCY = "Emergencia"  # Urgente, proceso acelerado


class ChangePriority(enum.Enum):
    """Prioridad del cambio"""
    LOW = "Baja"
    MEDIUM = "Media"
    HIGH = "Alta"
    CRITICAL = "Crítica"


class ChangeStatus(enum.Enum):
    """Estados del ciclo de vida del cambio (Control 6.3 y 8.32)"""
    DRAFT = "Borrador"
    SUBMITTED = "Enviado"
    UNDER_REVIEW = "En revisión"
    PENDING_APPROVAL = "Pendiente de aprobación"
    APPROVED = "Aprobado"
    REJECTED = "Rechazado"
    SCHEDULED = "Programado"
    IN_PROGRESS = "En implementación"
    IMPLEMENTED = "Implementado"
    UNDER_VALIDATION = "En validación"
    CLOSED = "Cerrado"
    CANCELLED = "Cancelado"
    FAILED = "Fallido"
    ROLLED_BACK = "Revertido"


class RiskLevel(enum.Enum):
    """Nivel de riesgo del cambio"""
    LOW = "Bajo"
    MEDIUM = "Medio"
    HIGH = "Alto"
    CRITICAL = "Crítico"


class Change(db.Model):
    """
    Modelo principal de Gestión de Cambios
    Control 6.3 - Planificación de cambios
    Control 8.32 - Gestión de cambios
    """
    __tablename__ = 'changes'

    id = db.Column(db.Integer, primary_key=True)
    change_code = db.Column(db.String(50), unique=True, nullable=False)  # CHG-2025-001

    # Información básica
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)

    # Clasificación
    change_type = db.Column(Enum(ChangeType), nullable=False)
    category = db.Column(Enum(ChangeCategory), nullable=False, default=ChangeCategory.STANDARD)
    priority = db.Column(Enum(ChangePriority), nullable=False, default=ChangePriority.MEDIUM)

    # Estado
    status = db.Column(Enum(ChangeStatus), nullable=False, default=ChangeStatus.DRAFT)

    # Fechas y tiempos
    requested_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    scheduled_start_date = db.Column(db.DateTime)  # Fecha programada de inicio
    scheduled_end_date = db.Column(db.DateTime)  # Fecha programada de fin
    actual_start_date = db.Column(db.DateTime)  # Fecha real de inicio
    actual_end_date = db.Column(db.DateTime)  # Fecha real de finalización
    estimated_duration = db.Column(db.Integer)  # Duración estimada en horas
    actual_duration = db.Column(db.Integer)  # Duración real en horas

    # Ventana de mantenimiento
    downtime_required = db.Column(db.Boolean, default=False)  # ¿Requiere tiempo de inactividad?
    downtime_window_start = db.Column(db.DateTime)
    downtime_window_end = db.Column(db.DateTime)
    estimated_downtime_minutes = db.Column(db.Integer)  # Tiempo de inactividad estimado

    # Personas involucradas
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    requester = db.relationship('User', foreign_keys=[requester_id], backref='requested_changes')

    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    owner = db.relationship('User', foreign_keys=[owner_id], backref='owned_changes')

    # Justificación de negocio
    business_justification = db.Column(db.Text, nullable=False)
    expected_benefits = db.Column(db.Text)  # Beneficios esperados
    impact_if_not_implemented = db.Column(db.Text)  # Impacto si no se implementa

    # Evaluación de riesgos (Control 6.1.2)
    risk_assessment = db.Column(db.Text)  # Evaluación de riesgos
    risk_level = db.Column(Enum(RiskLevel), default=RiskLevel.MEDIUM)

    # Impacto en CIA
    impact_confidentiality = db.Column(db.Boolean, default=False)
    impact_integrity = db.Column(db.Boolean, default=False)
    impact_availability = db.Column(db.Boolean, default=False)

    # Análisis de impacto
    impact_analysis = db.Column(db.Text)  # Análisis detallado de impacto
    affected_services = db.Column(db.JSON)  # Servicios afectados (array)
    affected_users_count = db.Column(db.Integer)  # Número estimado de usuarios afectados

    # Controles ISO 27001 afectados
    affected_controls = db.Column(db.JSON)  # Array de códigos: ["5.8", "8.32", ...]

    # Planes (Control 8.32)
    implementation_plan = db.Column(db.Text, nullable=False)  # Plan de implementación
    rollback_plan = db.Column(db.Text, nullable=False)  # Plan de retroceso/reversión
    test_plan = db.Column(db.Text)  # Plan de pruebas
    communication_plan = db.Column(db.Text)  # Plan de comunicación

    # Entornos afectados (Control 8.31)
    affects_development = db.Column(db.Boolean, default=False)
    affects_testing = db.Column(db.Boolean, default=False)
    affects_production = db.Column(db.Boolean, default=True)

    # Aprobaciones (Change Advisory Board)
    approval_required = db.Column(db.Boolean, default=True)
    cab_date = db.Column(db.DateTime)  # Fecha del comité de cambios
    cab_decision = db.Column(db.Text)  # Decisión del CAB
    cab_notes = db.Column(db.Text)  # Notas del CAB

    # Implementación
    implementation_notes = db.Column(db.Text)  # Notas de implementación
    issues_encountered = db.Column(db.Text)  # Problemas encontrados

    # Post-Implementation Review (PIR)
    pir_date = db.Column(db.DateTime)  # Fecha de revisión post-implementación
    success_criteria = db.Column(db.Text)  # Criterios de éxito
    success_status = db.Column(db.String(50))  # exitoso, parcial, fallido
    lessons_learned = db.Column(db.Text)  # Lecciones aprendidas
    recommendations = db.Column(db.Text)  # Recomendaciones

    # Costos
    estimated_cost = db.Column(db.Float)
    actual_cost = db.Column(db.Float)

    # Integración con otros módulos
    related_incident_id = db.Column(db.Integer, db.ForeignKey('incidents.id'))
    related_incident = db.relationship('Incident', backref='related_changes')

    related_nc_id = db.Column(db.Integer, db.ForeignKey('nonconformities.id'))
    related_nc = db.relationship('NonConformity', backref='related_changes')

    # Cambios relacionados o dependientes
    depends_on_change_id = db.Column(db.Integer, db.ForeignKey('changes.id'))
    depends_on_change = db.relationship('Change', remote_side=[id], backref='dependent_changes')

    # Metadatos
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_by = db.relationship('User', foreign_keys=[created_by_id])

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_by = db.relationship('User', foreign_keys=[updated_by_id])

    notes = db.Column(db.Text)  # Notas adicionales

    # Relaciones
    approvals = db.relationship('ChangeApproval', back_populates='change',
                               cascade='all, delete-orphan',
                               order_by='ChangeApproval.approval_level')

    tasks = db.relationship('ChangeTask', back_populates='change',
                          cascade='all, delete-orphan',
                          order_by='ChangeTask.order')

    documents = db.relationship('ChangeDocument', back_populates='change',
                               cascade='all, delete-orphan')

    history = db.relationship('ChangeHistory', back_populates='change',
                            cascade='all, delete-orphan',
                            order_by='ChangeHistory.changed_at.desc()')

    reviews = db.relationship('ChangeReview', back_populates='change',
                            cascade='all, delete-orphan')

    risk_assessments = db.relationship('ChangeRiskAssessment', back_populates='change',
                                      cascade='all, delete-orphan')

    affected_assets = db.relationship('ChangeAsset', back_populates='change',
                                     cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Change {self.change_code}: {self.title}>'

    @staticmethod
    def generate_change_code():
        """Genera código de cambio único: CHG-YYYY-###"""
        from sqlalchemy import func

        now = datetime.utcnow()
        prefix = f"CHG-{now.year}-"

        # Obtener el último cambio del año
        last_change = Change.query.filter(
            Change.change_code.like(f"{prefix}%")
        ).order_by(Change.change_code.desc()).first()

        if last_change:
            last_num = int(last_change.change_code.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"{prefix}{new_num:04d}"

    def calculate_duration(self):
        """Calcula la duración real del cambio en horas"""
        if self.actual_start_date and self.actual_end_date:
            delta = self.actual_end_date - self.actual_start_date
            return round(delta.total_seconds() / 3600, 2)  # Horas
        return None

    def calculate_variance(self):
        """Calcula la variación entre tiempo estimado y real"""
        if self.estimated_duration and self.actual_duration:
            variance = self.actual_duration - self.estimated_duration
            percentage = (variance / self.estimated_duration) * 100
            return {
                'hours': variance,
                'percentage': round(percentage, 2)
            }
        return None

    @property
    def days_since_request(self):
        """Calcula días desde la solicitud"""
        end_date = self.actual_end_date if self.actual_end_date else datetime.utcnow()
        if self.requested_date:
            delta = end_date - self.requested_date
            return delta.days
        return 0

    @property
    def is_overdue(self):
        """Verifica si el cambio está atrasado"""
        if self.scheduled_end_date and self.status not in [ChangeStatus.CLOSED, ChangeStatus.CANCELLED]:
            return datetime.utcnow() > self.scheduled_end_date
        return False

    @property
    def approval_status(self):
        """Obtiene el estado general de aprobaciones"""
        if not self.approval_required:
            return "no_required"

        if not self.approvals:
            return "pending"

        approved = all(a.status == 'approved' for a in self.approvals)
        rejected = any(a.status == 'rejected' for a in self.approvals)

        if rejected:
            return "rejected"
        elif approved:
            return "approved"
        else:
            return "pending"

    @property
    def completion_percentage(self):
        """Calcula porcentaje de completitud basado en tareas"""
        if not self.tasks:
            return 0

        completed = sum(1 for task in self.tasks if task.status == 'completed')
        total = len(self.tasks)

        return int((completed / total) * 100) if total > 0 else 0

    def can_approve(self):
        """Verifica si el cambio puede ser aprobado"""
        return (
            self.status == ChangeStatus.PENDING_APPROVAL and
            self.approval_status == "approved"
        )

    def can_implement(self):
        """Verifica si el cambio puede ser implementado"""
        return (
            self.status == ChangeStatus.APPROVED and
            self.scheduled_start_date is not None
        )

    def to_dict(self):
        """Serializa el cambio a diccionario"""
        return {
            'id': self.id,
            'change_code': self.change_code,
            'title': self.title,
            'description': self.description,
            'change_type': self.change_type.value if self.change_type else None,
            'category': self.category.value if self.category else None,
            'priority': self.priority.value if self.priority else None,
            'status': self.status.value if self.status else None,
            'risk_level': self.risk_level.value if self.risk_level else None,
            'requested_date': self.requested_date.isoformat() if self.requested_date else None,
            'scheduled_start_date': self.scheduled_start_date.isoformat() if self.scheduled_start_date else None,
            'scheduled_end_date': self.scheduled_end_date.isoformat() if self.scheduled_end_date else None,
            'requester': {
                'id': self.requester.id,
                'name': self.requester.name,
                'email': self.requester.email
            } if self.requester else None,
            'owner': {
                'id': self.owner.id,
                'name': self.owner.name,
                'email': self.owner.email
            } if self.owner else None,
            'approval_required': self.approval_required,
            'approval_status': self.approval_status,
            'completion_percentage': self.completion_percentage,
            'is_overdue': self.is_overdue,
            'days_since_request': self.days_since_request,
            'downtime_required': self.downtime_required,
            'estimated_cost': self.estimated_cost,
            'actual_cost': self.actual_cost,
            'impact': {
                'confidentiality': self.impact_confidentiality,
                'integrity': self.impact_integrity,
                'availability': self.impact_availability
            },
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ApprovalLevel(enum.Enum):
    """Niveles de aprobación"""
    TECHNICAL = "Técnico"
    SECURITY = "Seguridad"
    MANAGEMENT = "Dirección"
    CAB = "CAB (Comité de Cambios)"
    CISO = "CISO"


class ApprovalStatus(enum.Enum):
    """Estado de la aprobación"""
    PENDING = "Pendiente"
    APPROVED = "Aprobado"
    REJECTED = "Rechazado"
    DELEGATED = "Delegado"


class ChangeApproval(db.Model):
    """
    Aprobaciones del cambio (flujo multinivel)
    """
    __tablename__ = 'change_approvals'

    id = db.Column(db.Integer, primary_key=True)
    change_id = db.Column(db.Integer, db.ForeignKey('changes.id'), nullable=False)
    change = db.relationship('Change', back_populates='approvals')

    approval_level = db.Column(Enum(ApprovalLevel), nullable=False)
    approver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    approver = db.relationship('User', foreign_keys=[approver_id])

    status = db.Column(Enum(ApprovalStatus), nullable=False, default=ApprovalStatus.PENDING)

    comments = db.Column(db.Text)
    conditions = db.Column(db.Text)  # Condiciones para la aprobación

    approved_date = db.Column(db.DateTime)

    # Delegación
    delegated_to_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    delegated_to = db.relationship('User', foreign_keys=[delegated_to_id])
    delegation_reason = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<ChangeApproval {self.change_id} - {self.approval_level.value}>'


class TaskStatus(enum.Enum):
    """Estado de las tareas"""
    PENDING = "Pendiente"
    IN_PROGRESS = "En progreso"
    COMPLETED = "Completada"
    BLOCKED = "Bloqueada"
    SKIPPED = "Omitida"


class ChangeTask(db.Model):
    """
    Tareas de implementación del cambio
    """
    __tablename__ = 'change_tasks'

    id = db.Column(db.Integer, primary_key=True)
    change_id = db.Column(db.Integer, db.ForeignKey('changes.id'), nullable=False)
    change = db.relationship('Change', back_populates='tasks')

    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

    order = db.Column(db.Integer, default=0)  # Orden de ejecución
    is_critical = db.Column(db.Boolean, default=False)  # Tarea crítica

    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    assigned_to = db.relationship('User')

    status = db.Column(Enum(TaskStatus), nullable=False, default=TaskStatus.PENDING)

    estimated_duration = db.Column(db.Integer)  # Minutos
    actual_duration = db.Column(db.Integer)  # Minutos

    start_date = db.Column(db.DateTime)
    completed_date = db.Column(db.DateTime)

    notes = db.Column(db.Text)
    blocking_reason = db.Column(db.Text)  # Razón si está bloqueada

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<ChangeTask {self.id} - {self.title}>'


class DocumentType(enum.Enum):
    """Tipos de documentos del cambio"""
    IMPLEMENTATION_PLAN = "Plan de implementación"
    ROLLBACK_PLAN = "Plan de retroceso"
    TEST_PLAN = "Plan de pruebas"
    RISK_ASSESSMENT = "Evaluación de riesgos"
    APPROVAL_FORM = "Formulario de aprobación"
    EVIDENCE = "Evidencia"
    SCREENSHOT = "Captura de pantalla"
    LOG_FILE = "Archivo de log"
    DIAGRAM = "Diagrama"
    OTHER = "Otro"


class ChangeDocument(db.Model):
    """
    Documentos asociados al cambio
    """
    __tablename__ = 'change_documents'

    id = db.Column(db.Integer, primary_key=True)
    change_id = db.Column(db.Integer, db.ForeignKey('changes.id'), nullable=False)
    change = db.relationship('Change', back_populates='documents')

    document_type = db.Column(Enum(DocumentType), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)  # Bytes
    mime_type = db.Column(db.String(100))

    description = db.Column(db.Text)
    version = db.Column(db.String(20))  # Versión del documento

    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    uploaded_by = db.relationship('User')

    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<ChangeDocument {self.file_name}>'


class ChangeHistory(db.Model):
    """
    Historial de cambios (auditoría)
    Proporciona trazabilidad completa (Control 7.5.3)
    """
    __tablename__ = 'change_history'

    id = db.Column(db.Integer, primary_key=True)
    change_id = db.Column(db.Integer, db.ForeignKey('changes.id'), nullable=False)
    change = db.relationship('Change', back_populates='history')

    field_changed = db.Column(db.String(100), nullable=False)
    old_value = db.Column(db.Text)
    new_value = db.Column(db.Text)

    changed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    changed_by = db.relationship('User')

    changed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    comments = db.Column(db.Text)

    def __repr__(self):
        return f'<ChangeHistory {self.change_id} - {self.field_changed}>'


class ReviewStatus(enum.Enum):
    """Estado de la revisión post-implementación"""
    SUCCESSFUL = "Exitoso"
    PARTIALLY_SUCCESSFUL = "Parcialmente exitoso"
    FAILED = "Fallido"


class ChangeReview(db.Model):
    """
    Revisión Post-Implementación (PIR - Post Implementation Review)
    """
    __tablename__ = 'change_reviews'

    id = db.Column(db.Integer, primary_key=True)
    change_id = db.Column(db.Integer, db.ForeignKey('changes.id'), nullable=False)
    change = db.relationship('Change', back_populates='reviews')

    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reviewer = db.relationship('User')

    review_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    success_status = db.Column(Enum(ReviewStatus), nullable=False)

    objectives_met = db.Column(db.Boolean)  # ¿Se cumplieron los objetivos?
    success_criteria_met = db.Column(db.Boolean)  # ¿Se cumplieron criterios de éxito?

    lessons_learned = db.Column(db.Text)  # Lecciones aprendidas
    what_went_well = db.Column(db.Text)  # Qué salió bien
    what_went_wrong = db.Column(db.Text)  # Qué salió mal
    issues_found = db.Column(db.Text)  # Problemas encontrados
    recommendations = db.Column(db.Text)  # Recomendaciones

    # Métricas
    downtime_occurred = db.Column(db.Integer)  # Minutos de inactividad real
    incidents_caused = db.Column(db.Integer)  # Incidentes causados
    rollback_required = db.Column(db.Boolean, default=False)  # ¿Se requirió retroceso?

    notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ChangeReview {self.change_id} - {self.success_status.value}>'


class ChangeRiskAssessment(db.Model):
    """
    Evaluación de riesgos del cambio
    Control 6.1.2 - Evaluación de los riesgos
    """
    __tablename__ = 'change_risk_assessments'

    id = db.Column(db.Integer, primary_key=True)
    change_id = db.Column(db.Integer, db.ForeignKey('changes.id'), nullable=False)
    change = db.relationship('Change', back_populates='risk_assessments')

    risk_description = db.Column(db.Text, nullable=False)

    # Matriz de riesgo
    probability = db.Column(db.Integer, nullable=False)  # 1-5
    impact = db.Column(db.Integer, nullable=False)  # 1-5
    risk_score = db.Column(db.Integer)  # probability * impact

    risk_level = db.Column(Enum(RiskLevel))  # Calculado automáticamente

    mitigation_measures = db.Column(db.Text)  # Medidas de mitigación
    contingency_plan = db.Column(db.Text)  # Plan de contingencia

    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_by = db.relationship('User')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, **kwargs):
        super(ChangeRiskAssessment, self).__init__(**kwargs)
        self.calculate_risk()

    def calculate_risk(self):
        """Calcula el score y nivel de riesgo"""
        if self.probability and self.impact:
            self.risk_score = self.probability * self.impact

            if self.risk_score <= 6:
                self.risk_level = RiskLevel.LOW
            elif self.risk_score <= 12:
                self.risk_level = RiskLevel.MEDIUM
            elif self.risk_score <= 20:
                self.risk_level = RiskLevel.HIGH
            else:
                self.risk_level = RiskLevel.CRITICAL

    def __repr__(self):
        return f'<ChangeRiskAssessment {self.change_id} - Score:{self.risk_score}>'


class ChangeAsset(db.Model):
    """Relación entre cambios y activos afectados"""
    __tablename__ = 'change_assets'

    id = db.Column(db.Integer, primary_key=True)
    change_id = db.Column(db.Integer, db.ForeignKey('changes.id'), nullable=False)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)

    change = db.relationship('Change', back_populates='affected_assets')
    asset = db.relationship('Asset', backref='changes')

    impact_description = db.Column(db.Text)  # Descripción del impacto en el activo

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('change_id', 'asset_id', name='unique_change_asset'),
    )

    def __repr__(self):
        return f'<ChangeAsset Change:{self.change_id} Asset:{self.asset_id}>'
