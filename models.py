from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

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
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign Keys
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def has_role(self, role_name):
        return self.role.name == role_name

    def can_access(self, module):
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
    document_type = db.Column(db.String(50), nullable=False)  # policy, procedure, instruction, record, minutes
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

    # Relationships
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