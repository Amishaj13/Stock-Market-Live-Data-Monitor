"""
Stock Processor Service - Main Application
Consumes stock data from RabbitMQ, processes analytics, caches in Redis, stores in MongoDB
"""

from flask import Flask, jsonify, request
from consumer import RabbitMQConsumer
from processor import StockProcessor
from cache import RedisCache
from database import PostgreSQLDB
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

# Initialize components
redis_cache = RedisCache()
postgres_db = PostgreSQLDB()
stock_processor = StockProcessor(redis_cache, postgres_db)
consumer = RabbitMQConsumer(stock_processor)


def start_consumer():
    """Start RabbitMQ consumer in background thread"""
    logger.info("Starting RabbitMQ consumer...")
    consumer.start_consuming()


# Start consumer in background thread
consumer_thread = threading.Thread(target=start_consumer, daemon=True)
consumer_thread.start()


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    redis_status = redis_cache.ping()
    postgres_status = postgres_db.ping()
    
    return jsonify({
        'status': 'healthy',
        'service': 'stock-processor-service',
        'redis_connected': redis_status,
        'postgresql_connected': postgres_status,
        'consumer_running': consumer_thread.is_alive()
    }), 200


@app.route('/api/stocks/latest/<symbol>', methods=['GET'])
def get_latest_stock(symbol):
    """Get latest stock data from Redis cache"""
    try:
        data = redis_cache.get_latest_stock(symbol.upper())
        
        if data:
            return jsonify({
                'status': 'success',
                'data': data
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': f'No data found for {symbol}'
            }), 404
            
    except Exception as e:
        logger.error(f"Error fetching latest stock: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/stocks/history/<symbol>', methods=['GET'])
def get_stock_history(symbol):
    """Get historical stock data from MongoDB"""
    try:
        # Get query parameters
        limit = request.args.get('limit', 100, type=int)
        hours = request.args.get('hours', 24, type=int)
        
        # Fetch from PostgreSQL
        history = postgres_db.get_stock_history(symbol.upper(), hours=hours, limit=limit)
        
        return jsonify({
            'status': 'success',
            'symbol': symbol.upper(),
            'count': len(history),
            'data': history
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching stock history: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/stocks/analytics/<symbol>', methods=['GET'])
def get_stock_analytics(symbol):
    """Get computed analytics for a stock"""
    try:
        # Get latest data from cache
        latest = redis_cache.get_latest_stock(symbol.upper())
        
        if not latest:
            return jsonify({
                'status': 'error',
                'message': f'No data found for {symbol}'
            }), 404
        
        # Get historical data for trend analysis
        history = postgres_db.get_stock_history(symbol.upper(), hours=24, limit=100)
        
        # Compute additional analytics
        analytics = stock_processor.compute_advanced_analytics(history)
        
        return jsonify({
            'status': 'success',
            'symbol': symbol.upper(),
            'latest': latest,
            'analytics': analytics
        }), 200
        
    except Exception as e:
        logger.error(f"Error computing analytics: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=False)
