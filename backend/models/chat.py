from datetime import datetime

class Chat:
    @staticmethod
    def create(data, user_id):
        return {
            'user_id': user_id,
            'message': data.get('message'),
            'reply': data.get('reply'),
            'created_at': datetime.utcnow()
        }
