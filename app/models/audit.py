"""
Modelos para la gestión de auditorías según ISO 27001:2022
Cláusula 9.2 - Auditoría interna
Cláusula 9.3 - Revisión por la dirección
Basado en ISO 19011:2018
"""
from datetime import datetime
from sqlalchemy import Enum
import enum
from models import db


# ============================================================================
# ENUMERACIONES
# ============================================================================

class AuditType(enum.Enum):
    """Tipos de auditoría"""
    INTERNAL_PLANNED = "Auditoría interna planificada"
    INTERNAL_EXTRAORDINARY = "Auditoría interna extraordinaria"
    EXTERNAL_CERTIFICATION = "Auditoría externa de certificación"
    EXTERNAL_SURVEILLANCE = "Auditoría externa de seguimiento"
    MANAGEMENT_REVIEW = "Revisión por la dirección"
    SUPPLIER_AUDIT = "Auditoría a proveedor"


class AuditStatus(enum.Enum):
    """Estados del ciclo de vida de auditoría"""
    PLANNED = "Planificada"
    NOTIFIED = "Notificada"
    PREPARATION = "En preparación"
    IN_PROGRESS = "En progreso"
    REPORTING = "Elaborando informe"
    COMPLETED = "Completada"
    CLOSED = "Cerrada"
    CANCELLED = "Cancelada"


class AuditConclusion(enum.Enum):
    """Conclusión general de la auditoría"""
    CONFORMANT = "Conforme"
    CONFORMANT_WITH_OBSERVATIONS = "Conforme con observaciones"
    NON_CONFORMANT = "No conforme"
    NOT_APPLICABLE = "No aplicable"


class FindingType(enum.Enum):
    """Tipos de hallazgos de auditoría"""
    MAJOR_NC = "No conformidad mayor"
    MINOR_NC = "No conformidad menor"
    OBSERVATION = "Observación"
    OPPORTUNITY_IMPROVEMENT = "Oportunidad de mejora"


class FindingStatus(enum.Enum):
    """Estados de hallazgos"""
    OPEN = "Abierto"
    ACTION_PLAN_PENDING = "Plan de acción pendiente"
    ACTION_PLAN_APPROVED = "Plan de acción aprobado"
    IN_TREATMENT = "En tratamiento"
    RESOLVED = "Resuelto"
    VERIFIED = "Verificado"
    CLOSED = "Cerrado"
    DEFERRED = "Diferido"


class ActionType(enum.Enum):
    """Tipos de acción correctiva"""
    IMMEDIATE = "Acción inmediata"
    CORRECTIVE = "Acción correctiva"
    PREVENTIVE = "Acción preventiva"


class AuditActionStatus(enum.Enum):
    """Estados de acciones correctivas de auditoría"""
    PENDING = "Planificada"
    IN_PROGRESS = "En progreso"
    COMPLETED = "Completada"
    VERIFIED = "Verificada"
    REJECTED = "Rechazada"
    CANCELLED = "Cancelada"


class AuditorRole(enum.Enum):
    """Roles en el equipo auditor"""
    LEAD_AUDITOR = "Auditor líder"
    AUDITOR = "Auditor"
    TECHNICAL_EXPERT = "Experto técnico"
    OBSERVER = "Observador"


class EvidenceType(enum.Enum):
    """Tipos de evidencia de auditoría"""
    DOCUMENT = "Documento"
    RECORD = "Registro"
    INTERVIEW = "Entrevista"
    OBSERVATION = "Observación"
    SCREENSHOT = "Captura de pantalla"
    LOG = "Log del sistema"


class DocumentType(enum.Enum):
    """Tipos de documentos de auditoría"""
    AUDIT_PLAN = "Plan de auditoría"
    AUDIT_REPORT = "Informe de auditoría"
    OPENING_MEETING = "Acta de reunión de apertura"
    CLOSING_MEETING = "Acta de reunión de cierre"
    CHECKLIST = "Lista de verificación"
    EVIDENCE = "Evidencia"
    OTHER = "Otro"


class ProgramStatus(enum.Enum):
    """Estados del programa de auditoría"""
    DRAFT = "Borrador"
    APPROVED = "Aprobado"
    IN_PROGRESS = "En progreso"
    COMPLETED = "Completado"


class AuditFrequency(enum.Enum):
    """Frecuencia de auditorías"""
    ANNUAL = "Anual"
    SEMIANNUAL = "Semestral"
    QUARTERLY = "Trimestral"
    MONTHLY = "Mensual"
    ON_DEMAND = "Bajo demanda"


class QualificationType(enum.Enum):
    """Tipos de calificación de auditores"""
    LEAD_AUDITOR = "Auditor líder"
    AUDITOR = "Auditor"
    AUDITOR_IN_TRAINING = "Auditor en formación"
    TECHNICAL_EXPERT = "Experto técnico"


# ============================================================================
# MODELOS PRINCIPALES
# ============================================================================

class AuditProgram(db.Model):
    """
    Programa Anual de Auditorías
    ISO 27001:2022 - Cláusula 9.2.1
    """
    __tablename__ = 'audit_programs'

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(Enum(ProgramStatus), nullable=False, default=ProgramStatus.DRAFT)

    # Alcance y objetivos
    scope = db.Column(db.Text)
    objectives = db.Column(db.Text)

    # Fechas
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)

    # Aprobación
    approved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_by = db.relationship('User', foreign_keys=[approved_by_id])
    approval_date = db.Column(db.Date)

    # Auditoría
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_by = db.relationship('User', foreign_keys=[created_by_id])

    # Relaciones
    audits = db.relationship('AuditRecord', back_populates='audit_program', lazy='dynamic')
    schedules = db.relationship('AuditSchedule', back_populates='audit_program', lazy='dynamic')

    def __repr__(self):
        return f'<AuditProgram {self.year}: {self.title}>'

    @property
    def audits_count(self):
        """Retorna el número total de auditorías del programa"""
        return self.audits.count()

    @property
    def completion_rate(self):
        """Calcula el % de cumplimiento del programa"""
        total = self.audits.count()
        if total == 0:
            return 0
        completed = self.audits.filter(
            AuditRecord.status.in_([AuditStatus.COMPLETED, AuditStatus.CLOSED])
        ).count()
        return round((completed / total) * 100, 2)


class AuditRecord(db.Model):
    """
    Auditoría Individual (renombrado de Audit para evitar conflictos)
    ISO 27001:2022 - Cláusula 9.2
    """
    __tablename__ = 'audit_records'

    id = db.Column(db.Integer, primary_key=True)
    audit_code = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)

    # Relación con programa
    audit_program_id = db.Column(db.Integer, db.ForeignKey('audit_programs.id'))
    audit_program = db.relationship('AuditProgram', back_populates='audits')

    # Tipo y estado
    audit_type = db.Column(Enum(AuditType), nullable=False)
    status = db.Column(Enum(AuditStatus), nullable=False, default=AuditStatus.PLANNED)

    # Alcance y criterios
    scope = db.Column(db.Text, nullable=False)
    audit_criteria = db.Column(db.Text)
    objectives = db.Column(db.Text)

    # Fechas del ciclo de vida
    planned_date = db.Column(db.Date)
    notification_date = db.Column(db.Date)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    report_date = db.Column(db.Date)
    closure_date = db.Column(db.Date)

    # Equipo auditor
    lead_auditor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    lead_auditor = db.relationship('User', foreign_keys=[lead_auditor_id])

    # Áreas/Procesos auditados (JSON arrays)
    audited_areas = db.Column(db.Text)
    audited_controls = db.Column(db.Text)

    # Documentos
    audit_plan_file = db.Column(db.String(500))
    audit_report_file = db.Column(db.String(500))
    audit_report_document_id = db.Column(db.Integer, db.ForeignKey('documents.id'))
    audit_report_document = db.relationship('Document', foreign_keys=[audit_report_document_id])
    opening_meeting_notes = db.Column(db.Text)
    closing_meeting_notes = db.Column(db.Text)

    # Resultados
    conformity_percentage = db.Column(db.Float)
    total_findings = db.Column(db.Integer, default=0)
    major_findings_count = db.Column(db.Integer, default=0)
    minor_findings_count = db.Column(db.Integer, default=0)
    observations_count = db.Column(db.Integer, default=0)
    opportunities_count = db.Column(db.Integer, default=0)

    # Conclusiones
    overall_conclusion = db.Column(Enum(AuditConclusion))
    conclusion_notes = db.Column(db.Text)
    recommendations = db.Column(db.Text)

    # Seguimiento
    requires_followup = db.Column(db.Boolean, default=False)
    followup_date = db.Column(db.Date)

    # Auditoría
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_by = db.relationship('User', foreign_keys=[updated_by_id])

    # Relaciones
    team_members = db.relationship('AuditTeamMember', back_populates='audit', cascade='all, delete-orphan')
    findings = db.relationship('AuditFinding', back_populates='audit', cascade='all, delete-orphan')
    evidences = db.relationship('AuditEvidence', back_populates='audit', cascade='all, delete-orphan')
    documents = db.relationship('AuditDocument', back_populates='audit', cascade='all, delete-orphan')
    checklists = db.relationship('AuditChecklist', back_populates='audit', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<AuditRecord {self.audit_code}: {self.title}>'

    @staticmethod
    def generate_audit_code():
        """Genera código único de auditoría: AUD-YYYY-###"""
        from sqlalchemy import func

        now = datetime.utcnow()
        prefix = f"AUD-{now.year}-"

        last_audit = AuditRecord.query.filter(
            AuditRecord.audit_code.like(f"{prefix}%")
        ).order_by(AuditRecord.audit_code.desc()).first()

        if last_audit:
            last_num = int(last_audit.audit_code.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"{prefix}{new_num:03d}"

    def update_findings_count(self):
        """Actualiza contadores de hallazgos"""
        self.major_findings_count = len([f for f in self.findings if f.finding_type == FindingType.MAJOR_NC])
        self.minor_findings_count = len([f for f in self.findings if f.finding_type == FindingType.MINOR_NC])
        self.observations_count = len([f for f in self.findings if f.finding_type == FindingType.OBSERVATION])
        self.opportunities_count = len([f for f in self.findings if f.finding_type == FindingType.OPPORTUNITY_IMPROVEMENT])
        self.total_findings = (self.major_findings_count + self.minor_findings_count +
                              self.observations_count + self.opportunities_count)


class AuditTeamMember(db.Model):
    """Miembros del equipo auditor"""
    __tablename__ = 'audit_team_members'

    id = db.Column(db.Integer, primary_key=True)
    audit_id = db.Column(db.Integer, db.ForeignKey('audit_records.id'), nullable=False)
    audit = db.relationship('AuditRecord', back_populates='team_members')

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User')

    role = db.Column(Enum(AuditorRole), nullable=False)
    assigned_areas = db.Column(db.Text)

    # Independencia
    is_independent = db.Column(db.Boolean, default=True)
    conflict_of_interest_declaration = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('audit_id', 'user_id', name='unique_audit_team_member'),
    )

    def __repr__(self):
        return f'<AuditTeamMember Audit:{self.audit_id} User:{self.user_id}>'


class AuditFinding(db.Model):
    """Hallazgos de auditoría"""
    __tablename__ = 'audit_findings'

    id = db.Column(db.Integer, primary_key=True)
    finding_code = db.Column(db.String(50), unique=True, nullable=False)

    audit_id = db.Column(db.Integer, db.ForeignKey('audit_records.id'), nullable=False)
    audit = db.relationship('AuditRecord', back_populates='findings')

    finding_type = db.Column(Enum(FindingType), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)

    # Referencia normativa
    affected_control = db.Column(db.String(20))
    affected_clause = db.Column(db.String(20))
    audit_criteria = db.Column(db.String(255))

    # Área afectada
    department = db.Column(db.String(100))
    process = db.Column(db.String(100))
    responsible_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    responsible = db.relationship('User', foreign_keys=[responsible_id])

    # Evidencia
    evidence = db.Column(db.Text)
    evidence_files = db.Column(db.Text)  # JSON array

    # Análisis
    root_cause = db.Column(db.Text)
    risk_level = db.Column(db.String(20))  # low, medium, high, critical
    potential_impact = db.Column(db.Text)

    # Estado
    status = db.Column(Enum(FindingStatus), nullable=False, default=FindingStatus.OPEN)

    # Auditoría
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_by = db.relationship('User', foreign_keys=[created_by_id])

    # Relaciones
    corrective_actions = db.relationship('AuditCorrectiveAction', back_populates='finding', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<AuditFinding {self.finding_code}>'

    @staticmethod
    def generate_finding_code(audit_code):
        """Genera código único de hallazgo: HAL-YYYY-###-##"""
        last_finding = AuditFinding.query.filter(
            AuditFinding.finding_code.like(f"{audit_code.replace('AUD', 'HAL')}-%")
        ).order_by(AuditFinding.finding_code.desc()).first()

        if last_finding:
            last_num = int(last_finding.finding_code.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"{audit_code.replace('AUD', 'HAL')}-{new_num:02d}"


class AuditCorrectiveAction(db.Model):
    """Acciones correctivas de hallazgos de auditoría"""
    __tablename__ = 'audit_corrective_actions'

    id = db.Column(db.Integer, primary_key=True)
    action_code = db.Column(db.String(50), unique=True, nullable=False)

    finding_id = db.Column(db.Integer, db.ForeignKey('audit_findings.id'), nullable=False)
    finding = db.relationship('AuditFinding', back_populates='corrective_actions')

    action_type = db.Column(Enum(ActionType), nullable=False)

    # Planificación
    description = db.Column(db.Text, nullable=False)
    implementation_plan = db.Column(db.Text)

    responsible_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    responsible = db.relationship('User', foreign_keys=[responsible_id])

    verifier_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    verifier = db.relationship('User', foreign_keys=[verifier_id])

    # Fechas
    planned_start_date = db.Column(db.Date)
    planned_completion_date = db.Column(db.Date)
    actual_completion_date = db.Column(db.Date)
    verification_date = db.Column(db.Date)

    # Estado
    status = db.Column(Enum(AuditActionStatus), nullable=False, default=AuditActionStatus.PENDING)

    # Efectividad
    effectiveness_verified = db.Column(db.Boolean, default=False)
    effectiveness_notes = db.Column(db.Text)
    effectiveness_verification_date = db.Column(db.Date)

    # Recursos
    estimated_cost = db.Column(db.Float)
    actual_cost = db.Column(db.Float)
    resources_needed = db.Column(db.Text)

    # Seguimiento
    progress_percentage = db.Column(db.Integer, default=0)
    progress_notes = db.Column(db.Text)
    blocking_issues = db.Column(db.Text)

    # Planificación adicional
    priority = db.Column(db.String(20))  # LOW, MEDIUM, HIGH, CRITICAL
    expected_benefit = db.Column(db.Text)
    success_criteria = db.Column(db.Text)
    notes = db.Column(db.Text)

    # Auditoría
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<CorrectiveAction {self.action_code}>'

    @staticmethod
    def generate_action_code():
        """Genera código único de acción: AC-YYYY-###"""
        from sqlalchemy import func

        now = datetime.utcnow()
        prefix = f"AC-{now.year}-"

        last_action = AuditCorrectiveAction.query.filter(
            AuditCorrectiveAction.action_code.like(f"{prefix}%")
        ).order_by(AuditCorrectiveAction.action_code.desc()).first()

        if last_action:
            last_num = int(last_action.action_code.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"{prefix}{new_num:03d}"


class AuditEvidence(db.Model):
    """Evidencias de auditoría"""
    __tablename__ = 'audit_evidences'

    id = db.Column(db.Integer, primary_key=True)

    audit_id = db.Column(db.Integer, db.ForeignKey('audit_records.id'), nullable=False)
    audit = db.relationship('AuditRecord', back_populates='evidences')

    finding_id = db.Column(db.Integer, db.ForeignKey('audit_findings.id'))
    finding = db.relationship('AuditFinding')

    evidence_type = db.Column(Enum(EvidenceType), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

    file_path = db.Column(db.String(500))
    file_size = db.Column(db.Integer)

    collected_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    collected_by = db.relationship('User')
    collection_date = db.Column(db.DateTime, default=datetime.utcnow)

    reference = db.Column(db.String(100))
    notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<AuditEvidence {self.id}: {self.title}>'


class AuditDocument(db.Model):
    """Documentos de auditoría"""
    __tablename__ = 'audit_documents'

    id = db.Column(db.Integer, primary_key=True)

    audit_id = db.Column(db.Integer, db.ForeignKey('audit_records.id'), nullable=False)
    audit = db.relationship('AuditRecord', back_populates='documents')

    document_type = db.Column(Enum(DocumentType), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

    file_path = db.Column(db.String(500))
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'))
    document = db.relationship('Document')

    version = db.Column(db.String(20))
    is_final = db.Column(db.Boolean, default=False)

    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    uploaded_by = db.relationship('User')
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)

    notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<AuditDocument {self.document_type.value}: {self.title}>'


class AuditChecklistTemplate(db.Model):
    """Plantillas de listas de verificación"""
    __tablename__ = 'audit_checklist_templates'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    audit_type = db.Column(db.String(50))
    scope = db.Column(db.String(255))

    items = db.Column(db.Text)  # JSON array

    is_active = db.Column(db.Boolean, default=True)
    version = db.Column(db.String(20))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_by = db.relationship('User')

    def __repr__(self):
        return f'<AuditChecklistTemplate {self.name}>'


class AuditChecklist(db.Model):
    """Listas de verificación de auditoría"""
    __tablename__ = 'audit_checklists'

    id = db.Column(db.Integer, primary_key=True)

    audit_id = db.Column(db.Integer, db.ForeignKey('audit_records.id'), nullable=False)
    audit = db.relationship('AuditRecord', back_populates='checklists')

    template_id = db.Column(db.Integer, db.ForeignKey('audit_checklist_templates.id'))
    template = db.relationship('AuditChecklistTemplate')

    auditor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    auditor = db.relationship('User')

    area = db.Column(db.String(100))
    items_data = db.Column(db.Text)  # JSON con resultados
    completion_percentage = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<AuditChecklist Audit:{self.audit_id} Area:{self.area}>'


class AuditorQualification(db.Model):
    """Calificaciones de auditores"""
    __tablename__ = 'auditor_qualifications'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref='auditor_qualifications')

    qualification_type = db.Column(Enum(QualificationType), nullable=False)
    certification_body = db.Column(db.String(200))
    certification_number = db.Column(db.String(100))
    certification_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)

    scope = db.Column(db.Text)
    training_hours = db.Column(db.Integer)
    audit_hours_completed = db.Column(db.Integer, default=0)

    is_active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<AuditorQualification User:{self.user_id} Type:{self.qualification_type.value}>'


class AuditSchedule(db.Model):
    """Cronograma de auditorías"""
    __tablename__ = 'audit_schedules'

    id = db.Column(db.Integer, primary_key=True)

    audit_program_id = db.Column(db.Integer, db.ForeignKey('audit_programs.id'), nullable=False)
    audit_program = db.relationship('AuditProgram', back_populates='schedules')

    area = db.Column(db.String(100), nullable=False)
    process = db.Column(db.String(100))
    frequency = db.Column(Enum(AuditFrequency), nullable=False)

    last_audit_date = db.Column(db.Date)
    next_planned_date = db.Column(db.Date)

    responsible_area_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    responsible_area = db.relationship('User')

    priority = db.Column(db.String(20), default='medium')
    estimated_duration_hours = db.Column(db.Integer)
    notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<AuditSchedule {self.area} - {self.frequency.value}>'


# Alias para compatibilidad con servicios
CorrectiveAction = AuditCorrectiveAction


class AuditMetrics(db.Model):
    """Métricas y KPIs de auditoría"""
    __tablename__ = 'audit_metrics'

    id = db.Column(db.Integer, primary_key=True)

    audit_program_id = db.Column(db.Integer, db.ForeignKey('audit_programs.id'))
    audit_program = db.relationship('AuditProgram')

    period = db.Column(db.String(50))  # 2025-Q1

    # Métricas de ejecución
    planned_audits = db.Column(db.Integer, default=0)
    completed_audits = db.Column(db.Integer, default=0)
    cancelled_audits = db.Column(db.Integer, default=0)
    compliance_rate = db.Column(db.Float)

    # Métricas de hallazgos
    total_findings = db.Column(db.Integer, default=0)
    major_nc = db.Column(db.Integer, default=0)
    minor_nc = db.Column(db.Integer, default=0)
    observations = db.Column(db.Integer, default=0)

    # Métricas de efectividad
    findings_closed_on_time = db.Column(db.Integer, default=0)
    findings_overdue = db.Column(db.Integer, default=0)
    average_closure_time_days = db.Column(db.Float)
    recurrent_findings = db.Column(db.Integer, default=0)

    # Métricas de recursos
    total_audit_hours = db.Column(db.Float)
    average_audit_duration = db.Column(db.Float)

    calculated_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<AuditMetrics {self.period}>'
