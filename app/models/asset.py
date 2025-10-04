"""
Modelos para la gestión de activos/inventario según ISO 27001:2023
Control 5.9 - Inventario de información y otros activos asociados
"""
from app import db
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
