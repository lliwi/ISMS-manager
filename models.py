from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import Enum
import enum

db = SQLAlchemy()

# Tabla de asociación para la relación muchos-a-muchos entre Document y SOAControl
document_control_association = db.Table('document_control_association',
    db.Column('document_id', db.Integer, db.ForeignKey('documents.id'), primary_key=True),
    db.Column('soa_control_id', db.Integer, db.ForeignKey('soa_controls.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)

class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    users = db.relationship('User', backref='role', lazy=True)

    def __repr__(self):
        return f'<Role {self.name}>'

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    department = db.Column(db.String(100))
    position = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)

    # Security fields
    failed_login_attempts = db.Column(db.Integer, default=0)
    account_locked_until = db.Column(db.DateTime)
    password_changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    must_change_password = db.Column(db.Boolean, default=False)
    last_password_change_notification = db.Column(db.DateTime)

    # Audit fields
    last_login = db.Column(db.DateTime)
    last_login_ip = db.Column(db.String(45))  # IPv6 compatible
    last_activity = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Foreign Keys
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)

    def set_password(self, password):
        """Establece la contraseña del usuario con hash seguro"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        self.password_changed_at = datetime.utcnow()
        self.must_change_password = False

    def check_password(self, password):
        """Verifica la contraseña del usuario"""
        return check_password_hash(self.password_hash, password)

    def is_account_locked(self):
        """Verifica si la cuenta está bloqueada"""
        if self.account_locked_until:
            if datetime.utcnow() < self.account_locked_until:
                return True
            else:
                # El bloqueo ha expirado, resetear contador
                self.failed_login_attempts = 0
                self.account_locked_until = None
        return False

    def increment_failed_login(self):
        """Incrementa el contador de intentos fallidos"""
        self.failed_login_attempts += 1
        # Bloquear cuenta después de 5 intentos fallidos por 30 minutos
        if self.failed_login_attempts >= 5:
            from datetime import timedelta
            self.account_locked_until = datetime.utcnow() + timedelta(minutes=30)

    def reset_failed_login(self):
        """Resetea el contador de intentos fallidos"""
        self.failed_login_attempts = 0
        self.account_locked_until = None

    def needs_password_change(self):
        """Verifica si la contraseña necesita ser cambiada (90 días)"""
        from datetime import timedelta
        if self.must_change_password:
            return True
        if self.password_changed_at:
            password_age = datetime.utcnow() - self.password_changed_at
            return password_age > timedelta(days=90)
        return True

    @property
    def full_name(self):
        """Retorna el nombre completo del usuario"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    def has_role(self, role_name):
        """Verifica si el usuario tiene un rol específico"""
        return self.role.name == role_name

    def can_access(self, module):
        """Verifica si el usuario puede acceder a un módulo"""
        permissions = {
            'admin': ['all'],
            'ciso': ['all'],
            'auditor': ['audits', 'dashboard', 'documents', 'soa', 'risks', 'incidents', 'nonconformities'],
            'owner': ['dashboard', 'documents', 'soa', 'risks', 'incidents', 'tasks'],
            'user': ['dashboard', 'incidents', 'documents']
        }
        user_permissions = permissions.get(self.role.name, [])
        return 'all' in user_permissions or module in user_permissions

    def __repr__(self):
        return f'<User {self.username}>'

class ISOVersion(db.Model):
    __tablename__ = 'iso_versions'

    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(20), unique=True, nullable=False)  # e.g., "2013", "2022"
    year = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    number_of_controls = db.Column(db.Integer)  # e.g., 114 controls in 2013, 93 controls in 2022
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<ISOVersion {self.version}>'

class SOAVersion(db.Model):
    __tablename__ = 'soa_versions'

    id = db.Column(db.Integer, primary_key=True)
    version_number = db.Column(db.String(20), nullable=False)  # e.g., "1.0", "1.1", "2.0"
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    iso_version = db.Column(db.String(20), default='2022')  # Version of ISO 27001
    status = db.Column(db.String(20), default='draft')  # draft, active, archived
    is_current = db.Column(db.Boolean, default=False)
    approval_date = db.Column(db.Date)
    next_review_date = db.Column(db.Date)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    approved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    created_by = db.relationship('User', foreign_keys=[created_by_id], backref='created_soa_versions')
    approved_by = db.relationship('User', foreign_keys=[approved_by_id], backref='approved_soa_versions')
    controls = db.relationship('SOAControl', backref='soa_version', lazy='dynamic')

    def __repr__(self):
        return f'<SOAVersion {self.version_number}>'

    @staticmethod
    def get_current_version():
        """Obtiene la versión actual activa del SOA"""
        return SOAVersion.query.filter_by(is_current=True).first()

    def set_as_current(self):
        """Establece esta versión como la actual"""
        # Desmarcar todas las demás versiones como actuales
        SOAVersion.query.update({'is_current': False})
        self.is_current = True
        self.status = 'active'
        db.session.commit()

class SOAControl(db.Model):
    __tablename__ = 'soa_controls'

    id = db.Column(db.Integer, primary_key=True)
    control_id = db.Column(db.String(10), nullable=False)  # e.g., A.5.1.1
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100), nullable=False)  # e.g., "Information Security Policies"
    applicability_status = db.Column(db.String(20), default='aplicable')  # aplicable, no_aplicable, transferido
    justification = db.Column(db.Text)
    transfer_details = db.Column(db.Text)  # Detalles de a quién se transfiere y bajo qué condiciones
    implementation_status = db.Column(db.String(50), default='not_implemented')  # not_implemented, implemented
    maturity_level = db.Column(db.String(20), default='no_implementado')  # no_implementado, inicial, repetible, definido, controlado, cuantificado, optimizado
    evidence = db.Column(db.Text)  # Campo para explicar cómo se cumple el control
    responsible_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    target_date = db.Column(db.Date)

    # Versionado
    soa_version_id = db.Column(db.Integer, db.ForeignKey('soa_versions.id'), nullable=True)

    # Auditoría
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    responsible = db.relationship('User', backref='soa_controls')
    related_documents = db.relationship('Document', secondary=document_control_association, back_populates='related_controls')

    # Constraints para evitar controles duplicados por versión
    __table_args__ = (
        db.UniqueConstraint('control_id', 'soa_version_id', name='unique_control_per_version'),
    )

    def __repr__(self):
        return f'<SOAControl {self.control_id} v{self.soa_version.version_number if self.soa_version else "None"}>'

    @property
    def maturity_level_display(self):
        """Retorna el nivel de madurez con formato legible"""
        maturity_map = {
            'no_implementado': 'No Implementado (0)',
            'inicial': 'Inicial (1)',
            'repetible': 'Repetible (2)',
            'definido': 'Definido (3)',
            'controlado': 'Controlado (4)',
            'cuantificado': 'Cuantificado (5)',
            'optimizado': 'Optimizado (6)'
        }
        return maturity_map.get(self.maturity_level, self.maturity_level)

    @property
    def maturity_score(self):
        """Retorna el score numérico del nivel de madurez"""
        maturity_scores = {
            'no_implementado': 0,
            'inicial': 1,
            'repetible': 2,
            'definido': 3,
            'controlado': 4,
            'cuantificado': 5,
            'optimizado': 6
        }
        return maturity_scores.get(self.maturity_level, 0)

    @property
    def is_implemented(self):
        """Determina si el control está implementado basado en el nivel de madurez"""
        return self.maturity_score > 0

class Risk(db.Model):
    __tablename__ = 'risks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100))
    probability = db.Column(db.Integer, nullable=False)  # 1-5 scale
    impact = db.Column(db.Integer, nullable=False)  # 1-5 scale
    risk_level = db.Column(db.String(20))  # low, medium, high, critical
    treatment = db.Column(db.String(50))  # accept, mitigate, transfer, avoid
    treatment_description = db.Column(db.Text)
    status = db.Column(db.String(20), default='identified')  # identified, assessed, treated, monitored
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = db.relationship('User', backref='risks')

    def calculate_risk_level(self):
        score = self.probability * self.impact
        if score <= 4:
            return 'low'
        elif score <= 9:
            return 'medium'
        elif score <= 16:
            return 'high'
        else:
            return 'critical'

    def __repr__(self):
        return f'<Risk {self.title}>'

class DocumentVersion(db.Model):
    __tablename__ = 'document_versions'

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    version_number = db.Column(db.String(20), nullable=False)
    file_path = db.Column(db.String(500))
    file_size = db.Column(db.Integer)  # Tamaño en bytes
    file_type = db.Column(db.String(100))  # MIME type
    content = db.Column(db.Text)
    status = db.Column(db.String(20), default='draft')
    change_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    created_by = db.relationship('User', backref='created_document_versions')

    def __repr__(self):
        return f'<DocumentVersion {self.version_number}>'

class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    document_type_id = db.Column(db.Integer, db.ForeignKey('document_types.id'), nullable=False)
    version = db.Column(db.String(20), default='1.0')
    status = db.Column(db.String(20), default='draft')  # draft, review, approved, obsolete
    content = db.Column(db.Text)
    file_path = db.Column(db.String(500))
    file_size = db.Column(db.Integer)  # Tamaño en bytes
    file_type = db.Column(db.String(100))  # MIME type
    approval_date = db.Column(db.Date)
    next_review_date = db.Column(db.Date)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    approver_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Versionado
    current_version_id = db.Column(db.Integer, db.ForeignKey('document_versions.id'))
    parent_document_id = db.Column(db.Integer, db.ForeignKey('documents.id'))

    # Validación IA (opcional)
    ai_verified = db.Column(db.Boolean, default=False)
    ai_verification_date = db.Column(db.DateTime)
    ai_verification_version = db.Column(db.String(20))
    ai_model_used = db.Column(db.String(100))
    ai_overall_score = db.Column(db.Integer)  # 0-100
    ai_verified_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    ai_needs_reverification = db.Column(db.Boolean, default=False)
    ai_verification_comments = db.Column(db.Text)  # Comentarios del verificador humano

    # Relationships
    document_type = db.relationship('DocumentType', backref='documents')
    author = db.relationship('User', foreign_keys=[author_id], backref='authored_documents')
    approver = db.relationship('User', foreign_keys=[approver_id], backref='approved_documents')
    ai_verified_by = db.relationship('User', foreign_keys=[ai_verified_by_id], backref='ai_verified_documents')
    related_controls = db.relationship('SOAControl', secondary=document_control_association, back_populates='related_documents')
    versions = db.relationship('DocumentVersion', backref='document', lazy='dynamic', foreign_keys='DocumentVersion.document_id')
    current_version = db.relationship('DocumentVersion', foreign_keys=[current_version_id], post_update=True)
    parent_document = db.relationship('Document', remote_side=[id], backref='cloned_documents')

    def __repr__(self):
        return f'<Document {self.title} v{self.version}>'

    @property
    def has_file(self):
        """Verifica si el documento tiene un archivo adjunto"""
        return self.file_path is not None and self.file_path != ''

    @property
    def file_extension(self):
        """Retorna la extensión del archivo"""
        if self.file_path:
            return self.file_path.rsplit('.', 1)[-1].lower()
        return None

    @property
    def is_pdf(self):
        """Verifica si el archivo es PDF"""
        return self.file_extension == 'pdf'

    @property
    def is_office(self):
        """Verifica si es un documento ofimático"""
        office_exts = ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'odt', 'ods', 'odp']
        return self.file_extension in office_exts

    @property
    def ai_verification_status(self):
        """Retorna el estado de verificación IA"""
        if not self.ai_verified:
            return 'not_verified'
        if self.ai_needs_reverification:
            return 'needs_reverification'
        if self.ai_overall_score:
            if self.ai_overall_score >= 80:
                return 'verified_compliant'
            elif self.ai_overall_score >= 50:
                return 'verified_partial'
            else:
                return 'verified_non_compliant'
        return 'verified'

class DocumentControlValidation(db.Model):
    __tablename__ = 'document_control_validations'

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    control_id = db.Column(db.Integer, db.ForeignKey('soa_controls.id'), nullable=False)
    document_version = db.Column(db.String(20))

    # Resultados
    compliance_status = db.Column(db.String(20))  # compliant, partial, non_compliant
    confidence_level = db.Column(db.Integer)  # 1-5
    overall_score = db.Column(db.Integer)  # 0-100
    summary = db.Column(db.Text)

    # Detalles (almacenados como JSON)
    ai_analysis = db.Column(db.Text)  # JSON completo de respuesta IA
    covered_aspects = db.Column(db.JSON)
    missing_aspects = db.Column(db.JSON)
    evidence_quotes = db.Column(db.JSON)
    recommendations = db.Column(db.JSON)
    maturity_suggestion = db.Column(db.Integer)  # 2-6

    # Metadatos
    ai_model = db.Column(db.String(100))
    tokens_used = db.Column(db.Integer)
    validation_time = db.Column(db.Float)  # Segundos
    validated_at = db.Column(db.DateTime, default=datetime.utcnow)
    validated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Relationships
    document = db.relationship('Document', backref='ai_validations')
    control = db.relationship('SOAControl', backref='document_validations')
    validated_by = db.relationship('User', backref='ai_validations_performed')

    def __repr__(self):
        return f'<DocumentControlValidation doc:{self.document_id} ctrl:{self.control_id}>'

class Incident(db.Model):
    __tablename__ = 'incidents'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20), nullable=False)  # low, medium, high, critical
    status = db.Column(db.String(20), default='reported')  # reported, investigating, contained, resolved, closed
    incident_type = db.Column(db.String(100))
    detection_date = db.Column(db.DateTime, nullable=False)
    resolution_date = db.Column(db.DateTime)
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    root_cause = db.Column(db.Text)
    lessons_learned = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    reporter = db.relationship('User', foreign_keys=[reporter_id], backref='reported_incidents')
    assignee = db.relationship('User', foreign_keys=[assignee_id], backref='assigned_incidents')

    def __repr__(self):
        return f'<Incident {self.title}>'

class NonConformity(db.Model):
    __tablename__ = 'nonconformities'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    source = db.Column(db.String(100))  # audit, incident, review, etc.
    severity = db.Column(db.String(20), nullable=False)  # minor, major, critical
    status = db.Column(db.String(20), default='open')  # open, investigating, action_plan, closed
    root_cause_method = db.Column(db.String(50))  # 5_whys, ishikawa, etc.
    root_cause_analysis = db.Column(db.Text)
    corrective_action = db.Column(db.Text)
    target_date = db.Column(db.Date)
    closure_date = db.Column(db.Date)
    responsible_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    verifier_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    responsible = db.relationship('User', foreign_keys=[responsible_id], backref='nonconformities')
    verifier = db.relationship('User', foreign_keys=[verifier_id], backref='verified_nonconformities')

    def __repr__(self):
        return f'<NonConformity {self.title}>'

class Audit(db.Model):
    __tablename__ = 'audits'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    audit_type = db.Column(db.String(50), nullable=False)  # internal, external, management_review
    scope = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='planned')  # planned, in_progress, completed, closed
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    lead_auditor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    lead_auditor = db.relationship('User', backref='audits')

    def __repr__(self):
        return f'<Audit {self.title}>'

class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    task_type = db.Column(db.String(50))  # review, maintenance, training, etc.
    frequency = db.Column(db.String(50))  # daily, weekly, monthly, yearly
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, overdue
    due_date = db.Column(db.DateTime, nullable=False)
    completed_date = db.Column(db.DateTime)
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assignee = db.relationship('User', backref='tasks')

    def __repr__(self):
        return f'<Task {self.title}>'

class TrainingSession(db.Model):
    __tablename__ = 'training_sessions'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    training_type = db.Column(db.String(100))  # security_awareness, technical, compliance
    duration_hours = db.Column(db.Float)
    date = db.Column(db.DateTime, nullable=False)
    trainer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    max_participants = db.Column(db.Integer)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled
    materials_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    trainer = db.relationship('User', backref='training_sessions')

    def __repr__(self):
        return f'<TrainingSession {self.title}>'

class DocumentType(db.Model):
    """Tipos de documentos configurables"""
    __tablename__ = 'document_types'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)  # policy, procedure, instruction, etc.
    name = db.Column(db.String(100), nullable=False)  # Política, Procedimiento, etc.
    description = db.Column(db.Text)
    review_period_months = db.Column(db.Integer, default=12)  # Período de revisión en meses
    requires_approval = db.Column(db.Boolean, default=True)  # Requiere aprobación
    approval_workflow = db.Column(db.String(100))  # Tipo de flujo de aprobación
    icon = db.Column(db.String(50), default='fa-file')  # Icono FontAwesome
    color = db.Column(db.String(20), default='primary')  # Color Bootstrap (primary, success, etc.)
    is_active = db.Column(db.Boolean, default=True)  # Tipo activo
    order = db.Column(db.Integer, default=0)  # Orden de visualización
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<DocumentType {self.code}: {self.name}>'

class AuditLog(db.Model):
    """Registro de auditoría para trazabilidad completa"""
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)

    # Información del evento
    action = db.Column(db.String(50), nullable=False)  # login, logout, create, update, delete, view, etc.
    entity_type = db.Column(db.String(50))  # User, Document, Risk, etc.
    entity_id = db.Column(db.Integer)  # ID de la entidad afectada
    description = db.Column(db.Text)

    # Datos del cambio
    old_values = db.Column(db.JSON)  # Valores anteriores
    new_values = db.Column(db.JSON)  # Valores nuevos

    # Información del usuario
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    username = db.Column(db.String(80))  # Guardado por si se elimina el usuario

    # Información de contexto
    ip_address = db.Column(db.String(45))  # IPv6 compatible
    user_agent = db.Column(db.String(255))
    session_id = db.Column(db.String(255))

    # Metadata
    status = db.Column(db.String(20), default='success')  # success, failed, error
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = db.relationship('User', backref='audit_logs', foreign_keys=[user_id])

    def __repr__(self):
        return f'<AuditLog {self.action} by {self.username} at {self.created_at}>'

    @staticmethod
    def log_action(action, entity_type=None, entity_id=None, description=None,
                   old_values=None, new_values=None, user=None, ip_address=None,
                   user_agent=None, status='success', error_message=None):
        """Helper para crear registros de auditoría"""
        from flask_login import current_user

        if user is None and current_user and current_user.is_authenticated:
            user = current_user

        log = AuditLog(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            old_values=old_values,
            new_values=new_values,
            user_id=user.id if user else None,
            username=user.username if user else 'anonymous',
            ip_address=ip_address,
            user_agent=user_agent,
            status=status,
            error_message=error_message
        )

        db.session.add(log)
        return log

"""
Modelos para la gestión de activos/inventario según ISO 27001:2023
Control 5.9 - Inventario de información y otros activos asociados
"""
# db already imported
from datetime import datetime
from sqlalchemy import Enum
import enum


class AssetCategory(enum.Enum):
    """Categorías de activos según ISO 27001"""
    HARDWARE = "Hardware"
    SOFTWARE = "Software"
    INFORMATION = "Información"
    SERVICES = "Servicios"
    PEOPLE = "Personas"
    FACILITIES = "Instalaciones"


class DepreciationPeriod(db.Model):
    """
    Períodos de amortización por categoría de activo
    Permite configurar los años de vida útil para calcular depreciación
    """
    __tablename__ = 'depreciation_periods'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(Enum(AssetCategory), nullable=False, unique=True)
    years = db.Column(db.Integer, nullable=False)  # Años de vida útil
    description = db.Column(db.Text)

    # Método de depreciación (lineal por defecto, futuras expansiones: acelerada, etc.)
    method = db.Column(db.String(50), default='linear')  # linear, accelerated, etc.

    # Valor residual (% del valor original que mantiene al final de vida útil)
    residual_value_percentage = db.Column(db.Float, default=0.0)  # 0-100

    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_by = db.relationship('User', foreign_keys=[updated_by_id])

    def __repr__(self):
        return f'<DepreciationPeriod {self.category.value}: {self.years} años>'

    def calculate_depreciation(self, purchase_cost, acquisition_date):
        """
        Calcula el valor depreciado de un activo

        Args:
            purchase_cost: Coste de adquisición
            acquisition_date: Fecha de adquisición

        Returns:
            Valor actual depreciado
        """
        if not purchase_cost or not acquisition_date:
            return purchase_cost or 0.0

        # Calcular años transcurridos
        today = datetime.now().date()
        if isinstance(acquisition_date, datetime):
            acquisition_date = acquisition_date.date()

        days_elapsed = (today - acquisition_date).days
        years_elapsed = days_elapsed / 365.25  # Considera años bisiestos

        # Si ya superó la vida útil, devolver valor residual
        if years_elapsed >= self.years:
            return purchase_cost * (self.residual_value_percentage / 100.0)

        # Depreciación lineal
        if self.method == 'linear':
            # Valor depreciable (coste - valor residual)
            depreciable_value = purchase_cost * (1 - self.residual_value_percentage / 100.0)
            # Depreciación anual
            annual_depreciation = depreciable_value / self.years
            # Depreciación acumulada
            accumulated_depreciation = annual_depreciation * years_elapsed
            # Valor actual
            current_value = purchase_cost - accumulated_depreciation

            return max(current_value, purchase_cost * (self.residual_value_percentage / 100.0))

        # Otros métodos pueden añadirse aquí en el futuro
        return purchase_cost


class AssetType(db.Model):
    """Tipos de activos configurables por categoría"""
    __tablename__ = 'asset_types'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(Enum(AssetCategory), nullable=False)

    # Configuración visual
    icon = db.Column(db.String(50), default='fa-cube')
    color = db.Column(db.String(20), default='primary')

    # Campos personalizados por tipo (JSON)
    custom_fields = db.Column(db.JSON)  # Define campos adicionales específicos del tipo

    # Estado
    is_active = db.Column(db.Boolean, default=True)
    order = db.Column(db.Integer, default=0)

    # Auditoría
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<AssetType {self.code}: {self.name}>'


class ClassificationLevel(enum.Enum):
    """Niveles de clasificación de información (Control 5.12)"""
    PUBLIC = "Público"
    INTERNAL = "Interno"
    CONFIDENTIAL = "Confidencial"
    RESTRICTED = "Restringido"


class CIALevel(enum.Enum):
    """Niveles de Confidencialidad, Integridad y Disponibilidad"""
    LOW = "Bajo"
    MEDIUM = "Medio"
    HIGH = "Alto"
    CRITICAL = "Crítico"


class AssetStatus(enum.Enum):
    """Estado del activo en su ciclo de vida"""
    ACTIVE = "Activo"
    MAINTENANCE = "En mantenimiento"
    RETIRED = "Retirado"
    DISPOSED = "Eliminado"


class Asset(db.Model):
    """
    Modelo principal de Activos
    Control 5.9 - Inventario de información y otros activos asociados
    """
    __tablename__ = 'assets'

    id = db.Column(db.Integer, primary_key=True)
    asset_code = db.Column(db.String(50), unique=True, nullable=False)  # Código único
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)

    # Categorización
    category = db.Column(Enum(AssetCategory), nullable=False)
    subcategory = db.Column(db.String(100))

    # Tipo de activo (relación con AssetType)
    asset_type_id = db.Column(db.Integer, db.ForeignKey('asset_types.id'))
    asset_type = db.relationship('AssetType', backref='assets')

    # Propietario del activo (requerido por Control 5.9)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    owner = db.relationship('User', foreign_keys=[owner_id], backref='owned_assets')

    # Custodio/responsable técnico (puede ser diferente del propietario)
    custodian_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    custodian = db.relationship('User', foreign_keys=[custodian_id])

    # Ubicación
    physical_location = db.Column(db.String(200))
    logical_location = db.Column(db.String(200))
    department = db.Column(db.String(100))

    # Clasificación de seguridad (Control 5.12)
    classification = db.Column(Enum(ClassificationLevel), nullable=False, default=ClassificationLevel.INTERNAL)

    # Evaluación CIA (Confidencialidad, Integridad, Disponibilidad)
    confidentiality_level = db.Column(Enum(CIALevel), nullable=False, default=CIALevel.MEDIUM)
    integrity_level = db.Column(Enum(CIALevel), nullable=False, default=CIALevel.MEDIUM)
    availability_level = db.Column(Enum(CIALevel), nullable=False, default=CIALevel.MEDIUM)

    # Valor y criticidad
    business_value = db.Column(db.Integer, default=5)  # Escala 1-10
    criticality = db.Column(db.Integer, default=5)  # Escala 1-10

    # Información técnica
    manufacturer = db.Column(db.String(100))
    model = db.Column(db.String(100))
    serial_number = db.Column(db.String(100))
    version = db.Column(db.String(50))

    # Ciclo de vida
    acquisition_date = db.Column(db.Date)
    installation_date = db.Column(db.Date)
    warranty_expiry = db.Column(db.Date)
    planned_retirement = db.Column(db.Date)
    status = db.Column(Enum(AssetStatus), nullable=False, default=AssetStatus.ACTIVE)

    # Costos
    purchase_cost = db.Column(db.Float)
    current_value = db.Column(db.Float)

    # Etiquetado y uso (Control 5.13, 5.10)
    tags = db.Column(db.Text)  # JSON array de etiquetas
    acceptable_use_policy = db.Column(db.Text)
    handling_requirements = db.Column(db.Text)

    # Metadatos
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_by = db.relationship('User', foreign_keys=[created_by_id])

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_by = db.relationship('User', foreign_keys=[updated_by_id])

    # Notas adicionales
    notes = db.Column(db.Text)

    # Relaciones
    relationships_as_source = db.relationship('AssetRelationship',
                                             foreign_keys='AssetRelationship.source_asset_id',
                                             backref='source_asset',
                                             cascade='all, delete-orphan')
    relationships_as_target = db.relationship('AssetRelationship',
                                             foreign_keys='AssetRelationship.target_asset_id',
                                             backref='target_asset',
                                             cascade='all, delete-orphan')

    lifecycle_events = db.relationship('AssetLifecycleEvent', backref='asset',
                                      cascade='all, delete-orphan',
                                      order_by='AssetLifecycleEvent.event_date.desc()')

    def __repr__(self):
        return f'<Asset {self.asset_code}: {self.name}>'

    def calculate_risk_score(self):
        """Calcula puntuación de riesgo basada en CIA y valor"""
        cia_scores = {
            CIALevel.LOW: 1,
            CIALevel.MEDIUM: 2,
            CIALevel.HIGH: 3,
            CIALevel.CRITICAL: 4
        }

        c_score = cia_scores.get(self.confidentiality_level, 2)
        i_score = cia_scores.get(self.integrity_level, 2)
        a_score = cia_scores.get(self.availability_level, 2)

        # Promedio ponderado con valor de negocio
        return ((c_score + i_score + a_score) / 3) * (self.business_value / 10)

    def calculate_current_value(self):
        """
        Calcula el valor actual del activo basado en depreciación

        Returns:
            float: Valor actual depreciado, o el valor manual si existe
        """
        # Si ya hay un valor actual manual, usarlo
        if self.current_value is not None:
            return self.current_value

        # Si no hay coste de adquisición o fecha, no se puede calcular
        if not self.purchase_cost or not self.acquisition_date:
            return None

        # Obtener período de depreciación para esta categoría
        depreciation_period = DepreciationPeriod.query.filter_by(
            category=self.category,
            is_active=True
        ).first()

        if not depreciation_period:
            # Si no hay configuración, devolver el coste de compra
            return self.purchase_cost

        # Calcular y devolver valor depreciado
        return depreciation_period.calculate_depreciation(
            self.purchase_cost,
            self.acquisition_date
        )

    def get_all_relationships(self):
        """Obtiene todas las relaciones del activo"""
        return self.relationships_as_source + self.relationships_as_target

    def to_dict(self):
        """Serializa el activo a diccionario"""
        return {
            'id': self.id,
            'asset_code': self.asset_code,
            'name': self.name,
            'description': self.description,
            'category': self.category.value if self.category else None,
            'subcategory': self.subcategory,
            'owner': {
                'id': self.owner.id,
                'name': self.owner.name,
                'email': self.owner.email
            } if self.owner else None,
            'classification': self.classification.value if self.classification else None,
            'confidentiality_level': self.confidentiality_level.value if self.confidentiality_level else None,
            'integrity_level': self.integrity_level.value if self.integrity_level else None,
            'availability_level': self.availability_level.value if self.availability_level else None,
            'business_value': self.business_value,
            'criticality': self.criticality,
            'status': self.status.value if self.status else None,
            'physical_location': self.physical_location,
            'risk_score': self.calculate_risk_score(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class RelationshipType(enum.Enum):
    """Tipos de relaciones entre activos"""
    DEPENDS_ON = "Depende de"
    CONTAINS = "Contiene"
    CONNECTS_TO = "Conecta con"
    PROCESSES = "Procesa"
    STORES = "Almacena"
    USES = "Utiliza"
    PROTECTS = "Protege"
    SUPPORTS = "Soporta"


class AssetRelationship(db.Model):
    """
    Relaciones y dependencias entre activos
    Importante para análisis de impacto en riesgos
    """
    __tablename__ = 'asset_relationships'

    id = db.Column(db.Integer, primary_key=True)
    source_asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    target_asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)

    relationship_type = db.Column(Enum(RelationshipType), nullable=False)
    description = db.Column(db.Text)

    # Criticidad de la relación
    criticality = db.Column(db.Integer, default=5)  # 1-10

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_by = db.relationship('User')

    __table_args__ = (
        db.UniqueConstraint('source_asset_id', 'target_asset_id', 'relationship_type',
                          name='unique_asset_relationship'),
    )

    def __repr__(self):
        return f'<AssetRelationship {self.source_asset_id} -{self.relationship_type.value}-> {self.target_asset_id}>'


class EventType(enum.Enum):
    """Tipos de eventos en el ciclo de vida del activo"""
    CREATED = "Creado"
    MODIFIED = "Modificado"
    CLASSIFIED = "Clasificado"
    TRANSFERRED = "Transferido"
    MAINTENANCE_START = "Inicio mantenimiento"
    MAINTENANCE_END = "Fin mantenimiento"
    INCIDENT = "Incidente"
    SECURITY_EVENT = "Evento de seguridad"
    RETIRED = "Retirado"
    DISPOSED = "Eliminado"
    CONTROL_APPLIED = "Control aplicado"
    CONTROL_REMOVED = "Control eliminado"
    RISK_IDENTIFIED = "Riesgo identificado"
    REVIEW = "Revisión"


class AssetLifecycleEvent(db.Model):
    """
    Historial de eventos del ciclo de vida del activo
    Proporciona trazabilidad completa (Control 7.5.3)
    """
    __tablename__ = 'asset_lifecycle_events'

    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)

    event_type = db.Column(Enum(EventType), nullable=False)
    event_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    description = db.Column(db.Text, nullable=False)
    details = db.Column(db.Text)  # JSON con detalles adicionales

    # Usuario que realizó el evento
    performed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    performed_by = db.relationship('User')

    # Referencias a otros objetos si aplica
    related_risk_id = db.Column(db.Integer, db.ForeignKey('risks.id'))
    related_incident_id = db.Column(db.Integer)  # Futura relación con incidentes
    related_control_id = db.Column(db.Integer)  # Futura relación con controles

    def __repr__(self):
        return f'<AssetLifecycleEvent {self.event_type.value} - Asset {self.asset_id}>'


class AssetControl(db.Model):
    """
    Relación entre activos y controles de seguridad aplicados
    Vincula con Anexo A de ISO 27001
    """
    __tablename__ = 'asset_controls'

    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    asset = db.relationship('Asset', backref='applied_controls')

    # Control del Anexo A (ej: "5.9", "8.1", etc.)
    control_code = db.Column(db.String(10), nullable=False)
    control_name = db.Column(db.String(200), nullable=False)

    # Estado de implementación
    implementation_status = db.Column(db.String(50))  # Implementado, Parcial, Planificado, No aplicable
    effectiveness = db.Column(db.Integer)  # 1-10

    # Detalles de implementación
    implementation_description = db.Column(db.Text)
    evidence = db.Column(db.Text)

    # Fechas
    implemented_date = db.Column(db.Date)
    last_review_date = db.Column(db.Date)
    next_review_date = db.Column(db.Date)

    # Responsable del control
    responsible_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    responsible = db.relationship('User')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('asset_id', 'control_code', name='unique_asset_control'),
    )

    def __repr__(self):
        return f'<AssetControl {self.control_code} - Asset {self.asset_id}>'
