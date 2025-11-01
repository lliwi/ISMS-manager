# Diseño: Visión de Activos por Servicio

## Objetivo
Implementar una funcionalidad que permita organizar y visualizar activos agrupados por servicios, facilitando la gestión del inventario desde una perspectiva de servicios de negocio.

## Contexto ISO 27001:2023
- **Control 5.9**: Inventario de información y otros activos asociados
- **Control 8.1**: Gestión de activos a nivel de servicio
- **Anexo A**: Trazabilidad de activos críticos por servicio

## Modelo de Datos

### Nueva Entidad: Service

```python
class ServiceType(enum.Enum):
    """Tipos de servicios"""
    BUSINESS = "Servicio de Negocio"
    TECHNICAL = "Servicio Técnico"
    INFRASTRUCTURE = "Infraestructura"
    APPLICATION = "Aplicación"
    SUPPORT = "Soporte"

class ServiceStatus(enum.Enum):
    """Estados del servicio"""
    ACTIVE = "Activo"
    INACTIVE = "Inactivo"
    DEPRECATED = "Obsoleto"
    PLANNED = "Planificado"

class Service(db.Model):
    """
    Modelo de Servicios
    Permite agrupar activos por servicio de negocio o técnico
    """
    __tablename__ = 'services'

    id = db.Column(db.Integer, primary_key=True)
    service_code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)

    # Clasificación
    service_type = db.Column(Enum(ServiceType), nullable=False)
    status = db.Column(Enum(ServiceStatus), default=ServiceStatus.ACTIVE)

    # Responsables
    service_owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service_owner = db.relationship('User', foreign_keys=[service_owner_id])

    technical_manager_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    technical_manager = db.relationship('User', foreign_keys=[technical_manager_id])

    # Criticidad y disponibilidad
    criticality = db.Column(db.Integer, default=5)  # 1-10
    required_availability = db.Column(db.Float)  # % (ej: 99.9)
    rto = db.Column(db.Float)  # Recovery Time Objective (días, ej: 0.5 = 12 horas)
    rpo = db.Column(db.Float)  # Recovery Point Objective (días, ej: 0.25 = 6 horas)

    # Información operativa
    operating_hours = db.Column(db.String(100))  # "24/7", "8-18 L-V", etc.
    max_users = db.Column(db.Integer)
    department = db.Column(db.String(100))

    # Costos
    annual_cost = db.Column(db.Float)

    # Dependencias (servicios de los que depende)
    # Se implementa con ServiceDependency

    # Auditoría
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_by = db.relationship('User', foreign_keys=[created_by_id])

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_by = db.relationship('User', foreign_keys=[updated_by_id])

    notes = db.Column(db.Text)
```

### Tabla de Asociación: service_asset_association

```python
service_asset_association = db.Table('service_asset_association',
    db.Column('service_id', db.Integer, db.ForeignKey('services.id'), primary_key=True),
    db.Column('asset_id', db.Integer, db.ForeignKey('assets.id'), primary_key=True),
    db.Column('role', db.String(50)),  # "critical", "support", "backup", etc.
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)
```

### Dependencias entre Servicios

```python
class ServiceDependency(db.Model):
    """Dependencias entre servicios"""
    __tablename__ = 'service_dependencies'

    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    depends_on_service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    dependency_type = db.Column(db.String(50))  # "required", "optional", "enhances"
    description = db.Column(db.Text)

    service = db.relationship('Service', foreign_keys=[service_id], backref='dependencies')
    depends_on = db.relationship('Service', foreign_keys=[depends_on_service_id])
```

## Funcionalidades a Implementar

### 1. CRUD de Servicios
- **Listar servicios**: Vista con filtros por tipo, estado, departamento
- **Crear servicio**: Formulario con todos los campos
- **Ver detalle**: Información completa + activos asociados + dependencias
- **Editar servicio**: Actualizar información
- **Eliminar servicio**: Soft delete con validaciones

### 2. Gestión de Activos por Servicio
- **Asociar activos a servicio**: Selección múltiple con roles
- **Desasociar activos**: Eliminar relación
- **Vista de activos por servicio**: Tabla filtrable
- **Mapa de dependencias**: Visualización de servicios y activos

### 3. Vistas y Reportes
- **Dashboard de servicios**: KPIs, criticidad, disponibilidad
- **Vista de activos por servicio**: Filtro adicional en /activos
- **Árbol de dependencias**: Visualización jerárquica
- **Análisis de impacto**: Si un servicio falla, qué otros se ven afectados

### 4. Integraciones
- **Con Riesgos**: Vincular riesgos a servicios
- **Con Incidentes**: Asociar incidentes a servicios
- **Con No Conformidades**: Relacionar NCs con servicios
- **Con SOA**: Controles aplicables a servicios

## Estructura de Rutas

```
/servicios/                          # Listar servicios
/servicios/new                       # Crear servicio
/servicios/<id>                      # Ver detalle
/servicios/<id>/edit                 # Editar
/servicios/<id>/delete              # Eliminar
/servicios/<id>/assets              # Gestionar activos del servicio
/servicios/<id>/assets/add          # Añadir activo
/servicios/<id>/assets/<asset_id>/remove  # Quitar activo
/servicios/<id>/dependencies        # Ver dependencias
/servicios/<id>/impact-analysis     # Análisis de impacto

# Vistas especiales
/servicios/map                      # Mapa de servicios
/servicios/dashboard               # Dashboard de servicios
```

## Modificaciones en Assets

### Actualizar modelo Asset
```python
# Agregar relación en Asset
services = db.relationship('Service',
                          secondary=service_asset_association,
                          backref=db.backref('assets', lazy='dynamic'))
```

### Actualizar vista de activos
- Agregar filtro por servicio
- Mostrar servicios asociados en la lista
- Incluir servicios en formulario de creación/edición

## Templates a Crear

### Servicios
1. `templates/services/index.html` - Listado
2. `templates/services/create.html` - Formulario crear
3. `templates/services/detail.html` - Detalle con tabs
4. `templates/services/edit.html` - Formulario editar
5. `templates/services/map.html` - Mapa de servicios
6. `templates/services/dashboard.html` - Dashboard

### Componentes
1. `templates/services/_service_card.html` - Card reutilizable
2. `templates/services/_asset_list.html` - Lista de activos
3. `templates/services/_dependency_tree.html` - Árbol de dependencias

## Migraciones

### Migración 1: Crear tabla services
```sql
CREATE TABLE services (
    id SERIAL PRIMARY KEY,
    service_code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    service_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'ACTIVE',
    service_owner_id INTEGER REFERENCES users(id),
    technical_manager_id INTEGER REFERENCES users(id),
    criticality INTEGER DEFAULT 5,
    required_availability FLOAT,
    rto INTEGER,
    rpo INTEGER,
    operating_hours VARCHAR(100),
    max_users INTEGER,
    department VARCHAR(100),
    annual_cost FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_id INTEGER REFERENCES users(id),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by_id INTEGER REFERENCES users(id),
    notes TEXT
);
```

### Migración 2: Crear tabla service_asset_association
```sql
CREATE TABLE service_asset_association (
    service_id INTEGER REFERENCES services(id) ON DELETE CASCADE,
    asset_id INTEGER REFERENCES assets(id) ON DELETE CASCADE,
    role VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (service_id, asset_id)
);
```

### Migración 3: Crear tabla service_dependencies
```sql
CREATE TABLE service_dependencies (
    id SERIAL PRIMARY KEY,
    service_id INTEGER REFERENCES services(id) ON DELETE CASCADE,
    depends_on_service_id INTEGER REFERENCES services(id) ON DELETE CASCADE,
    dependency_type VARCHAR(50),
    description TEXT,
    CONSTRAINT no_self_dependency CHECK (service_id != depends_on_service_id)
);
```

## Fases de Implementación

### Fase 1: Modelo y Migraciones (1-2 días)
- [ ] Crear modelos Service, ServiceDependency
- [ ] Crear tabla de asociación service_asset_association
- [ ] Crear migraciones
- [ ] Ejecutar y verificar migraciones

### Fase 2: CRUD Básico de Servicios (2-3 días)
- [ ] Crear blueprint services
- [ ] Implementar rutas CRUD
- [ ] Crear templates básicos
- [ ] Implementar validaciones

### Fase 3: Asociación Activos-Servicios (2 días)
- [ ] Actualizar modelo Asset
- [ ] Crear vistas para asociar/desasociar activos
- [ ] Actualizar formularios de activos
- [ ] Implementar búsqueda y filtrado

### Fase 4: Dependencias y Visualizaciones (2-3 días)
- [ ] Implementar gestión de dependencias
- [ ] Crear mapa de servicios (visualización)
- [ ] Implementar análisis de impacto
- [ ] Dashboard de servicios

### Fase 5: Integraciones (2 días)
- [ ] Integrar con módulo de riesgos
- [ ] Integrar con incidentes
- [ ] Integrar con no conformidades
- [ ] Actualizar reportes existentes

### Fase 6: Testing y Documentación (1-2 días)
- [ ] Pruebas funcionales
- [ ] Documentación de usuario
- [ ] Ajustes y correcciones

## Estimación Total: 10-14 días

## Beneficios Esperados

1. **Visión de negocio**: Ver activos desde perspectiva de servicios
2. **Análisis de impacto**: Identificar dependencias críticas
3. **Gestión de incidentes**: Correlacionar incidentes con servicios
4. **Cumplimiento ISO**: Mejor trazabilidad de activos
5. **Decisiones informadas**: Priorización basada en criticidad de servicios

## Consideraciones Técnicas

- **Performance**: Indexar service_code, service_type, status
- **Caché**: Implementar caché para mapas de dependencias
- **Validaciones**: Prevenir dependencias circulares
- **Permisos**: Control de acceso por servicio
- **Auditoría**: Log de todos los cambios
