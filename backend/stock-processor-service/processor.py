"""
Stock Processor Module
Validates stock data, computes analytics, and publishes alerts
"""

import logging
from datetime import datetime
import pika
import json
from config import Config

logger = logging.getLogger(__name__)


class StockProcessor:
    """Processes stock data and computes analytics"""
    
    def __init__(self, redis_cache, mongodb):
        self.redis_cache = redis_cache
        self.mongodb = mongodb
        self.alert_publisher = AlertPublisher()
        logger.info("StockProcessor initialized")
    
    def validate_stock_data(self, stock_data):
        """
        Validate stock data schema
        
        Args:
            stock_data (dict): Stock data to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        required_fields = ['symbol', 'price', 'timestamp']
        
        for field in required_fields:
            if field not in stock_data:
                logger.error(f"Missing required field: {field}")
                return False
        
        # Validate price is positive
        if stock_data['price'] <= 0:
            logger.error(f"Invalid price: {stock_data['price']}")
            return False
        
        return True
    
    def compute_analytics(self, stock_data, previous_data):
        """
        Compute analytics like change percentage and trend
        
        Args:
            stock_data (dict): Current stock data
            previous_data (dict): Previous stock data
            
        Returns:
            dict: Analytics data
        """
        analytics = {
            'change': 0,
            'change_percent': 0,
            'trend': 'NEUTRAL',
            'volatility': 'LOW'
        }
        
        if previous_data:
            prev_price = previous_data.get('price', 0)
            current_price = stock_data['price']
            
            if prev_price > 0:
                # Calculate change
                analytics['change'] = round(current_price - prev_price, 2)
                analytics['change_percent'] = round(
                    ((current_price - prev_price) / prev_price) * 100, 2
                )
                
                # Determine trend
                if analytics['change_percent'] > 0.5:
                    analytics['trend'] = 'UP'
                elif analytics['change_percent'] < -0.5:
                    analytics['trend'] = 'DOWN'
                
                # Determine volatility
                if abs(analytics['change_percent']) > 2:
                    analytics['volatility'] = 'HIGH'
                elif abs(analytics['change_percent']) > 1:
                    analytics['volatility'] = 'MEDIUM'
        
        return analytics
    
    def process_stock_data(self, stock_data):
        """
        Main processing function
        
        Args:
            stock_data (dict): Raw stock data from fetcher
        """
        try:
            # Validate data
            if not self.validate_stock_data(stock_data):
                logger.warning(f"Invalid stock data for {stock_data.get('symbol')}")
                return
            
            symbol = stock_data['symbol']
            
            # Get previous data from cache
            previous_data = self.redis_cache.get_latest_stock(symbol)
            
            # Compute analytics
            analytics = self.compute_analytics(stock_data, previous_data)
            
            # Merge analytics with stock data
            processed_data = {
                **stock_data,
                **analytics,
                'processed_at': datetime.utcnow().isoformat()
            }
            
            # Cache latest price in Redis
            self.redis_cache.set_latest_stock(symbol, processed_data)
            logger.info(f"Cached {symbol} in Redis")
            
            # Store historical data in MongoDB
            self.mongodb.insert_stock_data(processed_data)
            logger.info(f"Stored {symbol} in MongoDB")
            
            # Publish to stock.processed queue
            self.alert_publisher.publish_processed_data(processed_data)
            
            # Check for alert conditions
            if abs(analytics['change_percent']) > 1.5:
                alert_data = {
                    'symbol': symbol,
                    'alert_type': 'SUDDEN_RISE' if analytics['change_percent'] > 0 else 'SUDDEN_DROP',
                    'current_price': stock_data['price'],
                    'previous_price': previous_data['price'] if previous_data else 0,
                    'change_percent': analytics['change_percent'],
                    'threshold': 1.5,
                    'timestamp': datetime.utcnow().isoformat()
                }
                self.alert_publisher.publish_alert(alert_data)
                logger.warning(f"Alert triggered for {symbol}: {analytics['change_percent']}%")
            
        except Exception as e:
            logger.error(f"Error processing stock data: {str(e)}")
            raise
    
    def compute_advanced_analytics(self, history):
        """
        Compute advanced analytics from historical data
        
        Args:
            history (list): List of historical stock data
            
        Returns:
            dict: Advanced analytics
        """
        if not history or len(history) < 2:
            return {
                'avg_price': 0,
                'min_price': 0,
                'max_price': 0,
                'price_range': 0,
                'trend_direction': 'INSUFFICIENT_DATA'
            }
        
        prices = [item['price'] for item in history]
        
        analytics = {
            'avg_price': round(sum(prices) / len(prices), 2),
            'min_price': round(min(prices), 2),
            'max_price': round(max(prices), 2),
            'price_range': round(max(prices) - min(prices), 2),
            'data_points': len(history)
        }
        
        # Simple trend detection
        recent_avg = sum(prices[:len(prices)//2]) / (len(prices)//2)
        older_avg = sum(prices[len(prices)//2:]) / (len(prices) - len(prices)//2)
        
        if recent_avg > older_avg * 1.01:
            analytics['trend_direction'] = 'UPWARD'
        elif recent_avg < older_avg * 0.99:
            analytics['trend_direction'] = 'DOWNWARD'
        else:
            analytics['trend_direction'] = 'STABLE'
        
        return analytics


class AlertPublisher:
    """Publishes alert messages to RabbitMQ"""
    
    def __init__(self):
        self.rabbitmq_url = Config.RABBITMQ_URL
        self.connection = None
        self.channel = None
        self._connect()
    
    def _connect(self):
        """Establish connection to RabbitMQ"""
        try:
            parameters = pika.URLParameters(self.rabbitmq_url)
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare queues
            self.channel.queue_declare(queue='stock.processed', durable=True)
            self.channel.queue_declare(queue='alert.trigger', durable=True)
            
            logger.info("Alert publisher connected to RabbitMQ")
            
        except Exception as e:
            logger.error(f"Failed to connect alert publisher: {str(e)}")
            raise
    
    def publish_processed_data(self, data):
        """Publish processed stock data"""
        try:
            if not self.connection or self.connection.is_closed:
                self._connect()
            
            message = json.dumps(data)
            self.channel.basic_publish(
                exchange='',
                routing_key='stock.processed',
                body=message,
                properties=pika.BasicProperties(delivery_mode=2)
            )
            logger.debug(f"Published to stock.processed: {data['symbol']}")
            
        except Exception as e:
            logger.error(f"Failed to publish processed data: {str(e)}")
    
    def publish_alert(self, alert_data):
        """Publish alert trigger"""
        try:
            if not self.connection or self.connection.is_closed:
                self._connect()
            
            message = json.dumps(alert_data)
            self.channel.basic_publish(
                exchange='',
                routing_key='alert.trigger',
                body=message,
                properties=pika.BasicProperties(delivery_mode=2)
            )
            logger.info(f"Published alert: {alert_data['symbol']} - {alert_data['alert_type']}")
            
        except Exception as e:
            logger.error(f"Failed to publish alert: {str(e)}")
