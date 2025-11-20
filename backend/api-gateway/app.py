"""
API Gateway Service - Main Application
Single entry point for all frontend requests with routing, authentication, and WebSocket support
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sock import Sock
import requests
import redis
import json
import logging
from config import Config
from auth_middleware import verify_token
from rate_limiter import RateLimiter
from aggregator import DataAggregator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize WebSocket
sock = Sock(app)

# Initialize components
rate_limiter = RateLimiter()
data_aggregator = DataAggregator()

# Redis for pub/sub
redis_client = redis.from_url(Config.REDIS_URL)
pubsub = redis_client.pubsub()

# Service URLs
SERVICES = {
    'user': Config.USER_SERVICE_URL,
    'processor': Config.STOCK_PROCESSOR_URL,
    'alert': Config.ALERT_SERVICE_URL
}


def proxy_request(service_url, path, method='GET', **kwargs):
    """
    Proxy request to microservice
    
    Args:
        service_url (str): Base URL of the service
        path (str): API path
        method (str): HTTP method
        **kwargs: Additional arguments for requests
        
    Returns:
        tuple: (response_data, status_code)
    """
    try:
        url = f"{service_url}{path}"
        
        # Forward headers
        headers = {}
        if 'Authorization' in request.headers:
            headers['Authorization'] = request.headers['Authorization']
        if 'Content-Type' in request.headers:
            headers['Content-Type'] = request.headers['Content-Type']
        
        # Make request
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            timeout=10,
            **kwargs
        )
        
        return response.json(), response.status_code
        
    except requests.exceptions.Timeout:
        logger.error(f"Timeout calling {service_url}{path}")
        return {'status': 'error', 'message': 'Service timeout'}, 504
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error to {service_url}{path}")
        return {'status': 'error', 'message': 'Service unavailable'}, 503
    except Exception as e:
        logger.error(f"Error proxying request: {str(e)}")
        return {'status': 'error', 'message': str(e)}, 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'api-gateway'
    }), 200


# ==================== Authentication Routes ====================

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """Proxy signup to user service"""
    if not rate_limiter.check_rate_limit('signup'):
        return jsonify({'status': 'error', 'message': 'Rate limit exceeded'}), 429
    
    data, status = proxy_request(
        SERVICES['user'],
        '/api/auth/signup',
        method='POST',
        json=request.get_json()
    )
    return jsonify(data), status


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Proxy login to user service"""
    if not rate_limiter.check_rate_limit('login'):
        return jsonify({'status': 'error', 'message': 'Rate limit exceeded'}), 429
    
    data, status = proxy_request(
        SERVICES['user'],
        '/api/auth/login',
        method='POST',
        json=request.get_json()
    )
    return jsonify(data), status


@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    """Proxy get current user to user service"""
    data, status = proxy_request(SERVICES['user'], '/api/auth/me')
    return jsonify(data), status


# ==================== Watchlist Routes ====================

@app.route('/api/watchlist', methods=['GET'])
def get_watchlist():
    """Proxy get watchlist to user service"""
    data, status = proxy_request(SERVICES['user'], '/api/watchlist')
    return jsonify(data), status


@app.route('/api/watchlist', methods=['POST'])
def add_to_watchlist():
    """Proxy add to watchlist to user service"""
    data, status = proxy_request(
        SERVICES['user'],
        '/api/watchlist',
        method='POST',
        json=request.get_json()
    )
    return jsonify(data), status


@app.route('/api/watchlist/<int:item_id>', methods=['DELETE'])
def remove_from_watchlist(item_id):
    """Proxy remove from watchlist to user service"""
    data, status = proxy_request(
        SERVICES['user'],
        f'/api/watchlist/{item_id}',
        method='DELETE'
    )
    return jsonify(data), status


# ==================== Stock Data Routes ====================

@app.route('/api/stocks/latest/<symbol>', methods=['GET'])
def get_latest_stock(symbol):
    """Get latest stock data from processor service"""
    data, status = proxy_request(
        SERVICES['processor'],
        f'/api/stocks/latest/{symbol}'
    )
    return jsonify(data), status


@app.route('/api/stocks/history/<symbol>', methods=['GET'])
def get_stock_history(symbol):
    """Get stock history from processor service"""
    # Forward query parameters
    params = request.args.to_dict()
    data, status = proxy_request(
        SERVICES['processor'],
        f'/api/stocks/history/{symbol}',
        params=params
    )
    return jsonify(data), status


@app.route('/api/stocks/analytics/<symbol>', methods=['GET'])
def get_stock_analytics(symbol):
    """Get stock analytics from processor service"""
    data, status = proxy_request(
        SERVICES['processor'],
        f'/api/stocks/analytics/{symbol}'
    )
    return jsonify(data), status


@app.route('/api/stocks/dashboard', methods=['GET'])
def get_dashboard_data():
    """Aggregated dashboard data"""
    try:
        # Verify token
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'status': 'error', 'message': 'Authorization required'}), 401
        
        # Get user's watchlist
        watchlist_data, status = proxy_request(SERVICES['user'], '/api/watchlist')
        
        if status != 200:
            return jsonify(watchlist_data), status
        
        # Get latest data for watchlist stocks
        dashboard_data = data_aggregator.get_dashboard_data(watchlist_data.get('watchlist', []))
        
        return jsonify({
            'status': 'success',
            'data': dashboard_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting dashboard data: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ==================== Alert Routes ====================

@app.route('/api/alerts/<int:user_id>', methods=['GET'])
def get_user_alerts(user_id):
    """Proxy get alerts to alert service"""
    params = request.args.to_dict()
    data, status = proxy_request(
        SERVICES['alert'],
        f'/api/alerts/{user_id}',
        params=params
    )
    return jsonify(data), status


@app.route('/api/alert-rules', methods=['POST'])
def create_alert_rule():
    """Proxy create alert rule to alert service"""
    data, status = proxy_request(
        SERVICES['alert'],
        '/api/alert-rules',
        method='POST',
        json=request.get_json()
    )
    return jsonify(data), status


# ==================== WebSocket Route ====================

@sock.route('/ws/stocks')
def stock_websocket(ws):
    """
    WebSocket endpoint for real-time stock updates
    Subscribes to Redis pub/sub and pushes to connected clients
    """
    logger.info("New WebSocket connection established")
    
    try:
        # Subscribe to Redis channels
        pubsub.subscribe('stock:updates', 'alerts:notifications')
        
        # Send initial connection message
        ws.send(json.dumps({
            'type': 'connection',
            'message': 'Connected to stock updates'
        }))
        
        # Listen for messages
        for message in pubsub.listen():
            if message['type'] == 'message':
                # Forward to WebSocket client
                ws.send(message['data'])
            
            # Check if client is still connected
            try:
                # Non-blocking receive to check connection
                data = ws.receive(timeout=0.1)
                if data:
                    # Handle client messages if needed
                    pass
            except:
                # Client disconnected
                break
                
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        pubsub.unsubscribe()
        logger.info("WebSocket connection closed")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
