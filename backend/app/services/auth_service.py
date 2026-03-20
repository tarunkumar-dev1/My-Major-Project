import jwt
import bcrypt
import datetime
from functools import wraps
from flask import request, jsonify, current_app
from app.database.connection import get_db

class AuthService:
    def __init__(self):
        self.db = get_db()
        self.users_collection = self.db['users']

    def generate_token(self, user_id):
        """Generates a JWT token valid for 24 hours."""
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
        """Hashes a password using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt)

    def verify_password(self, password, hashed_password):
        """Verifies a password against a hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

    def register_user(self, name, email, password, career_goal=None):
        """Registers a new user after checking for duplicates."""
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
        """Authenticates a user and returns a token."""
        user = self.users_collection.find_one({"email": email})
        
        if not user or not self.verify_password(password, user["hashed_password"]):
            return {"error": "Invalid email or password"}, 401
            
        token = self.generate_token(user["_id"])
        return {
            "message": "Login successful", 
            "token": token,
            "user": {
                "id": str(user["_id"]),
                "name": user["name"],
                "email": user["email"]
            }
        }, 200

def token_required(f):
    """Decorator to protect routes via JWT validation."""
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
