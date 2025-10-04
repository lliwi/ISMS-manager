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
    app = Flask(__name__)

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
    from models import User, Role, DocumentType

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Import and register blueprints
    from blueprints.auth import auth_bp
    from blueprints.dashboard import dashboard_bp
    from blueprints.soa import soa_bp
    from blueprints.risks import risks_bp
    from blueprints.documents import documents_bp
    from blueprints.incidents import incidents_bp
    from blueprints.audits import audits_bp
    from blueprints.nonconformities import nonconformities_bp
    from blueprints.tasks import tasks_bp
    from blueprints.training import training_bp
    from blueprints.admin import admin_bp
    from blueprints.auxiliary import auxiliary_bp

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
    app.register_blueprint(auxiliary_bp, url_prefix='/auxiliares')

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

    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)