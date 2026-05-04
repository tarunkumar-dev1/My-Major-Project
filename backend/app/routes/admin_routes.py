"""
Admin HTTP routes for lightweight administrative tasks and analytics.

This blueprint protects endpoints using the `admin_required` decorator which
validates that the JWT token contains the `role: admin` claim. Admin
credentials are stored in `Config` for development; consider replacing this
with a proper admin user collection for production.
"""

import datetime
import jwt
from functools import wraps
from flask import Blueprint, request, jsonify, current_app
from app.database.connection import get_db

admin_bp = Blueprint('admin_bp', __name__)


def admin_required(f):
    """Decorator to ensure the request has a valid admin JWT token.

    The decorator decodes the token from the `Authorization` header and
    verifies the `role` claim equals `'admin'`.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization', '')
        parts = auth_header.split(' ')
        if len(parts) == 2 and parts[0] == 'Bearer':
            token = parts[1]

        if not token:
            return jsonify({'error': 'Admin token is missing'}), 401

        try:
            payload = jwt.decode(token, current_app.config['JWT_SECRET'], algorithms=['HS256'])
            if payload.get('role') != 'admin':
                return jsonify({'error': 'Admin access required'}), 403
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Admin session has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid admin token'}), 401

        return f(*args, **kwargs)

    return decorated


@admin_bp.route('/login', methods=['POST'])
def admin_login():
    """Authenticate using developer/admin credentials from config.

    Returns a short-lived token with `role: admin` that admin_required checks
    for. This is convenient for local testing; do not use hardcoded
    credentials in production.
    """
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    expected_username = current_app.config['ADMIN_USERNAME']
    expected_password = current_app.config['ADMIN_PASSWORD']

    if username != expected_username or password != expected_password:
        return jsonify({'error': 'Invalid admin credentials'}), 401

    payload = {
        'sub': expected_username,
        'role': 'admin',
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    token = jwt.encode(payload, current_app.config['JWT_SECRET'], algorithm='HS256')

    return jsonify({
        'message': 'Admin login successful',
        'token': token,
        'admin': {
            'username': expected_username,
            'role': 'admin'
        }
    }), 200


@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def admin_dashboard():
    """Aggregate lightweight analytics for the admin UI.

    The route compiles basic stats (counts, averages, trends) and returns the
    entire user list (excluding passwords) for quick inspection.
    """
    db = get_db()
    users_col = db['users']
    careers_col = db['careers']
    courses_col = db['courses']
    login_events_col = db['login_events']

    users_cursor = users_col.find({}, {'hashed_password': 0}).sort('created_at', -1)
    users_list = []
    total_readiness = 0
    active_users = 0
    for user in users_cursor:
        user['_id'] = str(user['_id'])
        user['login_count'] = int(user.get('login_count', 0) or 0)
        user['skills_count'] = len(user.get('skills', []))
        user['completed_count'] = len(user.get('completed_skills', []))
        user['readiness_score'] = int(user.get('readiness_score', 0) or 0)
        user['has_photo'] = bool(user.get('profile_photo'))
        total_readiness += user['readiness_score']
        if user['login_count'] > 0:
            active_users += 1
        users_list.append(user)

    total_users = len(users_list)
    avg_readiness = round(total_readiness / total_users, 1) if total_users else 0
    recent_signups = users_list[:5]
    career_trends = list(users_col.aggregate([
        {'$group': {'_id': '$career_goal', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}}
    ]))
    career_trends = [trend for trend in career_trends if trend['_id']]

    career_catalog = []
    for career in careers_col.find({}, {'_id': 0}).sort('career_name', 1):
        career_catalog.append(career)

    stats = {
        'total_users': total_users,
        'active_users': active_users,
        'career_paths': careers_col.count_documents({}),
        'linked_courses': courses_col.count_documents({}),
        'skill_analyses_run': db['roadmaps'].count_documents({}),
        'login_events': login_events_col.count_documents({}),
        'avg_readiness': avg_readiness,
        'career_trends': career_trends,
        'total_completed_skills': sum(user['completed_count'] for user in users_list)
    }

    return jsonify({
        'stats': stats,
        'users': users_list,
        'recent_signups': recent_signups,
        'career_catalog': career_catalog
    }), 200


@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_all_users():
    """Return all user documents (safe for admin inspection)."""
    db = get_db()
    users_col = db['users']
    users_cursor = users_col.find({}, {'hashed_password': 0})
    users_list = []
    for user in users_cursor:
        user['_id'] = str(user['_id'])
        users_list.append(user)

    return jsonify({'users': users_list, 'count': len(users_list)}), 200