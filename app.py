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
    from models import User, Role

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
                password_hash=generate_password_hash('admin123'),
                role_id=admin_role.id,
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.session.add(admin_user)
            db.session.commit()

    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)