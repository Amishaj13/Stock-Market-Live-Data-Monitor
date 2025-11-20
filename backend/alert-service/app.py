"""
Alert Service - Main Application
Consumes alert events and manages user notifications
"""

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from consumer import AlertConsumer
from rule_engine import RuleEngine
from notifier import WebSocketNotifier
from models import db, Alert, AlertRule
from config import Config
import logging
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Initialize components
rule_engine = RuleEngine()
notifier = WebSocketNotifier()

# Create tables
with app.app_context():
    db.create_all()
    logger.info("Database tables created")

# Initialize consumer
consumer = AlertConsumer(rule_engine, notifier, db, app)


def start_consumer():
    """Start RabbitMQ consumer in background thread"""
    logger.info("Starting alert consumer...")
    consumer.start_consuming()


# Start consumer in background thread
consumer_thread = threading.Thread(target=start_consumer, daemon=True)
consumer_thread.start()


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'alert-service',
        'consumer_running': consumer_thread.is_alive()
    }), 200


@app.route('/api/alerts/<int:user_id>', methods=['GET'])
def get_user_alerts(user_id):
    """Get alerts for a specific user"""
    try:
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        
        # Query alerts
        query = Alert.query.filter_by(user_id=user_id)
        
        if unread_only:
            query = query.filter_by(is_read=False)
        
        alerts = query.order_by(Alert.triggered_at.desc()).limit(limit).all()
        
        return jsonify({
            'status': 'success',
            'count': len(alerts),
            'alerts': [alert.to_dict() for alert in alerts]
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching alerts: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/alerts/<int:alert_id>/read', methods=['PUT'])
def mark_alert_read(alert_id):
    """Mark an alert as read"""
    try:
        alert = Alert.query.get(alert_id)
        
        if not alert:
            return jsonify({
                'status': 'error',
                'message': 'Alert not found'
            }), 404
        
        alert.is_read = True
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Alert marked as read'
        }), 200
        
    except Exception as e:
        logger.error(f"Error marking alert as read: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/alert-rules', methods=['POST'])
def create_alert_rule():
    """Create a new alert rule"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_id', 'symbol', 'rule_type', 'threshold_value']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Create alert rule
        rule = AlertRule(
            user_id=data['user_id'],
            symbol=data['symbol'].upper(),
            rule_type=data['rule_type'],
            threshold_value=data['threshold_value'],
            is_active=data.get('is_active', True)
        )
        
        db.session.add(rule)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'rule': rule.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating alert rule: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/alert-rules/<int:user_id>', methods=['GET'])
def get_user_alert_rules(user_id):
    """Get alert rules for a user"""
    try:
        rules = AlertRule.query.filter_by(user_id=user_id, is_active=True).all()
        
        return jsonify({
            'status': 'success',
            'count': len(rules),
            'rules': [rule.to_dict() for rule in rules]
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching alert rules: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/alert-rules/<int:rule_id>', methods=['DELETE'])
def delete_alert_rule(rule_id):
    """Delete an alert rule"""
    try:
        rule = AlertRule.query.get(rule_id)
        
        if not rule:
            return jsonify({
                'status': 'error',
                'message': 'Rule not found'
            }), 404
        
        db.session.delete(rule)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Alert rule deleted'
        }), 200
        
    except Exception as e:
        logger.error(f"Error deleting alert rule: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=False)
