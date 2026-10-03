import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
basedir = Path(__file__).resolve().parent
load_dotenv(basedir / '.env')


class Config:
    """Base configuration with default settings."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'blind-assist-secret-key-development-2026-safe')
    
    # Instance directory and Database URI
    INSTANCE_DIR = basedir / 'instance'
    INSTANCE_DIR.mkdir(exist_ok=True)
    
    # Ensure default database path uses absolute URI for SQLite
    DEFAULT_DB_PATH = (INSTANCE_DIR / 'blind_assist.db').as_posix()
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f'sqlite:///{DEFAULT_DB_PATH}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Uploads configuration
    UPLOAD_FOLDER = basedir / 'uploads'
    UPLOAD_FOLDER.mkdir(exist_ok=True)
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16 MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
    
    # Demo and AI options
    DEMO_MODE = os.environ.get('DEMO_MODE', 'true').lower() in ('true', '1', 'yes', 't')
    TESSERACT_CMD = os.environ.get('TESSERACT_CMD', None)
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', None)
    
    # App info
    APP_NAME = "Blind Assist"
    APP_TAGLINE = "Smart Assistance for Independent Living"


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing environment configuration."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    TESTING = False


# Map environment names to configuration classes
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
