"""
Authentication HTTP routes used by the frontend.

This blueprint exposes `/signup` and `/login` endpoints. Validation is
minimal and most business logic lives in `AuthService`.
"""

from flask import Blueprint, request, jsonify
from app.services.auth_service import AuthService

auth_bp = Blueprint('auth_bp', __name__)


@auth_bp.route('/signup', methods=['POST'])
def signup():
    """Register a new student.

    Expected JSON fields: `name`, `email`, `password`. Optional: `career_goal`,
    `profile_photo`.
    """
    data = request.get_json() or {}

    # Basic presence validation for required fields
    if not data or not data.get('email') or not data.get('password') or not data.get('name'):
        return jsonify({"error": "Missing required fields (name, email, password)"}), 400

    try:
        auth_service = AuthService()
        response, status_code = auth_service.register_user(
            name=data.get('name'),
            email=data.get('email'),
            password=data.get('password'),
            career_goal=data.get('career_goal'), # Optional at signup
            profile_photo=data.get('profile_photo')
        )
        return jsonify(response), status_code
    except Exception as e:
        # Log unexpected server-side errors and return a 500 for debugging.
        import logging

        logging.exception('Error during signup: %s', e)
        return jsonify({'error': 'Internal server error during signup'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate an existing user and return a JWT on success."""
    data = request.get_json() or {}

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Missing email or password"}), 400

    auth_service = AuthService()
    response, status_code = auth_service.login_user(
        email=data.get('email'),
        password=data.get('password')
    )

    return jsonify(response), status_code
