from flask import Blueprint, request, jsonify
from app.services.auth_service import AuthService

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """Register a new student."""
    data = request.get_json()
    
    # Validation
    if not data or not data.get('email') or not data.get('password') or not data.get('name'):
        return jsonify({"error": "Missing required fields (name, email, password)"}), 400
        
    auth_service = AuthService()
    response, status_code = auth_service.register_user(
        name=data.get('name'),
        email=data.get('email'),
        password=data.get('password'),
        career_goal=data.get('career_goal') # Optional at signup
    )
    
    return jsonify(response), status_code

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate an existing user."""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Missing email or password"}), 400
        
    auth_service = AuthService()
    response, status_code = auth_service.login_user(
        email=data.get('email'),
        password=data.get('password')
    )
    
    return jsonify(response), status_code
