from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_required, current_user
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash
from datetime import datetime
import os
from config import config

def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__,
                template_folder='app/templates',
                static_folder='app/static')

    # Configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])

    # Initialize extensions
    from models import db
    db.init_app(app)

    migrate = Migrate(app, db)
    csrf = CSRFProtect(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, inicia sesión para acceder a esta página.'

    # Import models after db initialization
    from models import User, Role, DocumentType, AssetType, AssetCategory, DepreciationPeriod

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Import and register blueprints
    from app.blueprints.auth import auth_bp
    from app.blueprints.dashboard import dashboard_bp
    from app.blueprints.soa import soa_bp
    from app.blueprints.risks import risks_bp
    from app.blueprints.documents import documents_bp
    from app.blueprints.incidents import incidents_bp
    from app.blueprints.audits import audits_bp
    from app.blueprints.nonconformities import nonconformities_bp
    from app.blueprints.tasks import tasks_bp
    from app.blueprints.training import training_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.assets import assets_bp
    from app.blueprints.services import services_bp
    from app.blueprints.changes import changes_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/')
    app.register_blueprint(soa_bp, url_prefix='/soa')
    app.register_blueprint(risks_bp, url_prefix='/riesgos')
    app.register_blueprint(documents_bp, url_prefix='/documentos')
    app.register_blueprint(incidents_bp, url_prefix='/incidentes')
    app.register_blueprint(audits_bp, url_prefix='/auditorias')
    app.register_blueprint(nonconformities_bp, url_prefix='/no-conformidades')
    app.register_blueprint(tasks_bp, url_prefix='/tareas')
    app.register_blueprint(training_bp, url_prefix='/formacion')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(assets_bp, url_prefix='/activos')
    app.register_blueprint(services_bp, url_prefix='/servicios')
    app.register_blueprint(changes_bp, url_prefix='/cambios')

    # Root route
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
        return redirect(url_for('auth.login'))

    # Health check route for containers
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}, 200

    # Initialize database and create initial data
    with app.app_context():
        db.create_all()

        # Create default roles if they don't exist
        if not Role.query.first():
            roles = [
                Role(name='admin', description='Administrador del Sistema'),
                Role(name='ciso', description='Responsable de Seguridad (CISO)'),
                Role(name='auditor', description='Auditor Interno'),
                Role(name='owner', description='Propietario de Proceso'),
                Role(name='user', description='Usuario General')
            ]
            for role in roles:
                db.session.add(role)

            db.session.commit()

            # Create default admin user
            admin_role = Role.query.filter_by(name='admin').first()
            admin_user = User(
                username='admin',
                email='admin@isms.local',
                first_name='Administrador',
                last_name='del Sistema',
                role_id=admin_role.id,
                is_active=True,
                must_change_password=True,  # Forzar cambio de contraseña en primer login
                created_at=datetime.utcnow()
            )
            # Usar el método set_password que inicializa password_changed_at
            admin_user.set_password('admin123')

            db.session.add(admin_user)
            db.session.commit()

        # Create default document types if they don't exist
        if not DocumentType.query.first():
            document_types = [
                DocumentType(
                    code='policy',
                    name='Política',
                    description='Documentos de nivel estratégico que establecen las directrices generales de la organización',
                    review_period_months=24,
                    requires_approval=True,
                    approval_workflow='management',
                    icon='fa-gavel',
                    color='danger',
                    is_active=True,
                    order=1
                ),
                DocumentType(
                    code='procedure',
                    name='Procedimiento',
                    description='Descripciones detalladas de los procesos operativos de la organización',
                    review_period_months=12,
                    requires_approval=True,
                    approval_workflow='responsible',
                    icon='fa-list-ol',
                    color='primary',
                    is_active=True,
                    order=2
                ),
                DocumentType(
                    code='instruction',
                    name='Instrucción',
                    description='Guías específicas para la realización de tareas concretas',
                    review_period_months=12,
                    requires_approval=False,
                    approval_workflow='technical',
                    icon='fa-book',
                    color='info',
                    is_active=True,
                    order=3
                ),
                DocumentType(
                    code='record',
                    name='Registro',
                    description='Documentos que evidencian la ejecución de actividades',
                    review_period_months=6,
                    requires_approval=False,
                    approval_workflow='automatic',
                    icon='fa-folder-open',
                    color='success',
                    is_active=True,
                    order=4
                ),
                DocumentType(
                    code='minutes',
                    name='Acta',
                    description='Registros de reuniones y decisiones tomadas',
                    review_period_months=3,
                    requires_approval=False,
                    approval_workflow='automatic',
                    icon='fa-clipboard',
                    color='warning',
                    is_active=True,
                    order=5
                ),
                DocumentType(
                    code='form',
                    name='Formulario',
                    description='Plantillas para la recopilación de información',
                    review_period_months=12,
                    requires_approval=False,
                    approval_workflow='technical',
                    icon='fa-file-alt',
                    color='secondary',
                    is_active=True,
                    order=6
                ),
                DocumentType(
                    code='manual',
                    name='Manual',
                    description='Documentos de referencia y consulta',
                    review_period_months=24,
                    requires_approval=True,
                    approval_workflow='management',
                    icon='fa-book-open',
                    color='dark',
                    is_active=True,
                    order=7
                ),
                DocumentType(
                    code='report',
                    name='Informe',
                    description='Documentos de análisis y resultados',
                    review_period_months=6,
                    requires_approval=False,
                    approval_workflow='automatic',
                    icon='fa-chart-bar',
                    color='info',
                    is_active=True,
                    order=8
                )
            ]
            for doc_type in document_types:
                db.session.add(doc_type)

            db.session.commit()

        # Create default asset types if they don't exist
        if not AssetType.query.first():
            asset_types = [
                # HARDWARE
                AssetType(code='hw-server', name='Servidor', description='Servidores físicos o virtuales',
                         category=AssetCategory.HARDWARE, icon='fa-server', color='primary', order=1),
                AssetType(code='hw-workstation', name='Estación de Trabajo', description='Ordenadores de escritorio y portátiles',
                         category=AssetCategory.HARDWARE, icon='fa-desktop', color='primary', order=2),
                AssetType(code='hw-mobile', name='Dispositivo Móvil', description='Smartphones y tablets',
                         category=AssetCategory.HARDWARE, icon='fa-mobile-alt', color='primary', order=3),
                AssetType(code='hw-network', name='Equipo de Red', description='Routers, switches, firewalls',
                         category=AssetCategory.HARDWARE, icon='fa-network-wired', color='primary', order=4),
                AssetType(code='hw-storage', name='Almacenamiento', description='Dispositivos de almacenamiento',
                         category=AssetCategory.HARDWARE, icon='fa-hdd', color='primary', order=5),
                AssetType(code='hw-peripheral', name='Periférico', description='Impresoras, escáneres, etc.',
                         category=AssetCategory.HARDWARE, icon='fa-print', color='primary', order=6),

                # SOFTWARE
                AssetType(code='sw-os', name='Sistema Operativo', description='Sistemas operativos',
                         category=AssetCategory.SOFTWARE, icon='fa-window-restore', color='info', order=1),
                AssetType(code='sw-app', name='Aplicación', description='Software de aplicación',
                         category=AssetCategory.SOFTWARE, icon='fa-laptop-code', color='info', order=2),
                AssetType(code='sw-database', name='Base de Datos', description='Sistemas de gestión de bases de datos',
                         category=AssetCategory.SOFTWARE, icon='fa-database', color='info', order=3),
                AssetType(code='sw-security', name='Software de Seguridad', description='Antivirus, firewalls, etc.',
                         category=AssetCategory.SOFTWARE, icon='fa-shield-alt', color='info', order=4),
                AssetType(code='sw-middleware', name='Middleware', description='Software intermedio',
                         category=AssetCategory.SOFTWARE, icon='fa-cogs', color='info', order=5),

                # INFORMATION
                AssetType(code='inf-customer', name='Datos de Clientes', description='Información de clientes',
                         category=AssetCategory.INFORMATION, icon='fa-users', color='warning', order=1),
                AssetType(code='inf-financial', name='Datos Financieros', description='Información financiera y contable',
                         category=AssetCategory.INFORMATION, icon='fa-euro-sign', color='warning', order=2),
                AssetType(code='inf-personal', name='Datos Personales', description='Información personal (RGPD)',
                         category=AssetCategory.INFORMATION, icon='fa-user-shield', color='warning', order=3),
                AssetType(code='inf-technical', name='Documentación Técnica', description='Documentación técnica y de sistemas',
                         category=AssetCategory.INFORMATION, icon='fa-file-code', color='warning', order=4),
                AssetType(code='inf-business', name='Información de Negocio', description='Datos de procesos de negocio',
                         category=AssetCategory.INFORMATION, icon='fa-briefcase', color='warning', order=5),

                # SERVICES
                AssetType(code='srv-cloud', name='Servicio Cloud', description='Servicios en la nube',
                         category=AssetCategory.SERVICES, icon='fa-cloud', color='success', order=1),
                AssetType(code='srv-email', name='Correo Electrónico', description='Servicios de correo',
                         category=AssetCategory.SERVICES, icon='fa-envelope', color='success', order=2),
                AssetType(code='srv-web', name='Servicio Web', description='Sitios y aplicaciones web',
                         category=AssetCategory.SERVICES, icon='fa-globe', color='success', order=3),
                AssetType(code='srv-telecom', name='Telecomunicaciones', description='Servicios de telecomunicaciones',
                         category=AssetCategory.SERVICES, icon='fa-phone', color='success', order=4),
                AssetType(code='srv-support', name='Soporte Técnico', description='Servicios de soporte',
                         category=AssetCategory.SERVICES, icon='fa-life-ring', color='success', order=5),

                # PEOPLE
                AssetType(code='ppl-employee', name='Empleado', description='Personal interno',
                         category=AssetCategory.PEOPLE, icon='fa-user-tie', color='secondary', order=1),
                AssetType(code='ppl-contractor', name='Contratista', description='Personal externo',
                         category=AssetCategory.PEOPLE, icon='fa-user-clock', color='secondary', order=2),
                AssetType(code='ppl-admin', name='Administrador', description='Administradores de sistemas',
                         category=AssetCategory.PEOPLE, icon='fa-user-cog', color='secondary', order=3),

                # FACILITIES
                AssetType(code='fac-datacenter', name='Centro de Datos', description='Salas de servidores',
                         category=AssetCategory.FACILITIES, icon='fa-building', color='dark', order=1),
                AssetType(code='fac-office', name='Oficina', description='Espacios de oficina',
                         category=AssetCategory.FACILITIES, icon='fa-city', color='dark', order=2),
                AssetType(code='fac-utility', name='Servicios Básicos', description='Electricidad, climatización, etc.',
                         category=AssetCategory.FACILITIES, icon='fa-bolt', color='dark', order=3),
            ]
            for asset_type in asset_types:
                db.session.add(asset_type)

            db.session.commit()

        # Create default depreciation periods if they don't exist
        if not DepreciationPeriod.query.first():
            depreciation_periods = [
                DepreciationPeriod(
                    category=AssetCategory.HARDWARE,
                    years=4,
                    description='Equipos informáticos: servidores, ordenadores, dispositivos móviles, etc.',
                    method='linear',
                    residual_value_percentage=10.0
                ),
                DepreciationPeriod(
                    category=AssetCategory.SOFTWARE,
                    years=3,
                    description='Licencias de software y aplicaciones',
                    method='linear',
                    residual_value_percentage=0.0
                ),
                DepreciationPeriod(
                    category=AssetCategory.INFORMATION,
                    years=0,
                    description='La información no se deprecia (valor constante)',
                    method='linear',
                    residual_value_percentage=100.0
                ),
                DepreciationPeriod(
                    category=AssetCategory.SERVICES,
                    years=1,
                    description='Servicios y suscripciones (normalmente anuales)',
                    method='linear',
                    residual_value_percentage=0.0
                ),
                DepreciationPeriod(
                    category=AssetCategory.PEOPLE,
                    years=0,
                    description='Las personas no se deprecian (valor no aplicable)',
                    method='linear',
                    residual_value_percentage=100.0
                ),
                DepreciationPeriod(
                    category=AssetCategory.FACILITIES,
                    years=30,
                    description='Instalaciones y edificios',
                    method='linear',
                    residual_value_percentage=20.0
                ),
            ]
            for period in depreciation_periods:
                db.session.add(period)

            db.session.commit()

    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)