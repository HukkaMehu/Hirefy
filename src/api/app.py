"""Flask application factory"""

from flask import Flask, jsonify
from flask_cors import CORS
from .config import get_config
from src.database import init_database


def create_app(config_name: str = None) -> Flask:
    """Create and configure the Flask application.
    
    Args:
        config_name: Configuration environment name
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    config_class = get_config(config_name)
    app.config.from_object(config_class)
    
    # Ensure directories exist first
    config_instance = config_class()
    config_instance.ensure_directories()
    
    # Validate configuration
    try:
        config_class.validate_config()
    except ValueError as e:
        print(f"⚠️  Configuration warning: {e}")
    
    # Initialize CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Initialize database
    init_database(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'AI Recruitment Verification Platform'
        })
    
    return app


def register_blueprints(app: Flask) -> None:
    """Register Flask blueprints.
    
    Args:
        app: Flask application instance
    """
    from .routes import verifications_bp, chat_bp
    from .routes.documents import documents_bp
    from .routes.ai_analysis import ai_analysis_bp
    from .routes.transcripts import transcripts_bp
    
    # Register API blueprints
    app.register_blueprint(verifications_bp, url_prefix='/api/verifications')
    app.register_blueprint(documents_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(ai_analysis_bp, url_prefix='/api/ai')
    app.register_blueprint(transcripts_bp, url_prefix='/api')
    
    print("✅ Blueprints registered")


def register_error_handlers(app: Flask) -> None:
    """Register error handlers.
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad Request',
            'message': str(error)
        }), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }), 500
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        return jsonify({
            'error': 'File Too Large',
            'message': 'The uploaded file exceeds the maximum size of 10MB'
        }), 413
