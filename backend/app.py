from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from utils.db import init_db

app = Flask(__name__)
app.config.from_object(Config)

CORS(app)
JWTManager(app)

# Initialize database
init_db()

# Register blueprints
from routes.auth import auth_bp
from routes.chat import chat_bp
from routes.materials import materials_bp
from routes.cost import cost_bp
from routes.projects import projects_bp
from routes.expenses import expenses_bp
from routes.reminders import reminders_bp
from routes.documents import documents_bp
from routes.tasks import tasks_bp
from routes.architecture import architecture_bp
from routes.budget import budget_bp
from routes.analytics import analytics_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(chat_bp, url_prefix='/api')
app.register_blueprint(materials_bp, url_prefix='/api/materials')
app.register_blueprint(cost_bp, url_prefix='/api/cost')
app.register_blueprint(projects_bp, url_prefix='/api')
app.register_blueprint(expenses_bp, url_prefix='/api')
app.register_blueprint(reminders_bp, url_prefix='/api')
app.register_blueprint(documents_bp, url_prefix='/api')
app.register_blueprint(tasks_bp, url_prefix='/api')
app.register_blueprint(architecture_bp, url_prefix='/api')
app.register_blueprint(budget_bp, url_prefix='/api')
app.register_blueprint(analytics_bp, url_prefix='/api')
from routes.scrum import scrum_bp
app.register_blueprint(scrum_bp, url_prefix='/api')
from routes.estimation import estimation_bp
app.register_blueprint(estimation_bp, url_prefix='/api')
from routes.material_prices import material_prices_bp
app.register_blueprint(material_prices_bp, url_prefix='/api')

# Initialize price scheduler
from services.price_scheduler import PriceScheduler
price_scheduler = PriceScheduler()
price_scheduler.start()

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.PORT, debug=Config.FLASK_ENV == 'development')
