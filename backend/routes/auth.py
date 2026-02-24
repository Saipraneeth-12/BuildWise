from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from utils.db import get_db
from utils.auth import hash_password, verify_password
from models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        db = get_db()
        
        if db.users.find_one({'email': data.get('email')}):
            return jsonify({'error': 'Email already exists'}), 400
        
        user_data = User.create(data)
        user_data['password'] = hash_password(data.get('password'))
        
        result = db.users.insert_one(user_data)
        user_data['_id'] = result.inserted_id
        
        token = create_access_token(identity=str(result.inserted_id))
        
        return jsonify({
            'token': token,
            'user': User.to_json(user_data)
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        db = get_db()
        
        user = db.users.find_one({'email': data.get('email')})
        if not user or not verify_password(data.get('password'), user['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        token = create_access_token(identity=str(user['_id']))
        
        return jsonify({
            'token': token,
            'user': User.to_json(user)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    from middleware.auth import jwt_required_custom, get_current_user
    from bson import ObjectId
    
    @jwt_required_custom
    def _get_profile():
        try:
            user_id = get_current_user()
            db = get_db()
            user = db.users.find_one({'_id': ObjectId(user_id)})
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            return jsonify({'user': User.to_json(user)}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return _get_profile()
