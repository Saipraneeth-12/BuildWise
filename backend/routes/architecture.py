from flask import Blueprint, request, jsonify
from middleware.auth import jwt_required_custom, get_current_user
from utils.db import get_db
from datetime import datetime
from services.ai_blueprint_generator import AIBlueprintGenerator
from services.deterministic_layout_engine import DeterministicLayoutEngine
from services.advanced_architecture_generator import AdvancedArchitectureGenerator

architecture_bp = Blueprint('architecture', __name__)

# Initialize services
blueprint_generator = AIBlueprintGenerator()
layout_engine = DeterministicLayoutEngine()
advanced_generator = AdvancedArchitectureGenerator()

@architecture_bp.route('/architecture/generate-variants', methods=['POST'])
@jwt_required_custom
def generate_architecture_variants():
    """
    Generate Multiple Layout Variants
    Uses advanced AI to generate 3 different layout options with scoring
    """
    try:
        data = request.get_json()
        user_id = get_current_user()
        prompt = data.get('prompt', '')
        num_variants = data.get('num_variants', 3)
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        # Generate multiple variants using advanced generator
        variants = advanced_generator.generate_multi_variant_layouts(prompt, num_variants)
        
        # Save all variants to database
        db = get_db()
        saved_variants = []
        
        for variant in variants:
            variant_data = {
                'user_id': user_id,
                'type': 'variant_blueprint',
                'prompt': prompt,
                'variant_number': variant['variant_number'],
                'generation_mode': variant['generation_mode'],
                'layout': variant['3_floor_layouts'],
                'metadata': {
                    'variant_number': variant['variant_number'],
                    'generation_mode': variant['generation_mode'],
                    'optimization_focus': variant['optimization_focus'],
                    'creativity_level': variant['creativity_level'],
                    'overall_score': variant['overall_score'],
                    'grade': variant['grade'],
                    'scores': variant['scores'],
                    'ai_recommendation': variant['ai_recommendation']
                },
                'professional_analysis': variant,
                'created_at': datetime.utcnow()
            }
            
            result = db.blueprints.insert_one(variant_data)
            variant_data['_id'] = str(result.inserted_id)
            variant_data['created_at'] = variant_data['created_at'].isoformat()
            saved_variants.append(variant_data)
        
        return jsonify({
            'variants': saved_variants,
            'message': f'{num_variants} layout variants generated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@architecture_bp.route('/architecture/generate', methods=['POST'])
@jwt_required_custom
def generate_architecture():
    """
    AI Blueprint Generation
    Generates labeled architectural blueprint from natural language prompt
    Supports both deterministic and professional AI modes
    Supports multi-variant generation (3-4 layout options)
    """
    try:
        data = request.get_json()
        user_id = get_current_user()
        prompt = data.get('prompt', '')
        use_professional_ai = data.get('use_professional_ai', False)
        generate_variants = data.get('generate_variants', False)
        num_variants = data.get('num_variants', 3)
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        # Generate blueprint using AI
        result = blueprint_generator.generate_blueprint(
            prompt, 
            use_professional_ai=use_professional_ai,
            generate_variants=generate_variants,
            num_variants=num_variants
        )
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        # Save blueprint to database
        db = get_db()
        blueprint_data = {
            'user_id': user_id,
            'type': 'blueprint',
            'prompt': prompt,
            'layout': result['layout'],
            'blueprint_image': result['blueprint_image'],
            'metadata': result['metadata'],
            'use_professional_ai': use_professional_ai,
            'generate_variants': generate_variants,
            'created_at': datetime.utcnow()
        }
        
        # Add professional analysis if available
        if 'professional_analysis' in result:
            blueprint_data['professional_analysis'] = result['professional_analysis']
        
        # Add variants if available
        if 'variants' in result:
            blueprint_data['variants'] = result['variants']
            blueprint_data['selected_variant'] = result.get('selected_variant', 0)
        
        db_result = db.blueprints.insert_one(blueprint_data)
        blueprint_data['_id'] = str(db_result.inserted_id)
        blueprint_data['created_at'] = blueprint_data['created_at'].isoformat()
        
        return jsonify({
            'blueprint': blueprint_data,
            'message': 'Blueprint generated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@architecture_bp.route('/architecture/blueprints', methods=['GET'])
@jwt_required_custom
def get_blueprints():
    """Get all blueprints for current user"""
    try:
        user_id = get_current_user()
        db = get_db()
        
        blueprints = list(db.blueprints.find({'user_id': user_id}).sort('created_at', -1))
        
        for bp in blueprints:
            bp['_id'] = str(bp['_id'])
            bp['created_at'] = bp['created_at'].isoformat()
        
        return jsonify({'blueprints': blueprints}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@architecture_bp.route('/architecture/blueprints/<blueprint_id>', methods=['DELETE'])
@jwt_required_custom
def delete_blueprint(blueprint_id):
    """Delete a blueprint"""
    try:
        from bson import ObjectId
        user_id = get_current_user()
        db = get_db()
        
        db.blueprints.delete_one({'_id': ObjectId(blueprint_id), 'user_id': user_id})
        
        return jsonify({'message': 'Blueprint deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@architecture_bp.route('/architecture/save-drawing', methods=['POST'])
@jwt_required_custom
def save_manual_drawing():
    """
    Save manual drawing to documents
    Saves canvas data and image to documents collection
    """
    try:
        data = request.get_json()
        user_id = get_current_user()
        db = get_db()
        
        # Save to documents collection as 'manual_drawing' type
        doc_data = {
            'user_id': user_id,
            'name': data.get('name', 'Manual Drawing'),
            'type': 'manual_drawing',
            'canvas_data': data.get('canvas_data'),
            'image_data': data.get('image_data'),  # base64 PNG
            'measurements': data.get('measurements', []),
            'annotations': data.get('annotations', []),
            'size': len(data.get('image_data', '')) if data.get('image_data') else 0,
            'url': '',  # Will be canvas image
            'created_at': datetime.utcnow()
        }
        
        result = db.documents.insert_one(doc_data)
        doc_data['_id'] = str(result.inserted_id)
        doc_data['created_at'] = doc_data['created_at'].isoformat()
        
        return jsonify({
            'document': doc_data,
            'message': 'Manual drawing saved to documents'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@architecture_bp.route('/architecture/save-blueprint-to-docs', methods=['POST'])
@jwt_required_custom
def save_blueprint_to_documents():
    """
    Save AI-generated blueprint to documents collection
    """
    try:
        data = request.get_json()
        user_id = get_current_user()
        db = get_db()
        
        # Save to documents collection as 'blueprint' type
        doc_data = {
            'user_id': user_id,
            'name': data.get('name', 'AI Blueprint'),
            'type': 'blueprint',
            'prompt': data.get('prompt', ''),
            'blueprint_image': data.get('blueprint_image', ''),
            'layout': data.get('layout', {}),
            'metadata': data.get('metadata', {}),
            'size': len(data.get('blueprint_image', '')) if data.get('blueprint_image') else 0,
            'url': '',  # Image is embedded
            'created_at': datetime.utcnow()
        }
        
        result = db.documents.insert_one(doc_data)
        doc_data['_id'] = str(result.inserted_id)
        doc_data['created_at'] = doc_data['created_at'].isoformat()
        
        return jsonify({
            'document': doc_data,
            'message': 'Blueprint saved to documents'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
