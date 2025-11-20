"""
User & Watchlist Service - Main Application
Handles user authentication and watchlist management
"""

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import db
from routes.auth import auth_bp
from routes.watchlist import watchlist_bp
from config import Config
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS
CORS(app)

# Initialize database
db.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(watchlist_bp, url_prefix='/api/watchlist')

# Create tables
with app.app_context():
    db.create_all()
    logger.info("Database tables created")


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        db_status = True
    except:
        db_status = False
    
    return jsonify({
        'status': 'healthy' if db_status else 'unhealthy',
        'service': 'user-service',
        'database_connected': db_status
    }), 200 if db_status else 503


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=False)
