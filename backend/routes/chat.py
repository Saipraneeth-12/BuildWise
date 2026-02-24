from flask import Blueprint, request, jsonify
from middleware.auth import jwt_required_custom, get_current_user
from utils.db import get_db
from models.chat import Chat

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['POST'])
@jwt_required_custom
def send_message():
    try:
        data = request.get_json()
        user_id = get_current_user()
        db = get_db()
        
        message = data.get('message')
        
        # Placeholder response - RAG will be attached later
        reply = "AI placeholder response. This is where the RAG-powered AI assistant will provide intelligent construction planning advice. The system is ready for AI integration."
        
        chat_data = Chat.create({
            'message': message,
            'reply': reply
        }, user_id)
        
        db.chat_history.insert_one(chat_data)
        
        return jsonify({'reply': reply}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/chat/history', methods=['GET'])
@jwt_required_custom
def get_history():
    try:
        user_id = get_current_user()
        db = get_db()
        
        history = list(db.chat_history.find({'user_id': user_id}).sort('created_at', -1).limit(50))
        
        for item in history:
            item['_id'] = str(item['_id'])
            item['created_at'] = item['created_at'].isoformat()
        
        return jsonify({'history': history}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
