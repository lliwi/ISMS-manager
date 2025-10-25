"""
Modelos de Base de Datos para el Módulo de Gestión de Riesgos
Implementa todas las entidades necesarias para ISO 27001:2023 apartados 6.1.2 y 6.1.3
"""

from models import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY
import math


# ==================== PROCESOS DE NEGOCIO ====================

class ProcesoNegocio(db.Model):
    """Procesos de negocio críticos de la organización"""
    __tablename__ = 'procesos_negocio'

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    area_responsable = db.Column(db.String(100))
    criticidad = db.Column(db.Integer, nullable=False)  # 1-5
    responsable_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    responsable = db.relationship('User', backref='procesos_responsable', foreign_keys=[responsable_id])
    activos = db.relationship('ActivoProceso', back_populates='proceso', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<ProcesoNegocio {self.codigo}: {self.nombre}>'


# ==================== ACTIVOS DE INFORMACIÓN ====================

class ActivoInformacion(db.Model):
    """Activos de información que requieren protección"""
    __tablename__ = 'activos_informacion'

    TIPOS_ACTIVO = ['AP', 'CPD', 'CL', 'DAT', 'DOC', 'FW', 'HW', 'NET', 'OS', 'OT', 'PE', 'ST', 'SW', 'SU', 'TL', 'S', 'INST']
    ESTADOS = ['activo', 'inactivo', 'retirado']

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    tipo_activo = db.Column(db.String(20), nullable=False, index=True)
    funcion = db.Column(db.Text)
    ubicacion = db.Column(db.String(200))
    propietario_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    estado = db.Column(db.String(20), default='activo', index=True)

    # Valoración CIA (0-5)
    confidencialidad = db.Column(db.Integer, default=0)  # 0=No aplica, 1-5=Nivel
    integridad = db.Column(db.Integer, default=0)
    disponibilidad = db.Column(db.Integer, default=0)

    # Justificaciones
    justificacion_c = db.Column(db.Text)
    justificacion_i = db.Column(db.Text)
    justificacion_d = db.Column(db.Text)

    # Importancia calculada (máximo de C-I-D)
    importancia_propia = db.Column(db.Numeric(5, 2))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    propietario = db.relationship('User', backref='activos_propietario', foreign_keys=[propietario_id])
    procesos = db.relationship('ActivoProceso', back_populates='activo', cascade='all, delete-orphan')
    recursos = db.relationship('ActivoRecurso', back_populates='activo', cascade='all, delete-orphan')
    riesgos = db.relationship('Riesgo', back_populates='activo', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<ActivoInformacion {self.codigo}: {self.nombre}>'

    def calcular_importancia_propia(self):
        """Calcula la importancia propia como el máximo de C-I-D"""
        valores = [self.confidencialidad, self.integridad, self.disponibilidad]
        self.importancia_propia = max(valores)
        return self.importancia_propia

    def get_valoracion_dimension(self, dimension):
        """Obtiene la valoración de una dimensión específica (C, I, D)"""
        dimension_map = {
            'C': self.confidencialidad,
            'I': self.integridad,
            'D': self.disponibilidad
        }
        return dimension_map.get(dimension.upper(), 0)


class ActivoProceso(db.Model):
    """Relación M:N entre Activos y Procesos de Negocio"""
    __tablename__ = 'activos_procesos'

    ROLES_RACI = ['R', 'A', 'C', 'I']  # Responsable, Accountable, Consultado, Informado

    id = db.Column(db.Integer, primary_key=True)
    activo_id = db.Column(db.Integer, db.ForeignKey('activos_informacion.id'), nullable=False)
    proceso_id = db.Column(db.Integer, db.ForeignKey('procesos_negocio.id'), nullable=False)
    rol_raci = db.Column(db.String(1))  # R, A, C, I

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    activo = db.relationship('ActivoInformacion', back_populates='procesos')
    proceso = db.relationship('ProcesoNegocio', back_populates='activos')

    __table_args__ = (
        db.UniqueConstraint('activo_id', 'proceso_id', name='uq_activo_proceso'),
    )

    def __repr__(self):
        return f'<ActivoProceso A:{self.activo_id} P:{self.proceso_id} RACI:{self.rol_raci}>'


# ==================== RECURSOS DE INFORMACIÓN ====================

class RecursoInformacion(db.Model):
    """Recursos de información (HW, SW, personas, ubicaciones, etc.)"""
    __tablename__ = 'recursos_informacion'

    TIPOS_RECURSO = ['HARDWARE', 'SOFTWARE', 'RED', 'PERSONAS', 'UBICACION', 'DATOS', 'SERVICIOS']
    ESTADOS = ['operativo', 'mantenimiento', 'retirado']

    # Importancia Tipológica por tipo de recurso
    IMPORTANCIA_TIPOLOGICA = {
        'DOCUMENTACION': 1,
        'UBICACION': 1,
        'PERSONAS': 2,
        'ORGANIZACION': 2,
        'SOFTWARE': 3,
        'RED': 3,
        'HARDWARE': 4,
        'EQUIPAMIENTO': 4,
        'DATOS': 5,
        'SERVICIOS': 5
    }

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    tipo_recurso = db.Column(db.String(20), nullable=False, index=True)
    importancia_tipologica = db.Column(db.Integer, nullable=False, default=3)
    responsable_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    ubicacion = db.Column(db.String(200))
    estado = db.Column(db.String(20), default='operativo')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    responsable = db.relationship('User', backref='recursos_responsable', foreign_keys=[responsable_id])
    activos = db.relationship('ActivoRecurso', back_populates='recurso', cascade='all, delete-orphan')
    riesgos = db.relationship('Riesgo', back_populates='recurso', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<RecursoInformacion {self.codigo}: {self.nombre}>'

    @classmethod
    def get_importancia_tipologica_default(cls, tipo_recurso):
        """Obtiene la importancia tipológica por defecto según el tipo"""
        return cls.IMPORTANCIA_TIPOLOGICA.get(tipo_recurso.upper(), 3)


class ActivoRecurso(db.Model):
    """Relación M:N entre Activos y Recursos"""
    __tablename__ = 'activos_recursos'

    TIPOS_USO = ['almacena', 'procesa', 'transmite', 'accede']

    id = db.Column(db.Integer, primary_key=True)
    activo_id = db.Column(db.Integer, db.ForeignKey('activos_informacion.id'), nullable=False)
    recurso_id = db.Column(db.Integer, db.ForeignKey('recursos_informacion.id'), nullable=False)
    tipo_uso = db.Column(db.String(50))
    criticidad = db.Column(db.Integer)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    activo = db.relationship('ActivoInformacion', back_populates='recursos')
    recurso = db.relationship('RecursoInformacion', back_populates='activos')

    __table_args__ = (
        db.UniqueConstraint('activo_id', 'recurso_id', name='uq_activo_recurso'),
    )

    def __repr__(self):
        return f'<ActivoRecurso A:{self.activo_id} R:{self.recurso_id}>'


# ==================== AMENAZAS ====================

class Amenaza(db.Model):
    """Catálogo de amenazas según MAGERIT 3.2"""
    __tablename__ = 'amenazas'

    GRUPOS = ['NATURALES', 'INDUSTRIALES', 'ERRORES', 'ATAQUES']

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    grupo = db.Column(db.String(50), nullable=False, index=True)
    categoria_magerit = db.Column(db.String(50))

    # Aplicabilidad por dimensión
    afecta_confidencialidad = db.Column(db.Boolean, default=False)
    afecta_integridad = db.Column(db.Boolean, default=False)
    afecta_disponibilidad = db.Column(db.Boolean, default=False)

    # Tipo de control
    es_preventiva = db.Column(db.Boolean, default=True)
    es_reactiva = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    aplicabilidad_recursos = db.relationship('AmenazaRecursoTipo', back_populates='amenaza', cascade='all, delete-orphan')
    controles = db.relationship('ControlAmenaza', back_populates='amenaza', cascade='all, delete-orphan')
    riesgos = db.relationship('Riesgo', back_populates='amenaza', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Amenaza {self.codigo}: {self.nombre}>'

    def afecta_dimension(self, dimension):
        """Verifica si la amenaza afecta una dimensión específica"""
        dimension_map = {
            'C': self.afecta_confidencialidad,
            'I': self.afecta_integridad,
            'D': self.afecta_disponibilidad
        }
        return dimension_map.get(dimension.upper(), False)


class AmenazaRecursoTipo(db.Model):
    """Aplicabilidad de amenazas a tipos de recursos con frecuencia"""
    __tablename__ = 'amenazas_recursos_tipo'

    DIMENSIONES = ['C', 'I', 'D']

    id = db.Column(db.Integer, primary_key=True)
    amenaza_id = db.Column(db.Integer, db.ForeignKey('amenazas.id'), nullable=False)
    tipo_recurso = db.Column(db.String(20), nullable=False)
    frecuencia_base = db.Column(db.Integer, default=3)  # 0-5
    dimension_afectada = db.Column(db.String(1))  # C, I, D

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    amenaza = db.relationship('Amenaza', back_populates='aplicabilidad_recursos')

    __table_args__ = (
        db.UniqueConstraint('amenaza_id', 'tipo_recurso', 'dimension_afectada', name='uq_amenaza_recurso_dim'),
    )

    def __repr__(self):
        return f'<AmenazaRecursoTipo A:{self.amenaza_id} R:{self.tipo_recurso} D:{self.dimension_afectada}>'


# ==================== CONTROLES ISO 27002 ====================

class ControlISO27002(db.Model):
    """Catálogo de controles ISO 27002:2022 (93 controles)"""
    __tablename__ = 'controles_iso27002'

    CATEGORIAS = ['ORGANIZACIONALES', 'PERSONAS', 'FISICOS', 'TECNOLOGICOS']
    TIPOS_CONTROL = ['PREVENTIVO', 'REACTIVO', 'DETECTIVE', 'DISUASORIO']

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(300), nullable=False)
    descripcion = db.Column(db.Text)
    categoria = db.Column(db.String(50), nullable=False, index=True)
    tipo_control = db.Column(db.String(20), nullable=False, index=True)

    # Referencias cruzadas
    codigo_iso27001_2013 = db.Column(db.String(20))
    codigo_tisax = db.Column(db.String(20))

    objetivo = db.Column(db.Text)
    guia_implementacion = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    # NOTA: amenazas ya no usa ControlISO27002, usa SOA directamente
    salvaguardas = db.relationship('SalvaguardaImplantada', back_populates='control', cascade='all, delete-orphan')
    declaraciones = db.relationship('DeclaracionAplicabilidad', back_populates='control', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<ControlISO27002 {self.codigo}: {self.nombre[:50]}>'


class ControlAmenaza(db.Model):
    """Aplicabilidad de controles SOA a amenazas

    Relaciona controles del SOA (por código, ej: 'A.5.1') con amenazas.
    El control_codigo referencia al SOA activo, no a la tabla controles_iso27002.
    Esto permite cambiar versiones de ISO/SOA sin romper las relaciones.
    """
    __tablename__ = 'controles_amenazas'

    TIPOS_CONTROL = ['PREVENTIVO', 'REACTIVO', 'DETECTIVE', 'DISUASORIO']

    id = db.Column(db.Integer, primary_key=True)
    control_codigo = db.Column(db.String(10), nullable=False, index=True)  # ej: "A.5.1"
    amenaza_id = db.Column(db.Integer, db.ForeignKey('amenazas.id'), nullable=False)
    tipo_control = db.Column(db.String(20), nullable=False, default='PREVENTIVO', index=True)
    efectividad = db.Column(db.Numeric(3, 2), default=1.00)  # 0.0 - 1.0

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    amenaza = db.relationship('Amenaza', back_populates='controles')

    __table_args__ = (
        db.UniqueConstraint('control_codigo', 'amenaza_id', name='uq_control_amenaza'),
    )

    def get_soa_control(self):
        """Obtiene el control correspondiente del SOA activo"""
        from models import SOAControl, SOAVersion

        soa_activo = SOAVersion.query.filter_by(is_current=True).first()
        if not soa_activo:
            return None

        return SOAControl.query.filter_by(
            control_id=self.control_codigo,
            soa_version_id=soa_activo.id
        ).first()

    def __repr__(self):
        return f'<ControlAmenaza C:{self.control_codigo} A:{self.amenaza_id} T:{self.tipo_control}>'


# ==================== SALVAGUARDAS IMPLANTADAS ====================

class SalvaguardaImplantada(db.Model):
    """Controles implementados en la organización con su nivel de madurez"""
    __tablename__ = 'salvaguardas_implantadas'

    ESTADOS = ['planificado', 'en_progreso', 'implementado', 'verificado', 'no_aplica']

    id = db.Column(db.Integer, primary_key=True)
    control_id = db.Column(db.Integer, db.ForeignKey('controles_iso27002.id'), nullable=False)

    # Nivel de madurez CMM (0-5)
    nivel_madurez = db.Column(db.Integer, default=0)  # 0=No existe, 5=Optimizado

    # Detalles de implementación
    descripcion_implementacion = db.Column(db.Text)
    evidencias = db.Column(db.Text)
    responsable_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    fecha_implementacion = db.Column(db.Date)
    fecha_ultima_revision = db.Column(db.Date)

    # Estado
    estado = db.Column(db.String(20), default='implementado', index=True)

    # Aplicabilidad
    aplica = db.Column(db.Boolean, default=True)
    justificacion_no_aplica = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    control = db.relationship('ControlISO27002', back_populates='salvaguardas')
    responsable = db.relationship('User', backref='salvaguardas_responsable', foreign_keys=[responsable_id])

    def __repr__(self):
        return f'<SalvaguardaImplantada C:{self.control_id} Madurez:{self.nivel_madurez}>'

    @property
    def nivel_madurez_texto(self):
        """Devuelve el texto del nivel de madurez"""
        niveles = {
            0: 'No existe',
            1: 'Inicial/Ad-hoc',
            2: 'Reproducible',
            3: 'Definido',
            4: 'Gestionado',
            5: 'Optimizado'
        }
        return niveles.get(self.nivel_madurez, 'Desconocido')


# ==================== EVALUACIONES DE RIESGO ====================

class EvaluacionRiesgo(db.Model):
    """Evaluaciones de riesgo realizadas"""
    __tablename__ = 'evaluaciones_riesgo'

    ESTADOS = ['planificada', 'en_curso', 'completada', 'aprobada', 'obsoleta']

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date)
    estado = db.Column(db.String(20), default='en_curso', index=True)

    # Criterios de aceptación
    umbral_riesgo_objetivo = db.Column(db.Numeric(5, 2), default=50.00)

    # Alcance
    alcance_descripcion = db.Column(db.Text)

    # Responsables
    responsable_evaluacion_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    aprobador_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    fecha_aprobacion = db.Column(db.Date)

    # Versionado
    version = db.Column(db.String(20))
    evaluacion_anterior_id = db.Column(db.Integer, db.ForeignKey('evaluaciones_riesgo.id'))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    responsable_evaluacion = db.relationship('User', foreign_keys=[responsable_evaluacion_id], backref='evaluaciones_responsable')
    aprobador = db.relationship('User', foreign_keys=[aprobador_id], backref='evaluaciones_aprobadas')
    evaluacion_anterior = db.relationship('EvaluacionRiesgo', remote_side=[id], backref='evaluaciones_posteriores')
    riesgos = db.relationship('Riesgo', back_populates='evaluacion', cascade='all, delete-orphan')
    declaraciones = db.relationship('DeclaracionAplicabilidad', back_populates='evaluacion', cascade='all, delete-orphan')
    planes_tratamiento = db.relationship('PlanTratamientoRiesgos', back_populates='evaluacion', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<EvaluacionRiesgo {self.nombre} v{self.version}>'


# ==================== RIESGOS ====================

class Riesgo(db.Model):
    """Riesgos identificados y calculados"""
    __tablename__ = 'riesgos'

    CLASIFICACIONES = ['MUY_BAJO', 'BAJO', 'MEDIO', 'ALTO', 'MUY_ALTO']
    DIMENSIONES = ['C', 'I', 'D']

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    evaluacion_id = db.Column(db.Integer, db.ForeignKey('evaluaciones_riesgo.id'), nullable=False)

    # Relaciones
    activo_id = db.Column(db.Integer, db.ForeignKey('activos_informacion.id'))
    recurso_id = db.Column(db.Integer, db.ForeignKey('recursos_informacion.id'))
    amenaza_id = db.Column(db.Integer, db.ForeignKey('amenazas.id'))

    # Dimensión afectada
    dimension = db.Column(db.String(1))  # C, I, D

    # ===== CÁLCULOS DE RIESGO INTRÍNSECO (sin controles) =====
    importancia_propia = db.Column(db.Numeric(5, 2))
    importancia_tipologica = db.Column(db.Integer)
    modulo_normalizador_impacto = db.Column(db.Numeric(5, 4))

    frecuencia_amenaza = db.Column(db.Integer)
    modulo_normalizador_probabilidad = db.Column(db.Numeric(5, 4))

    impacto_intrinseco = db.Column(db.Numeric(8, 2))
    probabilidad_intrinseca = db.Column(db.Numeric(8, 2))
    nivel_riesgo_intrinseco = db.Column(db.Numeric(10, 2))

    # ===== CÁLCULOS DE RIESGO EFECTIVO (con controles actuales) =====
    gravedad_vulnerabilidad = db.Column(db.Numeric(5, 2))
    facilidad_explotacion = db.Column(db.Numeric(5, 2))
    num_controles_reactivos = db.Column(db.Integer, default=0)
    num_controles_preventivos = db.Column(db.Integer, default=0)

    impacto_efectivo = db.Column(db.Numeric(8, 2))
    probabilidad_efectiva = db.Column(db.Numeric(8, 2))
    nivel_riesgo_efectivo = db.Column(db.Numeric(10, 2), index=True)

    # ===== CÁLCULOS DE RIESGO RESIDUAL (con controles planificados) =====
    impacto_residual = db.Column(db.Numeric(8, 2))
    probabilidad_residual = db.Column(db.Numeric(8, 2))
    nivel_riesgo_residual = db.Column(db.Numeric(10, 2))

    # Clasificaciones cualitativas
    clasificacion_intrinseca = db.Column(db.String(20))
    clasificacion_efectiva = db.Column(db.String(20))
    clasificacion_residual = db.Column(db.String(20))

    # Propietario del riesgo
    propietario_riesgo_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Observaciones
    observaciones = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones ORM
    evaluacion = db.relationship('EvaluacionRiesgo', back_populates='riesgos')
    activo = db.relationship('ActivoInformacion', back_populates='riesgos')
    recurso = db.relationship('RecursoInformacion', back_populates='riesgos')
    amenaza = db.relationship('Amenaza', back_populates='riesgos')
    propietario_riesgo = db.relationship('User', backref='riesgos_propietario', foreign_keys=[propietario_riesgo_id])
    tratamientos = db.relationship('TratamientoRiesgo', back_populates='riesgo', cascade='all, delete-orphan')
    historial = db.relationship('HistorialRiesgo', back_populates='riesgo', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Riesgo {self.codigo} Nivel:{self.nivel_riesgo_efectivo} {self.clasificacion_efectiva}>'

    @staticmethod
    def clasificar_nivel(probabilidad, impacto):
        """
        Clasifica el riesgo según la matriz Probabilidad x Impacto

        Escala normalizada 0-10 para Probabilidad e Impacto:
        - ALTO: >= 7
        - MEDIO: 4-6.9
        - BAJO: < 4

        Matriz:
                    Impacto
                Bajo  Medio  Alto
        Prob Alto   Medio Alto  Muy Alto
        Prob Medio  Bajo  Medio Alto
        Prob Bajo   Muy Bajo Bajo Medio
        """
        # Determinar nivel de probabilidad (escala 0-10)
        if probabilidad >= 7:
            nivel_prob = 'ALTO'
        elif probabilidad >= 4:
            nivel_prob = 'MEDIO'
        else:
            nivel_prob = 'BAJO'

        # Determinar nivel de impacto (escala 0-10)
        if impacto >= 7:
            nivel_imp = 'ALTO'
        elif impacto >= 4:
            nivel_imp = 'MEDIO'
        else:
            nivel_imp = 'BAJO'

        # Aplicar matriz
        matriz = {
            ('ALTO', 'ALTO'): 'MUY_ALTO',
            ('ALTO', 'MEDIO'): 'ALTO',
            ('ALTO', 'BAJO'): 'MEDIO',
            ('MEDIO', 'ALTO'): 'ALTO',
            ('MEDIO', 'MEDIO'): 'MEDIO',
            ('MEDIO', 'BAJO'): 'BAJO',
            ('BAJO', 'ALTO'): 'MEDIO',
            ('BAJO', 'MEDIO'): 'BAJO',
            ('BAJO', 'BAJO'): 'MUY_BAJO'
        }

        return matriz.get((nivel_prob, nivel_imp), 'MEDIO')


# ==================== TRATAMIENTOS DE RIESGO ====================

class TratamientoRiesgo(db.Model):
    """Decisiones de tratamiento para cada riesgo"""
    __tablename__ = 'tratamientos_riesgo'

    OPCIONES = ['ASUMIR', 'REDUCIR', 'TRANSFERIR', 'ELIMINAR']
    ESTADOS = ['planificado', 'en_progreso', 'implementado', 'verificado', 'cancelado']

    id = db.Column(db.Integer, primary_key=True)
    riesgo_id = db.Column(db.Integer, db.ForeignKey('riesgos.id'), nullable=False)

    # Decisión de tratamiento
    opcion_tratamiento = db.Column(db.String(20), nullable=False, index=True)
    justificacion = db.Column(db.Text, nullable=False)

    # Controles a implementar (solo para REDUCIR)
    controles_adicionales = db.Column(ARRAY(db.Integer))  # Array de IDs de controles

    # Detalles de transferencia
    tercero_receptor = db.Column(db.String(200))
    poliza_seguro = db.Column(db.String(100))
    coste_estimado = db.Column(db.Numeric(10, 2))

    # Plan de acción
    descripcion_accion = db.Column(db.Text)
    fecha_inicio_planificada = db.Column(db.Date)
    fecha_fin_planificada = db.Column(db.Date)

    # Responsables
    responsable_implementacion_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Estado
    estado = db.Column(db.String(20), default='planificado', index=True)
    progreso = db.Column(db.Integer, default=0)  # 0-100%

    # Aprobación
    aprobado_por_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    fecha_aprobacion = db.Column(db.Date)

    # Seguimiento
    fecha_ultima_revision = db.Column(db.Date)
    proxima_revision = db.Column(db.Date)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    riesgo = db.relationship('Riesgo', back_populates='tratamientos')
    responsable_implementacion = db.relationship('User', foreign_keys=[responsable_implementacion_id], backref='tratamientos_responsable')
    aprobado_por = db.relationship('User', foreign_keys=[aprobado_por_id], backref='tratamientos_aprobados')

    def __repr__(self):
        return f'<TratamientoRiesgo R:{self.riesgo_id} {self.opcion_tratamiento}>'


# ==================== DECLARACIÓN DE APLICABILIDAD (SOA) ====================

class DeclaracionAplicabilidad(db.Model):
    """Statement of Applicability - Declaración de Aplicabilidad ISO 27001"""
    __tablename__ = 'declaracion_aplicabilidad'

    id = db.Column(db.Integer, primary_key=True)
    evaluacion_id = db.Column(db.Integer, db.ForeignKey('evaluaciones_riesgo.id'), nullable=False)
    control_id = db.Column(db.Integer, db.ForeignKey('controles_iso27002.id'), nullable=False)

    # Decisión de aplicabilidad
    aplica = db.Column(db.Boolean, nullable=False)
    justificacion_inclusion = db.Column(db.Text)
    justificacion_exclusion = db.Column(db.Text)

    # Estado de implementación
    implementado = db.Column(db.Boolean, default=False)
    nivel_implementacion = db.Column(db.Integer)  # 0-5
    salvaguarda_id = db.Column(db.Integer, db.ForeignKey('salvaguardas_implantadas.id'))

    # Seguimiento
    fecha_revision = db.Column(db.Date)
    revisor_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    evaluacion = db.relationship('EvaluacionRiesgo', back_populates='declaraciones')
    control = db.relationship('ControlISO27002', back_populates='declaraciones')
    salvaguarda = db.relationship('SalvaguardaImplantada', backref='declaraciones_soa')
    revisor = db.relationship('User', backref='declaraciones_revisadas', foreign_keys=[revisor_id])

    __table_args__ = (
        db.UniqueConstraint('evaluacion_id', 'control_id', name='uq_eval_control'),
    )

    def __repr__(self):
        return f'<DeclaracionAplicabilidad E:{self.evaluacion_id} C:{self.control_id} Aplica:{self.aplica}>'


# ==================== PLAN DE TRATAMIENTO ====================

class PlanTratamientoRiesgos(db.Model):
    """Plan global de tratamiento de riesgos"""
    __tablename__ = 'plan_tratamiento_riesgos'

    ESTADOS = ['borrador', 'aprobado', 'en_ejecucion', 'completado', 'cancelado']

    id = db.Column(db.Integer, primary_key=True)
    evaluacion_id = db.Column(db.Integer, db.ForeignKey('evaluaciones_riesgo.id'), nullable=False)

    nombre = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)

    # Periodo de ejecución
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin_prevista = db.Column(db.Date, nullable=False)
    fecha_fin_real = db.Column(db.Date)

    # Presupuesto
    presupuesto_estimado = db.Column(db.Numeric(12, 2))
    presupuesto_ejecutado = db.Column(db.Numeric(12, 2))

    # Estado global
    estado = db.Column(db.String(20), default='borrador', index=True)
    progreso_global = db.Column(db.Integer, default=0)  # 0-100%

    # Aprobación
    aprobado_por_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    fecha_aprobacion = db.Column(db.Date)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    evaluacion = db.relationship('EvaluacionRiesgo', back_populates='planes_tratamiento')
    aprobado_por = db.relationship('User', backref='planes_aprobados', foreign_keys=[aprobado_por_id])

    def __repr__(self):
        return f'<PlanTratamientoRiesgos {self.nombre} {self.estado}>'


# ==================== HISTORIAL ====================

class HistorialRiesgo(db.Model):
    """Historial de cambios en los riesgos"""
    __tablename__ = 'historial_riesgos'

    id = db.Column(db.Integer, primary_key=True)
    riesgo_id = db.Column(db.Integer, db.ForeignKey('riesgos.id'), nullable=False)

    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Snapshot de valores
    nivel_riesgo_efectivo_anterior = db.Column(db.Numeric(10, 2))
    nivel_riesgo_efectivo_nuevo = db.Column(db.Numeric(10, 2))

    clasificacion_anterior = db.Column(db.String(20))
    clasificacion_nueva = db.Column(db.String(20))

    # Cambio realizado
    tipo_cambio = db.Column(db.String(50))  # EVALUACION_INICIAL, IMPLEMENTACION_CONTROL, etc.
    descripcion_cambio = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    riesgo = db.relationship('Riesgo', back_populates='historial')
    usuario = db.relationship('User', backref='historial_riesgos')

    def __repr__(self):
        return f'<HistorialRiesgo R:{self.riesgo_id} {self.tipo_cambio}>'
