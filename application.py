from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_required, current_user
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
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

    # Initialize Flask-Mail
    mail = Mail(app)

    # Make mail available globally for notification service
    app.extensions['mail'] = mail

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
    from app.risks import bp as risks_bp
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

    # Initialize task scheduler within app context
    with app.app_context():
        # Create all database tables
        db.create_all()

        # Seed initial data (admin user, roles, etc.)
        from utils.seed_data import seed_initial_data
        seed_initial_data()

        # Initialize task scheduler
        try:
            from app.services.scheduler_service import init_scheduler
            scheduler = init_scheduler(app)
            # Store scheduler in app context for access in routes
            app.extensions['task_scheduler'] = scheduler
        except Exception as e:
            print(f"Warning: Task scheduler not initialized: {str(e)}")

    # Register CLI commands for risk management
    from app.risks.commands import init_app as init_risks_commands
    init_risks_commands(app)

    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)