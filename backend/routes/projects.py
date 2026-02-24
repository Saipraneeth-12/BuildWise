from flask import Blueprint, request, jsonify
from bson import ObjectId
from middleware.auth import jwt_required_custom, get_current_user
from utils.db import get_db
from models.project import Project

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/projects', methods=['GET'])
@jwt_required_custom
def get_projects():
    try:
        user_id = get_current_user()
        db = get_db()
        
        projects = list(db.projects.find({'user_id': user_id}))
        
        for project in projects:
            project['_id'] = str(project['_id'])
            project['created_at'] = project['created_at'].isoformat()
        
        return jsonify({'projects': projects}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/projects', methods=['POST'])
@jwt_required_custom
def create_project():
    try:
        data = request.get_json()
        user_id = get_current_user()
        db = get_db()
        
        project_data = Project.create(data, user_id)
        result = db.projects.insert_one(project_data)
        
        project_data['_id'] = str(result.inserted_id)
        project_data['created_at'] = project_data['created_at'].isoformat()
        
        return jsonify({'project': project_data}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/projects/<project_id>', methods=['PUT'])
@jwt_required_custom
def update_project(project_id):
    try:
        data = request.get_json()
        user_id = get_current_user()
        db = get_db()
        
        db.projects.update_one(
            {'_id': ObjectId(project_id), 'user_id': user_id},
            {'$set': data}
        )
        
        return jsonify({'message': 'Project updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
