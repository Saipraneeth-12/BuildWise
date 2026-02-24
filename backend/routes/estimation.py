"""
Construction Estimation Routes
Handles manual, AI prompt, and blueprint image estimation with CORRECT formulas
"""

from flask import Blueprint, request, jsonify
from middleware.auth import jwt_required_custom
from services.construction_estimator import ConstructionEstimator
from services.ai_estimator import AIEstimator
from services.blueprint_image_estimator import BlueprintImageEstimator
from services.price_fetcher import PriceFetcher

estimation_bp = Blueprint('estimation', __name__)
estimator = ConstructionEstimator()
ai_estimator = AIEstimator()
blueprint_estimator = BlueprintImageEstimator()
price_fetcher = PriceFetcher()

@estimation_bp.route('/estimate', methods=['POST'])
@jwt_required_custom
def manual_estimate():
    """
    Manual estimation endpoint with CORRECT formulas
    Accepts: area_sqft, floors, wage, steel_type, cement_type, location
    """
    try:
        data = request.get_json()
        
        # Extract parameters (now using sqft instead of sq yards)
        area_sqft = float(data.get('area', 0))
        floors = int(data.get('floors', 0))
        wage = float(data.get('wage', 0))
        steel_type = data.get('steel_type', 'Fe500')
        cement_type = data.get('cement_type', 'OPC 53')
        location = data.get('location', 'India')
        
        # Validate inputs
        errors = estimator.validate_inputs(area_sqft, floors, wage)
        if errors:
            return jsonify({'error': ', '.join(errors)}), 400
        
        # Fetch real-time prices
        prices = price_fetcher.get_all_prices(steel_type, cement_type, location)
        
        # Calculate estimate with CORRECT formulas
        estimate = estimator.calculate_estimate(
            area_sqft=area_sqft,
            floors=floors,
            wage_per_day=wage,
            steel_type=steel_type,
            cement_type=cement_type,
            steel_price_per_ton=prices['steel_price_per_ton'],
            cement_price_per_bag=prices['cement_price_per_bag']
        )
        
        return jsonify({
            'success': True,
            'estimate': estimate,
            'prices': prices,
            'mode': 'manual'
        }), 200
        
    except ValueError as e:
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400
    except Exception as e:
        print(f"Manual estimate error: {str(e)}")
        return jsonify({'error': 'Failed to calculate estimate'}), 500


@estimation_bp.route('/ai-estimate', methods=['POST'])
@jwt_required_custom
def ai_estimate():
    """
    AI estimation endpoint
    Accepts natural language prompt
    Uses Granite LLM to extract parameters, then calculates
    """
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        # Extract parameters using Granite LLM
        extracted = ai_estimator.extract_parameters(prompt)
        
        # Get parameters (now in sqft)
        area_sqft = extracted.get('area', 1500)
        floors = extracted['floors']
        wage = extracted['wage']
        steel_type = extracted.get('steel_type', 'Fe500')
        cement_type = extracted.get('cement_type', 'OPC 53')
        location = extracted.get('location', 'India')
        
        # Validate extracted inputs
        errors = estimator.validate_inputs(area_sqft, floors, wage)
        if errors:
            return jsonify({
                'error': 'Extracted invalid parameters',
                'details': errors,
                'extracted': extracted
            }), 400
        
        # Fetch real-time prices
        prices = price_fetcher.get_all_prices(steel_type, cement_type, location)
        
        # Calculate estimate using same engine
        estimate = estimator.calculate_estimate(
            area_sqft=area_sqft,
            floors=floors,
            wage_per_day=wage,
            steel_type=steel_type,
            cement_type=cement_type,
            steel_price_per_ton=prices['steel_price_per_ton'],
            cement_price_per_bag=prices['cement_price_per_bag']
        )
        
        return jsonify({
            'success': True,
            'estimate': estimate,
            'extracted_parameters': extracted,
            'prices': prices,
            'original_prompt': prompt,
            'mode': 'ai'
        }), 200
        
    except Exception as e:
        print(f"AI estimate error: {str(e)}")
        return jsonify({'error': f'Failed to process AI estimate: {str(e)}'}), 500


@estimation_bp.route('/estimate/test', methods=['GET'])
def test_estimation():
    """Test endpoint to verify CORRECT estimation engine"""
    try:
        # Test with sample data: 1500 sqft, G+1 (2 floors)
        # Should give 7.5 tons of steel (NOT 70+ tons)
        test_estimate = estimator.calculate_estimate(
            area_sqft=1500,
            floors=2,  # G+1
            wage_per_day=500,
            steel_type='Fe500',
            cement_type='OPC 53'
        )
        
        return jsonify({
            'success': True,
            'test_estimate': test_estimate,
            'message': 'CORRECT estimation engine working',
            'verification': {
                'total_area': '3000 sqft',
                'steel_required': f"{test_estimate['steel_tons']} tons (CORRECT: should be 7-8 tons)",
                'formula_used': '2.5 kg/sqft (NOT 4 kg/sqft)'
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@estimation_bp.route('/blueprint-estimate', methods=['POST'])
@jwt_required_custom
def blueprint_estimate():
    """
    Blueprint image estimation endpoint
    Accepts multiple image files (one per floor)
    Extracts dimensions using OCR/Vision, then calculates
    CRITICAL: Uses area_per_floor from extraction, NOT total_area
    """
    try:
        # Get uploaded files
        if 'images' not in request.files:
            return jsonify({'error': 'No images uploaded'}), 400
        
        files = request.files.getlist('images')
        
        if not files or len(files) == 0:
            return jsonify({'error': 'At least one image is required'}), 400
        
        # Get parameters from form data
        wage = float(request.form.get('wage', 500))
        steel_type = request.form.get('steel_type', 'Fe500')
        cement_type = request.form.get('cement_type', 'OPC 53')
        location = request.form.get('location', 'India')
        
        # Extract dimensions from images
        extraction_result = blueprint_estimator.extract_dimensions_from_images(files)
        
        # CRITICAL: Use area_per_floor, NOT total_area
        # The estimator will multiply by floors internally
        area_per_floor_sqft = extraction_result['area_per_floor_sqft']
        floors = extraction_result['floors']
        
        # Validate extracted inputs
        errors = estimator.validate_inputs(area_per_floor_sqft, floors, wage)
        if errors:
            return jsonify({
                'error': 'Extracted invalid parameters',
                'details': errors,
                'extraction': extraction_result
            }), 400
        
        # Fetch real-time prices
        prices = price_fetcher.get_all_prices(steel_type, cement_type, location)
        
        # Calculate estimate using same engine
        # CRITICAL: Pass area_per_floor, NOT total_area
        estimate = estimator.calculate_estimate(
            area_sqft=area_per_floor_sqft,  # This is PER FLOOR
            floors=floors,
            wage_per_day=wage,
            steel_type=steel_type,
            cement_type=cement_type,
            steel_price_per_ton=prices['steel_price_per_ton'],
            cement_price_per_bag=prices['cement_price_per_bag']
        )
        
        return jsonify({
            'success': True,
            'estimate': estimate,
            'extraction_details': extraction_result,
            'prices': prices,
            'mode': 'blueprint'
        }), 200
        
    except ValueError as e:
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400
    except Exception as e:
        print(f"Blueprint estimate error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to process blueprint estimate: {str(e)}'}), 500


@estimation_bp.route('/prices/materials', methods=['GET'])
@jwt_required_custom
def get_material_prices():
    """
    Get current material prices
    Query params: steel_type, cement_type, location
    """
    try:
        steel_type = request.args.get('steel_type', 'Fe500')
        cement_type = request.args.get('cement_type', 'OPC 53')
        location = request.args.get('location', 'India')
        
        prices = price_fetcher.get_all_prices(steel_type, cement_type, location)
        
        return jsonify({
            'success': True,
            'prices': prices
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@estimation_bp.route('/materials/types', methods=['GET'])
def get_material_types():
    """Get available steel and cement types"""
    try:
        return jsonify({
            'success': True,
            'steel_types': estimator.get_steel_types(),
            'cement_types': estimator.get_cement_types()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
