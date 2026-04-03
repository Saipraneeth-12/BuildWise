from flask import Blueprint, request, jsonify, Response, stream_with_context
from middleware.auth import jwt_required_custom, get_current_user
from utils.db import get_db
from models.chat import Chat
from services.construction_ai_assistant import ConstructionAIAssistant
import json

chat_bp = Blueprint('chat', __name__)
ai_assistant = ConstructionAIAssistant()

@chat_bp.route('/chat', methods=['POST'])
@jwt_required_custom
def send_message():
    """Standard (non-streaming) chat endpoint."""
    try:
        data = request.get_json()
        user_id = get_current_user()
        db = get_db()

        message = data.get('message', '').strip()
        if not message:
            return jsonify({'error': 'Message is required'}), 400

        recent_history = list(
            db.chat_history.find({'user_id': user_id}).sort('created_at', -1).limit(3)
        )
        conversation_history = []
        for item in reversed(recent_history):
            conversation_history.append({'role': 'user', 'content': item.get('message', '')})
            conversation_history.append({'role': 'assistant', 'content': item.get('reply', '')})

        ai_response = ai_assistant.chat(message, conversation_history)
        reply = ai_response.get('response', 'Unable to generate response.')

        chat_data = Chat.create({
            'message': message,
            'reply': reply,
            'model': ai_response.get('model', 'formula_engine'),
            'success': ai_response.get('success', False)
        }, user_id)
        db.chat_history.insert_one(chat_data)

        return jsonify({
            'reply': reply,
            'timestamp': ai_response.get('timestamp'),
            'model': ai_response.get('model'),
            'source': ai_response.get('source', 'unknown'),
            'success': ai_response.get('success', True)
        }), 200

    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({'error': 'Failed to process message'}), 500


@chat_bp.route('/chat/stream', methods=['POST'])
@jwt_required_custom
def send_message_stream():
    """
    Streaming chat endpoint — sends tokens as Server-Sent Events.
    Formula engine answers arrive instantly; LLM answers stream token by token.
    """
    try:
        data = request.get_json()
        user_id = get_current_user()
        db = get_db()

        message = data.get('message', '').strip()
        if not message:
            return jsonify({'error': 'Message is required'}), 400

        recent_history = list(
            db.chat_history.find({'user_id': user_id}).sort('created_at', -1).limit(3)
        )
        conversation_history = []
        for item in reversed(recent_history):
            conversation_history.append({'role': 'user', 'content': item.get('message', '')})
            conversation_history.append({'role': 'assistant', 'content': item.get('reply', '')})

        full_reply = []

        def generate():
            for token in ai_assistant.chat_stream(message, conversation_history):
                full_reply.append(token)
                yield f"data: {json.dumps({'token': token})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"

            # Save to DB after streaming completes
            reply_text = "".join(full_reply)
            chat_data = Chat.create({
                'message': message,
                'reply': reply_text,
                'model': ai_assistant.model,
                'success': True
            }, user_id)
            db.chat_history.insert_one(chat_data)

        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )

    except Exception as e:
        print(f"Stream chat error: {e}")
        return jsonify({'error': 'Failed to process message'}), 500

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


@chat_bp.route('/chat/quick-estimate', methods=['POST'])
@jwt_required_custom
def quick_estimate():
    """
    Generate quick thumb rule estimate via AI assistant
    """
    try:
        data = request.get_json()
        area_sqft = float(data.get('area', 0))
        floors = int(data.get('floors', 1))
        
        if area_sqft <= 0 or floors <= 0:
            return jsonify({'error': 'Invalid area or floors'}), 400
        
        # Generate estimate using AI assistant
        estimate_response = ai_assistant.get_quick_estimate(area_sqft, floors)
        
        return jsonify({
            'estimate': estimate_response,
            'success': True
        }), 200
        
    except ValueError as e:
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400
    except Exception as e:
        print(f"Quick estimate error: {str(e)}")
        return jsonify({'error': 'Failed to generate estimate'}), 500


@chat_bp.route('/chat/clear', methods=['DELETE'])
@jwt_required_custom
def clear_history():
    """
    Clear chat history for current user
    """
    try:
        user_id = get_current_user()
        db = get_db()
        
        result = db.chat_history.delete_many({'user_id': user_id})
        
        return jsonify({
            'success': True,
            'deleted_count': result.deleted_count
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
