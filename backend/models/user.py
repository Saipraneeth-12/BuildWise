from datetime import datetime
from bson import ObjectId

class User:
    @staticmethod
    def create(data):
        return {
            'email': data.get('email'),
            'password': data.get('password'),
            'name': data.get('name'),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
    
    @staticmethod
    def to_json(user):
        return {
            'id': str(user['_id']),
            'email': user['email'],
            'name': user['name'],
            'created_at': user.get('created_at').isoformat() if user.get('created_at') else None
        }
