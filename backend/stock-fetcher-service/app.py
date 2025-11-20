"""
Stock Fetcher Service - Main Application
Fetches live stock data from Yahoo Finance API and publishes to RabbitMQ
"""

from flask import Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from fetcher import StockFetcher
from publisher import RabbitMQPublisher
from config import Config
import logging
import atexit

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Initialize components
stock_fetcher = StockFetcher()
publisher = RabbitMQPublisher()

# List of stocks to monitor
STOCK_SYMBOLS = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM']


def fetch_and_publish_stocks():
    """
    Fetch stock data for all symbols and publish to RabbitMQ
    This function runs periodically based on scheduler
    """
    logger.info(f"Starting stock fetch cycle for {len(STOCK_SYMBOLS)} symbols")
    
    for symbol in STOCK_SYMBOLS:
        try:
            # Fetch stock data
            stock_data = stock_fetcher.fetch_stock_data(symbol)
            
            if stock_data:
                # Publish to RabbitMQ
                publisher.publish_stock_data(stock_data)
                logger.info(f"Published data for {symbol}: ${stock_data['price']}")
            else:
                logger.warning(f"No data received for {symbol}")
                
        except Exception as e:
            logger.error(f"Error processing {symbol}: {str(e)}")
    
    logger.info("Stock fetch cycle completed")


# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(
    func=fetch_and_publish_stocks,
    trigger="interval",
    seconds=app.config['FETCH_INTERVAL'],
    id='stock_fetcher_job',
    name='Fetch and publish stock data',
    replace_existing=True
)

# Start scheduler
scheduler.start()
logger.info(f"Scheduler started - fetching every {app.config['FETCH_INTERVAL']} seconds")

# Shutdown scheduler on app exit
atexit.register(lambda: scheduler.shutdown())


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'stock-fetcher-service',
        'scheduler_running': scheduler.running,
        'monitored_stocks': STOCK_SYMBOLS
    }), 200


@app.route('/fetch-now', methods=['POST'])
def fetch_now():
    """Manual trigger for stock fetching (for testing)"""
    try:
        fetch_and_publish_stocks()
        return jsonify({
            'status': 'success',
            'message': 'Stock data fetched and published'
        }), 200
    except Exception as e:
        logger.error(f"Manual fetch failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


if __name__ == '__main__':
    # Run initial fetch on startup
    logger.info("Running initial stock fetch on startup...")
    fetch_and_publish_stocks()
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5001, debug=False)
