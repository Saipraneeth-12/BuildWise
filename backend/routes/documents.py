from flask import Blueprint, request, jsonify
from bson import ObjectId
from middleware.auth import jwt_required_custom, get_current_user
from utils.db import get_db
from models.document import Document

documents_bp = Blueprint('documents', __name__)

@documents_bp.route('/documents', methods=['GET'])
@jwt_required_custom
def get_documents():
    try:
        user_id = get_current_user()
        db = get_db()
        
        documents = list(db.documents.find({'user_id': user_id}))
        
        for doc in documents:
            doc['_id'] = str(doc['_id'])
            doc['created_at'] = doc['created_at'].isoformat()
        
        return jsonify({'documents': documents}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@documents_bp.route('/documents', methods=['POST'])
@jwt_required_custom
def upload_document():
    try:
        data = request.get_json()
        user_id = get_current_user()
        db = get_db()
        
        doc_data = Document.create(data, user_id)
        result = db.documents.insert_one(doc_data)
        
        doc_data['_id'] = str(result.inserted_id)
        doc_data['created_at'] = doc_data['created_at'].isoformat()
        
        return jsonify({'document': doc_data}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@documents_bp.route('/documents/<doc_id>', methods=['DELETE'])
@jwt_required_custom
def delete_document(doc_id):
    try:
        user_id = get_current_user()
        db = get_db()
        
        db.documents.delete_one({'_id': ObjectId(doc_id), 'user_id': user_id})
        
        return jsonify({'message': 'Document deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
