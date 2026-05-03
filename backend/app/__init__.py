"""
Flask application factory for the backend.

The `create_app` factory follows Flask best practices: it creates and
configures the Flask application, registers blueprints and extensions, and
initializes the database connection within the application context.

This keeps module import time free of side-effects so WSGI servers can import
`backend.app:create_app` or the `app` variable from `backend/app.py` safely.
"""

from flask import Flask, jsonify
from flask_cors import CORS
from .database.connection import init_db
from config import Config
import logging


def create_app(config_class=Config):
    # Initialize Flask app
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable CORS (for local development the frontend may be served separately)
    CORS(app)

    # Initialize Logging with a simple, readable format
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Initialize DB Connection wrapped in app context. The function will
    # create the MongoDB client and attach it to the application state.
    with app.app_context():
        init_db(app.config['MONGO_URI'])

    # Register blueprints after app and DB are ready
    from .routes.auth_routes import auth_bp
    from .routes.student_routes import student_bp
    from .routes.admin_routes import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(student_bp, url_prefix='/api/student')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    # Global Error Handlers return consistent JSON responses for common errors
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({'error': 'Not Found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal Server Error'}), 500

    @app.route('/health')
    def health_check():
        return jsonify({"status": "healthy", "service": "SkillGap AI Analyzer"})

    return app
