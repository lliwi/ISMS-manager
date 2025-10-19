import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class"""

    # Flask Settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Database Settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://isms:isms@localhost/isms_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    # Session Settings
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = os.environ.get('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(seconds=int(os.environ.get('PERMANENT_SESSION_LIFETIME', '3600')))
    SESSION_COOKIE_NAME = 'isms_session'

    # Email Settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'localhost')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '25'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'False').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@isms.local')
    MAIL_MAX_EMAILS = int(os.environ.get('MAIL_MAX_EMAILS', '100'))

    # Task Management Settings
    TASK_AUTO_GENERATION_ENABLED = os.environ.get('TASK_AUTO_GENERATION_ENABLED', 'True').lower() == 'true'
    TASK_NOTIFICATION_ENABLED = os.environ.get('TASK_NOTIFICATION_ENABLED', 'True').lower() == 'true'

    # File Upload Settings
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', '16777216'))  # 16MB
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'}

    # Application Settings
    APP_NAME = os.environ.get('APP_NAME', 'ISMS Manager')
    APP_VERSION = os.environ.get('APP_VERSION', '1.0.0')
    ITEMS_PER_PAGE = int(os.environ.get('ITEMS_PER_PAGE', '20'))

    # Security Settings
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    WTF_CSRF_SSL_STRICT = False
    WTF_CSRF_CHECK_DEFAULT = True

    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/isms.log')

    # AI Document Verification Settings
    AI_VERIFICATION_ENABLED = os.environ.get('AI_VERIFICATION_ENABLED', 'False').lower() == 'true'
    AI_PROVIDER = os.environ.get('AI_PROVIDER', 'ollama')  # ollama, openai, deepseek
    AI_MODEL = os.environ.get('AI_MODEL', 'llama3:8b')
    AI_API_KEY = os.environ.get('AI_API_KEY', '')
    AI_BASE_URL = os.environ.get('AI_BASE_URL', 'http://localhost:11434')
    AI_TIMEOUT = int(os.environ.get('AI_TIMEOUT', '120'))
    KNOWLEDGE_BASE_PATH = os.environ.get('KNOWLEDGE_BASE_PATH', 'knowledge')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

    # Override database for development - use localhost for local development
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL', 'postgresql://isms:isms_secure_password@localhost:5432/isms_db')

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = False

    # Use in-memory SQLite for tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

    # Enhanced security for production
    # Set SESSION_COOKIE_SECURE=True in .env when using HTTPS
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    WTF_CSRF_SSL_STRICT = False

    # Production database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL environment variable is required in production")

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}