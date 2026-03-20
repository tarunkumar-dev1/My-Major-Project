from flask import Blueprint, request, jsonify
from app.services.auth_service import token_required
from app.database.connection import get_db

# Admin routes might be protected by a simple master token or role middleware in a larger app.
# For simplicity, we are leaving them open or using token_required.
admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.route('/add-career', methods=['POST'])
def add_career():
    """Add a new career and its required skills dataset."""
    data = request.get_json()
    career_name = data.get('career_name')
    required_skills = data.get('required_skills')
    difficulty_level = data.get('difficulty_level', 'Intermediate')
    
    if not career_name or not isinstance(required_skills, list):
        return jsonify({"error": "career_name and required_skills array are required"}), 400
        
    db = get_db()
    careers_col = db['careers']
    
    # Upsert career
    career_doc = {
        "career_name": career_name,
        "required_skills": required_skills,
        "difficulty_level": difficulty_level
    }
    
    careers_col.update_one(
        {"career_name": career_name},
        {"$set": career_doc},
        upsert=True
    )
    
    return jsonify({
        "message": f"Career '{career_name}' added/updated successfully",
        "career": career_doc
    }), 201

@admin_bp.route('/users', methods=['GET'])
def get_all_users():
    """Retrieve all users stats for the admin dashboard."""
    db = get_db()
    users_col = db['users']
    
    # Project out passwords
    users_cursor = users_col.find({}, {"hashed_password": 0})
    users_list = []
    
    for u in users_cursor:
        u['_id'] = str(u['_id'])
        users_list.append(u)
        
    # Example aggregate top careers
    pipeline = [
        {"$group": {"_id": "$career_goal", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    career_trends = list(users_col.aggregate(pipeline))
    
    return jsonify({
        "total_stats": {
            "total_users": len(users_list),
            "career_trends": [trend for trend in career_trends if trend['_id']]
        },
        "users": users_list
    }), 200
