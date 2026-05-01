"""
Application factory and Flask application setup for SkillGap.

This module exposes the `create_app` factory used to construct and configure
the Flask application. Using a factory function keeps configuration and
initialization explicit and makes the code easier to test.
"""

import logging

from flask import Flask, jsonify
from flask_cors import CORS
from .database.connection import init_db
from config import Config


def _parse_frontend_origins(raw_value):
    """Convert the configured frontend origin string into a Flask-CORS value."""
    if not raw_value or raw_value == "*":
        return "*"

    origins = [origin.strip() for origin in raw_value.split(",") if origin.strip()]
    return origins or "*"


def create_app(config_class=Config):
    """Create and configure the Flask application.

    Args:
        config_class: A configuration class (defaults to `Config`) that
            provides settings consumed via `app.config.from_object`.

    Returns:
        A configured Flask `app` instance ready to be served.
    """

    # Initialize Flask app and load configuration
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable Cross-Origin Resource Sharing for browser clients. In production
    # this can be narrowed via FRONTEND_ORIGINS, while keeping wildcard support
    # for local development.
    cors_origins = _parse_frontend_origins(app.config.get('FRONTEND_ORIGINS'))
    CORS(app, resources={r"/api/*": {"origins": cors_origins}, r"/health": {"origins": cors_origins}})

    # Initialize logging for the application; keep the format consistent
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Initialize DB Connection wrapped in app context so extensions can access
    # `current_app.config` if needed during initialization.
    with app.app_context():
        init_db(app.config['MONGO_URI'])

    # Register blueprints for modular route organization. Importing inside the
    # function avoids circular imports at module import time.
    from .routes.auth_routes import auth_bp
    from .routes.student_routes import student_bp
    from .routes.admin_routes import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(student_bp, url_prefix='/api/student')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    # Global Error Handlers provide consistent JSON responses for common
    # HTTP error codes used by the frontend and tests.
    @app.errorhandler(404)
    def not_found_error(error):
        """Return a JSON payload for 404 Not Found errors."""
        return jsonify({'error': 'Not Found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Return a JSON payload for 500 Internal Server errors."""
        return jsonify({'error': 'Internal Server Error'}), 500

    @app.route('/health')
    def health_check():
        """Lightweight health-check endpoint used by orchestration and tests."""
        return jsonify({"status": "healthy", "service": "SkillGap AI Analyzer"})

    return app
