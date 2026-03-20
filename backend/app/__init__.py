from flask import Flask, jsonify
from flask_cors import CORS
from .database.connection import init_db
from config import Config
import logging

def create_app(config_class=Config):
    # Initialize Flask app
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS
    CORS(app)
    
    # Initialize Logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Initialize DB Connection wrapped in app context
    with app.app_context():
        init_db(app.config['MONGO_URI'])
        
    # Register blueprints (To be imported and assigned below)
    from .routes.auth_routes import auth_bp
    from .routes.student_routes import student_bp
    from .routes.admin_routes import admin_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(student_bp, url_prefix='/api/student')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    # Global Error Handlers
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
