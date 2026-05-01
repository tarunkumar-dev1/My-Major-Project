"""
Authentication helpers and user account management service.

This module encapsulates common authentication primitives (password hashing,
JWT issuance/verification) and user lifecycle operations such as registration
and login. Routes import `AuthService` for high-level operations and use the
`token_required` decorator to protect endpoints.
"""

import jwt
import bcrypt
import datetime
import re
from functools import wraps
from flask import request, jsonify, current_app
from app.database.connection import get_db


class AuthService:
    """Service exposing registration, login and account management helpers."""

    def __init__(self):
        self.db = get_db()
        self.users_collection = self.db['users']

    def generate_token(self, user_id):
        """Generate a JWT token valid for 24 hours.

        The token's `sub` claim contains the `user_id` and can be used by the
        `token_required` decorator to identify the current user.
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
                'iat': datetime.datetime.utcnow(),
                'sub': str(user_id)
            }
            return jwt.encode(payload, current_app.config['JWT_SECRET'], algorithm='HS256')
        except Exception as e:
            raise Exception(f"Error generating token: {str(e)}")

    def hash_password(self, password):
        """Create a bcrypt salted hash for `password`."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt)

    def is_valid_gmail(self, email):
        """Validate the email is a Gmail address. Returns boolean."""
        if not email:
            return False
        return bool(re.fullmatch(r'[A-Za-z0-9._%+-]+@gmail\.com', email.strip(), re.IGNORECASE))

    def is_strong_password(self, password):
        """Enforce a minimal password strength policy used at registration."""
        if not password or len(password) < 8:
            return False
        has_letter = re.search(r'[A-Za-z]', password)
        has_digit = re.search(r'\d', password)
        has_symbol = re.search(r'[^A-Za-z0-9]', password)
        return bool(has_letter and has_digit and has_symbol)

    def verify_password(self, password, hashed_password):
        """Verify a plaintext password against a stored bcrypt hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

    def register_user(self, name, email, password, career_goal=None, profile_photo=None):
        """Register a new user with basic validation and return token.

        Returns `(payload, status_code)` to be returned directly by routes.
        """
        if not self.is_valid_gmail(email):
            return {"error": "Only valid Gmail addresses are allowed"}, 400

        if not self.is_strong_password(password):
            return {"error": "Password must be at least 8 characters long and include letters, numbers, and symbols"}, 400

        existing_user = self.users_collection.find_one({"email": email})
        if existing_user:
            return {"error": "Email already exists"}, 400

        hashed_password = self.hash_password(password)

        new_user = {
            "name": name,
            "email": email,
            "hashed_password": hashed_password,
            "skills": [],
            "career_goal": career_goal,
            "completed_skills": [],
            "readiness_score": 0,
            "preferences": {
                "email_notifications": True,
                "public_profile": False,
                "two_factor_enabled": False,
            },
            "profile_photo": profile_photo,
            "created_at": datetime.datetime.utcnow()
        }

        result = self.users_collection.insert_one(new_user)
        token = self.generate_token(result.inserted_id)

        return {
            "message": "User registered successfully",
            "token": token,
            "user": {
                "id": str(result.inserted_id),
                "name": name,
                "email": email
            }
        }, 201

    def login_user(self, email, password):
        """Authenticate a user and return a fresh JWT on success."""
        if not self.is_valid_gmail(email):
            return {"error": "Only valid Gmail addresses are allowed"}, 400

        user = self.users_collection.find_one({"email": email})

        if not user or not self.verify_password(password, user["hashed_password"]):
            return {"error": "Invalid email or password"}, 401

        token = self.generate_token(user["_id"])

        # Store login activity for admin analytics and update user counters.
        login_events = self.db["login_events"]
        login_events.insert_one({
            "user_id": str(user["_id"]),
            "email": email,
            "logged_in_at": datetime.datetime.utcnow()
        })
        self.users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"last_login": datetime.datetime.utcnow()}, "$inc": {"login_count": 1}}
        )

        return {
            "message": "Login successful",
            "token": token,
            "user": {
                "id": str(user["_id"]),
                "name": user["name"],
                "email": user["email"]
            }
        }, 200

    def change_password(self, user_id, current_password, new_password):
        """Change a user's password after validating the current password.

        Note: `user_id` is expected to be the internal `_id` value used by
        MongoDB. Routes should pass `ObjectId(...)` where appropriate.
        """
        user = self.users_collection.find_one({"_id": user_id})
        if not user:
            return {"error": "User not found"}, 404

        if not current_password or not new_password:
            return {"error": "Current password and new password are required"}, 400

        if not self.verify_password(current_password, user["hashed_password"]):
            return {"error": "Current password is incorrect"}, 400

        if not self.is_strong_password(new_password):
            return {"error": "New password must be at least 8 characters long and include letters, numbers, and symbols"}, 400

        new_hash = self.hash_password(new_password)
        self.users_collection.update_one(
            {"_id": user_id},
            {"$set": {"hashed_password": new_hash}}
        )

        return {"message": "Password updated successfully"}, 200

    def update_profile_photo(self, user_id, profile_photo):
        """Store a user profile photo payload in the user's document."""
        if profile_photo is None:
            return {"error": "Profile photo is required"}, 400

        self.users_collection.update_one(
            {"_id": user_id},
            {"$set": {"profile_photo": profile_photo}}
        )

        return {"message": "Profile photo updated successfully"}, 200


def token_required(f):
    """Decorator to protect Flask routes using JWT validation.

    The wrapped route receives `current_user_id` as the first argument which
    is the `sub` claim from the token. On failure the decorator returns a
    JSON error payload with the appropriate HTTP status code.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Extract token from the Authorization header (Bearer <token>)
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            parts = auth_header.split(" ")
            if len(parts) == 2 and parts[0] == "Bearer":
                token = parts[1]

        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        try:
            data = jwt.decode(token, current_app.config['JWT_SECRET'], algorithms=['HS256'])
            current_user_id = data['sub']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        return f(current_user_id, *args, **kwargs)

    return decorated
