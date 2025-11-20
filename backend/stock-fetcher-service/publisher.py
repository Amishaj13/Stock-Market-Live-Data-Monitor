"""
RabbitMQ Publisher Module
Publishes stock data to RabbitMQ message queue
"""

import pika
import json
import logging
from config import Config

logger = logging.getLogger(__name__)


class RabbitMQPublisher:
    """Publishes messages to RabbitMQ"""
    
    def __init__(self):
        self.rabbitmq_url = Config.RABBITMQ_URL
        self.queue_name = 'stock.raw'
        self.connection = None
        self.channel = None
        self._connect()
    
    def _connect(self):
        """Establish connection to RabbitMQ"""
        try:
            # Parse connection URL
            parameters = pika.URLParameters(self.rabbitmq_url)
            
            # Create connection
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare queue (idempotent operation)
            self.channel.queue_declare(
                queue=self.queue_name,
                durable=True,  # Survive broker restart
                arguments={'x-message-ttl': 60000}  # Message TTL: 60 seconds
            )
            
            logger.info(f"Connected to RabbitMQ, queue: {self.queue_name}")
            
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
            raise
    
    def publish_stock_data(self, stock_data):
        """
        Publish stock data to RabbitMQ queue
        
        Args:
            stock_data (dict): Stock data to publish
        """
        try:
            # Ensure connection is alive
            if not self.connection or self.connection.is_closed:
                logger.warning("Connection closed, reconnecting...")
                self._connect()
            
            # Convert to JSON
            message = json.dumps(stock_data)
            
            # Publish message
            self.channel.basic_publish(
                exchange='',
                routing_key=self.queue_name,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type='application/json'
                )
            )
            
            logger.debug(f"Published to {self.queue_name}: {stock_data['symbol']}")
            
        except Exception as e:
            logger.error(f"Failed to publish message: {str(e)}")
            # Try to reconnect
            try:
                self._connect()
            except:
                pass
            raise
    
    def close(self):
        """Close RabbitMQ connection"""
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.info("RabbitMQ connection closed")
        except Exception as e:
            logger.error(f"Error closing connection: {str(e)}")
