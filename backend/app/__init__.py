"""
Application factory and Flask application setup for SkillGap.

This module exposes the `create_app` factory used to construct and configure
Flask, initialize the database connection, and register API blueprints.
"""

import logging

from flask import Flask, jsonify
from flask_cors import CORS

from .database.connection import init_db
from config import Config


def _parse_frontend_origins(raw_value):
    """Convert configured frontend origins into Flask-CORS format."""
    if not raw_value or raw_value == "*":
        return "*"

    origins = [origin.strip() for origin in raw_value.split(",") if origin.strip()]
    return origins or "*"


def create_app(config_class=Config):
    """Create and configure the Flask application instance."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    cors_origins = _parse_frontend_origins(app.config.get("FRONTEND_ORIGINS"))
    CORS(app, resources={
        r"/api/*": {"origins": cors_origins},
        r"/health": {"origins": cors_origins}
    })

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    with app.app_context():
        init_db(app.config["MONGO_URI"])

    from .routes.auth_routes import auth_bp
    from .routes.student_routes import student_bp
    from .routes.admin_routes import admin_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(student_bp, url_prefix="/api/student")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"error": "Not Found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal Server Error"}), 500

    @app.route("/health")
    def health_check():
        return jsonify({"status": "healthy", "service": "SkillGap AI Analyzer"})

    return app
