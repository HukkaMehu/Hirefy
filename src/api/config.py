"""Configuration management for Flask application"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get project root directory (parent of src/api)
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Config:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Database settings
    _default_db_path = BASE_DIR / 'data' / 'verification_platform.db'
    # Convert Windows backslashes to forward slashes for SQLite URI
    _db_uri_path = str(_default_db_path).replace('\\', '/')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{_db_uri_path}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.getenv('SQLALCHEMY_ECHO', 'False').lower() == 'true'
    
    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
    GITHUB_API_TOKEN = os.getenv('GITHUB_API_TOKEN')
    
    # SMTP Configuration (for email verification)
    SMTP_HOST = os.getenv('SMTP_HOST')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    SMTP_FROM_EMAIL = os.getenv('SMTP_FROM_EMAIL')
    SMTP_FROM_NAME = os.getenv('SMTP_FROM_NAME', 'Verification Platform')
    
    # File upload settings
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB max file size
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', str(BASE_DIR / 'data' / 'uploads'))
    ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'heic'}
    
    # Transcript and document storage
    TRANSCRIPT_OUTPUT_DIR = os.getenv('TRANSCRIPT_OUTPUT_DIR', str(BASE_DIR / 'data' / 'transcripts'))
    DOCUMENT_STORAGE_DIR = os.getenv('DOCUMENT_STORAGE_DIR', str(BASE_DIR / 'data' / 'documents'))
    
    # Verification settings
    VERIFICATION_TIMEOUT_HOURS = int(os.getenv('VERIFICATION_TIMEOUT_HOURS', '24'))
    
    # CORS settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://localhost:3000').split(',')
    
    @staticmethod
    def validate_config():
        """Validate that required configuration is present"""
        required_keys = ['OPENAI_API_KEY']
        missing_keys = [key for key in required_keys if not os.getenv(key)]
        
        if missing_keys:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_keys)}")
        
        return True
    
    def ensure_directories(self):
        """Ensure all required directories exist"""
        directories = [
            self.UPLOAD_FOLDER,
            self.TRANSCRIPT_OUTPUT_DIR,
            self.DOCUMENT_STORAGE_DIR,
            BASE_DIR / 'data'  # Base data directory
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
        
        # Ensure database directory exists
        if self.SQLALCHEMY_DATABASE_URI.startswith('sqlite:///'):
            db_path = self.SQLALCHEMY_DATABASE_URI.replace('sqlite:///', '')
            db_dir = Path(db_path).parent
            db_dir.mkdir(parents=True, exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    
    @staticmethod
    def validate_config():
        """Additional validation for production"""
        Config.validate_config()
        
        # Ensure secret key is not default
        if Config.SECRET_KEY == 'dev-secret-key-change-in-production':
            raise ValueError("SECRET_KEY must be set to a secure value in production")
        
        return True


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env: str = None) -> Config:
    """Get configuration based on environment.
    
    Args:
        env: Environment name (development, production, testing)
        
    Returns:
        Configuration class
    """
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    
    return config.get(env, config['default'])
