"""
RabbitMQ Consumer Module
Consumes stock data from RabbitMQ and processes it
"""

import pika
import json
import logging
from config import Config

logger = logging.getLogger(__name__)


class RabbitMQConsumer:
    """Consumes messages from RabbitMQ"""
    
    def __init__(self, stock_processor):
        self.rabbitmq_url = Config.RABBITMQ_URL
        self.queue_name = 'stock.raw'
        self.stock_processor = stock_processor
        self.connection = None
        self.channel = None
    
    def _connect(self):
        """Establish connection to RabbitMQ"""
        try:
            parameters = pika.URLParameters(self.rabbitmq_url)
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare queue
            self.channel.queue_declare(
                queue=self.queue_name,
                durable=True
            )
            
            # Set QoS - process one message at a time
            self.channel.basic_qos(prefetch_count=1)
            
            logger.info(f"Connected to RabbitMQ, consuming from: {self.queue_name}")
            
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
            raise
    
    def callback(self, ch, method, properties, body):
        """
        Callback function for processing messages
        
        Args:
            ch: Channel
            method: Delivery method
            properties: Message properties
            body: Message body
        """
        try:
            # Parse message
            stock_data = json.loads(body)
            logger.info(f"Received: {stock_data['symbol']} - ${stock_data['price']}")
            
            # Process stock data
            self.stock_processor.process_stock_data(stock_data)
            
            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.debug(f"Processed and acknowledged: {stock_data['symbol']}")
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON message: {str(e)}")
            # Reject and don't requeue invalid messages
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            # Reject and requeue for retry
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def start_consuming(self):
        """Start consuming messages from queue"""
        try:
            self._connect()
            
            # Set up consumer
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=self.callback,
                auto_ack=False  # Manual acknowledgment
            )
            
            logger.info("Started consuming messages...")
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("Consumer stopped by user")
            self.stop_consuming()
            
        except Exception as e:
            logger.error(f"Consumer error: {str(e)}")
            raise
    
    def stop_consuming(self):
        """Stop consuming messages"""
        try:
            if self.channel:
                self.channel.stop_consuming()
            if self.connection and not self.connection.is_closed:
                self.connection.close()
            logger.info("Consumer stopped")
        except Exception as e:
            logger.error(f"Error stopping consumer: {str(e)}")
