from flask import Blueprint, request, jsonify
from app.services.auth_service import token_required
from app.services.analysis_service import AnalysisService
from app.services.roadmap_service import RoadmapService
from app.database.connection import get_db
from bson.objectid import ObjectId

student_bp = Blueprint('student_bp', __name__)

@student_bp.route('/submit-skills', methods=['POST'])
@token_required
def submit_skills(current_user_id):
    """Expects 'skills' (array of strings) and 'career_goal' (string)."""
    data = request.get_json()
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
    """Returns the user's dashboard metrics."""
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

@student_bp.route('/roadmap', methods=['GET'])
@token_required
def get_roadmap(current_user_id):
    """Returns the generated learning roadmap."""
    roadmap_service = RoadmapService()
    roadmap = roadmap_service.get_user_roadmap(current_user_id)
    
    if not roadmap:
        return jsonify({"message": "No roadmap found. Please run the analyzer first."}), 404
        
    roadmap['_id'] = str(roadmap.get('_id', ''))
    return jsonify({"roadmap": roadmap}), 200

@student_bp.route('/mark-completed', methods=['POST'])
@token_required
def mark_skill_completed(current_user_id):
    """Mark a specific roadmap module or skill as completed."""
    data = request.get_json()
    skill_name = data.get('skill')
    
    if not skill_name:
        return jsonify({"error": "Skill name is required"}), 400
        
    db = get_db()
    # In a real app we'd update exact roadmap nesting, here we push to completions
    db['users'].update_one(
        {"_id": ObjectId(current_user_id)},
        {"$addToSet": {"completed_skills": skill_name}}
    )
    
    return jsonify({"message": f"Successfully marked {skill_name} as completed."}), 200

@student_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user_id):
    """Update user's profile information."""
    data = request.get_json()
    name = data.get('name')
    career_goal = data.get('career_goal')

    db = get_db()
    users_col = db['users']

    update_fields = {}
    if name:
        update_fields['name'] = name
    if career_goal:
        update_fields['career_goal'] = career_goal

    if not update_fields:
        return jsonify({"message": "No valid fields provided for update"}), 400

    result = users_col.update_one(
        {"_id": ObjectId(current_user_id)},
        {"$set": update_fields}
    )

    if result.matched_count == 0:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"message": "Profile updated successfully"}), 200
