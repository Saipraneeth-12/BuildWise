"""
Material Price Model
Stores real-time construction material prices with historical tracking
"""

from datetime import datetime
from bson import ObjectId

class MaterialPrice:
    """Material price model for MongoDB"""
    
    @staticmethod
    def create(material, material_type, price, unit, location, state, source, trend='same'):
        """Create new material price record"""
        return {
            'material': material,
            'type': material_type,
            'price': float(price),
            'unit': unit,
            'location': location,
            'state': state,
            'source': source,
            'trend': trend,
            'scraped_at': datetime.utcnow(),
            'created_at': datetime.utcnow()
        }
    
    @staticmethod
    def calculate_trend(current_price, previous_price):
        """Calculate price trend"""
        if previous_price is None:
            return 'same'
        
        change_percent = ((current_price - previous_price) / previous_price) * 100
        
        if change_percent > 1:
            return 'up'
        elif change_percent < -1:
            return 'down'
        else:
            return 'same'
    
    @staticmethod
    def calculate_change_percent(current_price, previous_price):
        """Calculate percentage change"""
        if previous_price is None or previous_price == 0:
            return 0
        
        return round(((current_price - previous_price) / previous_price) * 100, 2)
