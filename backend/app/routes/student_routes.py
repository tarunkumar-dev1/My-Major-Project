"""
Student-facing HTTP routes (Blueprint).

This module exposes REST endpoints used by the student frontend to submit
skills, view dashboards, manage their profile, and fetch generated roadmaps.
All endpoints are protected by the `token_required` decorator which injects
the `current_user_id` parameter.
"""

from flask import Blueprint, request, jsonify
from app.services.auth_service import token_required, AuthService
from app.services.analysis_service import AnalysisService
from app.services.roadmap_service import RoadmapService
from app.database.connection import get_db
from bson.objectid import ObjectId

student_bp = Blueprint('student_bp', __name__)


@student_bp.route('/submit-skills', methods=['POST'])
@token_required
def submit_skills(current_user_id):
    """Accept a skills array and career goal, then run analysis.

    Request JSON expected keys:
      - `skills`: list of string skill names
      - `career_goal`: the desired career name (string)

    Returns a structured analysis payload and HTTP status code.
    """
    data = request.get_json() or {}
    skills = data.get('skills', [])
    career_goal = data.get('career_goal')

    if not skills or not isinstance(skills, list):
        return jsonify({"error": "Skills array is required and cannot be empty"}), 400

    if not career_goal:
        return jsonify({"error": "Career goal is required"}), 400

    analysis_service = AnalysisService()
    response, status_code = analysis_service.analyze_student_skills(
        user_id=current_user_id,
        submitted_skills=skills,
        career_goal=career_goal
    )

    return jsonify(response), status_code


@student_bp.route('/dashboard', methods=['GET'])
@token_required
def get_dashboard(current_user_id):
    """Return the user's profile and computed metrics for the dashboard."""
    db = get_db()
    users_col = db['users']

    user = users_col.find_one({"_id": ObjectId(current_user_id)}, {"hashed_password": 0})
    if not user:
        return jsonify({"error": "User not found"}), 404

    user['_id'] = str(user['_id'])
    return jsonify({
        "user": user,
        "message": "Dashboard data fetched successfully"
    }), 200


@student_bp.route('/careers', methods=['GET'])
@token_required
def get_careers(current_user_id):
    """List available career options and their required skills.

    The route returns careers sorted alphabetically for predictable UI
    rendering.
    """
    db = get_db()
    careers_cursor = db['careers'].find({}, {"_id": 0})
    careers = list(careers_cursor)

    careers.sort(key=lambda c: (c.get("career_name") or "").lower())

    return jsonify({
        "careers": careers,
        "count": len(careers)
    }), 200


@student_bp.route('/roadmap', methods=['GET'])
@token_required
def get_roadmap(current_user_id):
    """Retrieve the user's latest generated learning roadmap."""
    roadmap_service = RoadmapService()
    roadmap = roadmap_service.get_user_roadmap(current_user_id)

    if not roadmap:
        return jsonify({"message": "No roadmap found. Please run the analyzer first."}), 404

    roadmap['_id'] = str(roadmap.get('_id', ''))
    return jsonify({"roadmap": roadmap}), 200


@student_bp.route('/mark-completed', methods=['POST'])
@token_required
def mark_skill_completed(current_user_id):
    """Mark a roadmap skill/module as completed for the current user.

    This implementation:
    1. Stores completed skill names in the user's `completed_skills` array
    2. Recalculates the readiness_score based on completed + current skills
    3. Updates the user record with the new readiness score
    """
    data = request.get_json() or {}
    skill_name = data.get('skill')

    if not skill_name:
        return jsonify({"error": "Skill name is required"}), 400

    db = get_db()
    users_col = db['users']
    careers_col = db['careers']
    
    # Mark skill as completed
    users_col.update_one(
        {"_id": ObjectId(current_user_id)},
        {"$addToSet": {"completed_skills": skill_name}}
    )
    
    # Fetch updated user to get career goal
    user = users_col.find_one({"_id": ObjectId(current_user_id)})
    if not user or not user.get('career_goal'):
        return jsonify({"message": f"Successfully marked {skill_name} as completed."}), 200
    
    # Get required skills for the career
    career = careers_col.find_one({"career_name": user.get('career_goal')})
    if not career:
        return jsonify({"message": f"Successfully marked {skill_name} as completed."}), 200
    
    required_skills = career.get('required_skills', [])
    completed_skills = user.get('completed_skills', []) + [skill_name]
    current_skills = user.get('skills', [])
    
    # Calculate new readiness score
    all_covered = list(set(completed_skills + current_skills))
    new_readiness = 0
    if required_skills:
        new_readiness = int((len(all_covered) / len(required_skills)) * 100)
        new_readiness = min(100, new_readiness)  # Cap at 100%
    
    # Update readiness score in database
    users_col.update_one(
        {"_id": ObjectId(current_user_id)},
        {"$set": {"readiness_score": new_readiness}}
    )

    return jsonify({
        "message": f"Successfully marked {skill_name} as completed.",
        "new_readiness_score": new_readiness
    }), 200


@student_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user_id):
    """Update editable fields of the user's profile.

    Accepts optional `name`, `career_goal`, `preferences` and `profile_photo`.
    Only supplied fields are updated.
    """
    data = request.get_json() or {}
    name = data.get('name')
    career_goal = data.get('career_goal')
    preferences = data.get('preferences')
    profile_photo = data.get('profile_photo')

    db = get_db()
    users_col = db['users']

    update_fields = {}
    if name is not None and name != '':
        update_fields['name'] = name
    if career_goal is not None and career_goal != '':
        update_fields['career_goal'] = career_goal
    if isinstance(preferences, dict):
        update_fields['preferences'] = {
            'email_notifications': bool(preferences.get('email_notifications', True)),
            'public_profile': bool(preferences.get('public_profile', False)),
            'two_factor_enabled': bool(preferences.get('two_factor_enabled', False)),
        }
    if profile_photo is not None:
        update_fields['profile_photo'] = profile_photo

    if not update_fields:
        return jsonify({"message": "No valid fields provided for update"}), 400

    result = users_col.update_one(
        {"_id": ObjectId(current_user_id)},
        {"$set": update_fields}
    )

    if result.matched_count == 0:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"message": "Profile updated successfully", "updated": update_fields}), 200


@student_bp.route('/profile/password', methods=['PUT'])
@token_required
def update_password(current_user_id):
    """Change the logged-in user's password.

    Expects `current_password` and `new_password` in the request JSON.
    Delegates validation and update to `AuthService.change_password`.
    """
    data = request.get_json() or {}
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    auth_service = AuthService()
    response, status_code = auth_service.change_password(
        ObjectId(current_user_id),
        current_password,
        new_password
    )
    return jsonify(response), status_code
