from datetime import datetime

class Reminder:
    @staticmethod
    def create(data, user_id):
        return {
            'user_id': user_id,
            'title': data.get('title'),
            'description': data.get('description'),
            'date': data.get('date'),
            'completed': False,
            'created_at': datetime.utcnow()
        }
