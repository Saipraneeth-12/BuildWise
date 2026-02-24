"""
Material Prices Routes
API endpoints for real-time material price dashboard
"""

from flask import Blueprint, request, jsonify
from middleware.auth import jwt_required_custom
from utils.db import get_db
from services.material_price_scraper import MaterialPriceScraper
from models.material_price import MaterialPrice
from datetime import datetime, timedelta
from bson import ObjectId
import statistics

material_prices_bp = Blueprint('material_prices', __name__)
scraper = MaterialPriceScraper()

@material_prices_bp.route('/materials/live', methods=['GET'])
@jwt_required_custom
def get_live_prices():
    """Get current live material prices with filters"""
    try:
        db = get_db()
        
        # Get query parameters
        material = request.args.get('material')
        material_type = request.args.get('type')
        state = request.args.get('state')
        location = request.args.get('location')
        
        # Build query
        query = {}
        if material:
            query['material'] = material
        if material_type:
            query['type'] = material_type
        if state:
            query['state'] = state
        if location:
            query['location'] = location
        
        # Get latest prices (today's data)
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        query['scraped_at'] = {'$gte': today_start}
        
        prices = list(db.material_prices.find(query).sort('scraped_at', -1))
        
        # Convert ObjectId to string
        for price in prices:
            price['_id'] = str(price['_id'])
            price['scraped_at'] = price['scraped_at'].isoformat()
        
        return jsonify({
            'success': True,
            'count': len(prices),
            'prices': prices
        }), 200
        
    except Exception as e:
        print(f"Error fetching live prices: {str(e)}")
        return jsonify({'error': 'Failed to fetch live prices'}), 500



@material_prices_bp.route('/materials/history', methods=['GET'])
@jwt_required_custom
def get_price_history():
    """Get historical price data for trends"""
    try:
        db = get_db()
        
        # Get query parameters
        material = request.args.get('material', 'Cement')
        material_type = request.args.get('type', 'OPC 53')
        location = request.args.get('location', 'Mumbai')
        days = int(request.args.get('days', 30))
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Query historical data
        query = {
            'material': material,
            'type': material_type,
            'location': location,
            'scraped_at': {'$gte': start_date, '$lte': end_date}
        }
        
        history = list(db.material_prices.find(query).sort('scraped_at', 1))
        
        # If no historical data exists, generate it
        if len(history) == 0:
            print(f"No historical data found, generating for {days} days...")
            historical_data = scraper.generate_historical_data(days=days)
            
            # Filter for requested material/type/location
            filtered_data = [
                record for record in historical_data
                if record['material'] == material 
                and record['type'] == material_type 
                and record['location'] == location
            ]
            
            # Insert into database
            if filtered_data:
                db.material_prices.insert_many(filtered_data)
                history = filtered_data
        
        # Convert to chart-friendly format
        chart_data = []
        for record in history:
            chart_data.append({
                'date': record['scraped_at'].strftime('%Y-%m-%d') if isinstance(record['scraped_at'], datetime) else record['scraped_at'][:10],
                'price': record['price'],
                'trend': record.get('trend', 'same')
            })
        
        return jsonify({
            'success': True,
            'material': material,
            'type': material_type,
            'location': location,
            'history': chart_data
        }), 200
        
    except Exception as e:
        print(f"Error fetching price history: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to fetch price history'}), 500


@material_prices_bp.route('/materials/refresh', methods=['POST'])
@jwt_required_custom
def refresh_prices():
    """Manually trigger price refresh (admin only)"""
    try:
        db = get_db()
        
        # Fetch new prices
        new_prices = scraper.fetch_all_prices()
        
        # Calculate trends by comparing with yesterday's prices
        yesterday = datetime.utcnow() - timedelta(days=1)
        
        for price_data in new_prices:
            # Find yesterday's price for comparison
            previous = db.material_prices.find_one({
                'material': price_data['material'],
                'type': price_data['type'],
                'location': price_data['location'],
                'scraped_at': {'$gte': yesterday}
            }, sort=[('scraped_at', -1)])
            
            # Calculate trend
            if previous:
                trend = MaterialPrice.calculate_trend(
                    price_data['price'],
                    previous['price']
                )
                price_data['trend'] = trend
            else:
                price_data['trend'] = 'same'
            
            # Insert new price record
            db.material_prices.insert_one(price_data)
        
        return jsonify({
            'success': True,
            'message': f'Refreshed {len(new_prices)} price records',
            'count': len(new_prices)
        }), 200
        
    except Exception as e:
        print(f"Error refreshing prices: {str(e)}")
        return jsonify({'error': 'Failed to refresh prices'}), 500



@material_prices_bp.route('/materials/trends', methods=['GET'])
@jwt_required_custom
def get_price_trends():
    """Get aggregated price trends and statistics"""
    try:
        db = get_db()
        
        # Get today's and yesterday's average prices
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_start = today_start - timedelta(days=1)
        
        # Calculate averages for major materials
        materials = ['Cement', 'Steel', 'Sand', 'Aggregates', 'Bricks']
        trends = {}
        
        for material in materials:
            # Today's average
            today_prices = list(db.material_prices.find({
                'material': material,
                'scraped_at': {'$gte': today_start}
            }))
            
            # Yesterday's average
            yesterday_prices = list(db.material_prices.find({
                'material': material,
                'scraped_at': {'$gte': yesterday_start, '$lt': today_start}
            }))
            
            if today_prices:
                today_avg = statistics.mean([p['price'] for p in today_prices])
                yesterday_avg = statistics.mean([p['price'] for p in yesterday_prices]) if yesterday_prices else today_avg
                
                change_percent = MaterialPrice.calculate_change_percent(today_avg, yesterday_avg)
                
                trends[material] = {
                    'current_avg': round(today_avg, 2),
                    'previous_avg': round(yesterday_avg, 2),
                    'change_percent': change_percent,
                    'trend': 'up' if change_percent > 0 else 'down' if change_percent < 0 else 'same',
                    'count': len(today_prices)
                }
        
        return jsonify({
            'success': True,
            'trends': trends,
            'updated_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        print(f"Error fetching trends: {str(e)}")
        return jsonify({'error': 'Failed to fetch trends'}), 500


@material_prices_bp.route('/materials/filters', methods=['GET'])
def get_filter_options():
    """Get available filter options (states, cities, materials, types)"""
    try:
        return jsonify({
            'success': True,
            'states': list(MaterialPriceScraper.LOCATIONS.keys()),
            'locations': MaterialPriceScraper.LOCATIONS,
            'materials': list(MaterialPriceScraper.BASE_PRICES.keys()),
            'types': {
                material: list(types.keys())
                for material, types in MaterialPriceScraper.BASE_PRICES.items()
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@material_prices_bp.route('/materials/summary', methods=['GET'])
@jwt_required_custom
def get_dashboard_summary():
    """Get summary statistics for dashboard cards"""
    try:
        db = get_db()
        
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_start = today_start - timedelta(days=1)
        
        # Get averages for top materials
        summary = {}
        
        # Cement average
        cement_today = list(db.material_prices.find({
            'material': 'Cement',
            'scraped_at': {'$gte': today_start}
        }))
        
        cement_yesterday = list(db.material_prices.find({
            'material': 'Cement',
            'scraped_at': {'$gte': yesterday_start, '$lt': today_start}
        }))
        
        if cement_today:
            cement_avg_today = statistics.mean([p['price'] for p in cement_today])
            cement_avg_yesterday = statistics.mean([p['price'] for p in cement_yesterday]) if cement_yesterday else cement_avg_today
            
            summary['cement'] = {
                'avg_price': round(cement_avg_today, 2),
                'unit': 'bag',
                'change_percent': MaterialPrice.calculate_change_percent(cement_avg_today, cement_avg_yesterday)
            }
        
        # Steel average
        steel_today = list(db.material_prices.find({
            'material': 'Steel',
            'scraped_at': {'$gte': today_start}
        }))
        
        steel_yesterday = list(db.material_prices.find({
            'material': 'Steel',
            'scraped_at': {'$gte': yesterday_start, '$lt': today_start}
        }))
        
        if steel_today:
            steel_avg_today = statistics.mean([p['price'] for p in steel_today])
            steel_avg_yesterday = statistics.mean([p['price'] for p in steel_yesterday]) if steel_yesterday else steel_avg_today
            
            summary['steel'] = {
                'avg_price': round(steel_avg_today, 2),
                'unit': 'ton',
                'change_percent': MaterialPrice.calculate_change_percent(steel_avg_today, steel_avg_yesterday)
            }
        
        # Sand average
        sand_today = list(db.material_prices.find({
            'material': 'Sand',
            'scraped_at': {'$gte': today_start}
        }))
        
        if sand_today:
            sand_avg_today = statistics.mean([p['price'] for p in sand_today])
            summary['sand'] = {
                'avg_price': round(sand_avg_today, 2),
                'unit': 'cft',
                'change_percent': 0
            }
        
        # Aggregates average
        agg_today = list(db.material_prices.find({
            'material': 'Aggregates',
            'scraped_at': {'$gte': today_start}
        }))
        
        if agg_today:
            agg_avg_today = statistics.mean([p['price'] for p in agg_today])
            summary['aggregates'] = {
                'avg_price': round(agg_avg_today, 2),
                'unit': 'cft',
                'change_percent': 0
            }
        
        return jsonify({
            'success': True,
            'summary': summary,
            'updated_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        print(f"Error fetching summary: {str(e)}")
        return jsonify({'error': 'Failed to fetch summary'}), 500


@material_prices_bp.route('/materials/init-historical', methods=['POST'])
@jwt_required_custom
def init_historical_data():
    """Initialize historical data for all materials (admin only)"""
    try:
        db = get_db()
        days = int(request.json.get('days', 90))
        
        # Check if historical data already exists
        oldest_record = db.material_prices.find_one(sort=[('scraped_at', 1)])
        if oldest_record:
            oldest_date = oldest_record['scraped_at']
            days_existing = (datetime.utcnow() - oldest_date).days
            
            if days_existing >= days:
                return jsonify({
                    'success': True,
                    'message': f'Historical data already exists for {days_existing} days',
                    'skipped': True
                }), 200
        
        # Generate historical data
        print(f"Generating {days} days of historical data...")
        historical_data = scraper.generate_historical_data(days=days)
        
        # Insert in batches to avoid memory issues
        batch_size = 1000
        total_inserted = 0
        
        for i in range(0, len(historical_data), batch_size):
            batch = historical_data[i:i+batch_size]
            db.material_prices.insert_many(batch)
            total_inserted += len(batch)
            print(f"Inserted {total_inserted}/{len(historical_data)} records...")
        
        return jsonify({
            'success': True,
            'message': f'Initialized {total_inserted} historical price records for {days} days',
            'count': total_inserted,
            'days': days
        }), 200
        
    except Exception as e:
        print(f"Error initializing historical data: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to initialize historical data'}), 500
