"""
Alert Consumer Module
Consumes alert events from RabbitMQ
"""

import pika
import json
import logging
from models import Alert
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)


class AlertConsumer:
    """Consumes alert messages from RabbitMQ"""
    
    def __init__(self, rule_engine, notifier, db, app):
        self.rabbitmq_url = Config.RABBITMQ_URL
        self.queue_name = 'alert.trigger'
        self.processed_queue = 'stock.processed'
        self.rule_engine = rule_engine
        self.notifier = notifier
        self.db = db
        self.app = app
        self.connection = None
        self.channel = None
    
    def _connect(self):
        """Establish connection to RabbitMQ"""
        try:
            parameters = pika.URLParameters(self.rabbitmq_url)
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare queues
            self.channel.queue_declare(queue=self.queue_name, durable=True)
            self.channel.queue_declare(queue=self.processed_queue, durable=True)
            
            # Set QoS
            self.channel.basic_qos(prefetch_count=1)
            
            logger.info(f"Connected to RabbitMQ for alert consumption")
            
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
            raise
    
    def process_alert_trigger(self, alert_data):
        """Process alert trigger event"""
        try:
            with self.app.app_context():
                # Create alert message
                message = f"{alert_data['symbol']} {alert_data['alert_type']}: " \
                         f"Price changed by {alert_data['change_percent']}%"
                
                # Store alert in database (for all users watching this stock)
                # In a real system, you'd query which users are watching this stock
                # For now, we'll create a system alert
                alert = Alert(
                    user_id=1,  # System user or specific user
                    symbol=alert_data['symbol'],
                    alert_type=alert_data['alert_type'],
                    threshold=alert_data.get('threshold'),
                    message=message
                )
                
                self.db.session.add(alert)
                self.db.session.commit()
                
                logger.info(f"Alert stored: {message}")
                
                # Send notification via WebSocket
                self.notifier.send_notification({
                    'type': 'alert',
                    'data': alert.to_dict()
                })
                
        except Exception as e:
            logger.error(f"Error processing alert trigger: {str(e)}")
            self.db.session.rollback()
    
    def process_stock_update(self, stock_data):
        """Process stock update and check against user rules"""
        try:
            with self.app.app_context():
                # Evaluate rules for this stock
                triggered_rules = self.rule_engine.evaluate_rules(stock_data)
                
                for rule in triggered_rules:
                    # Create alert
                    message = f"{stock_data['symbol']} triggered {rule['rule_type']} rule: " \
                             f"Price ${stock_data['price']} vs threshold ${rule['threshold_value']}"
                    
                    alert = Alert(
                        user_id=rule['user_id'],
                        symbol=stock_data['symbol'],
                        alert_type=rule['rule_type'],
                        threshold=rule['threshold_value'],
                        message=message
                    )
                    
                    self.db.session.add(alert)
                    self.db.session.commit()
                    
                    logger.info(f"Rule-based alert created: {message}")
                    
                    # Send notification
                    self.notifier.send_notification({
                        'type': 'rule_alert',
                        'user_id': rule['user_id'],
                        'data': alert.to_dict()
                    })
                    
        except Exception as e:
            logger.error(f"Error processing stock update: {str(e)}")
            self.db.session.rollback()
    
    def callback(self, ch, method, properties, body):
        """Callback for processing messages"""
        try:
            data = json.loads(body)
            
            # Determine message type based on queue
            if method.routing_key == self.queue_name:
                # Alert trigger
                logger.info(f"Processing alert trigger: {data['symbol']}")
                self.process_alert_trigger(data)
            elif method.routing_key == self.processed_queue:
                # Stock update
                logger.debug(f"Processing stock update: {data['symbol']}")
                self.process_stock_update(data)
            
            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            logger.error(f"Error in callback: {str(e)}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def start_consuming(self):
        """Start consuming messages"""
        try:
            self._connect()
            
            # Consume from both queues
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=self.callback,
                auto_ack=False
            )
            
            self.channel.basic_consume(
                queue=self.processed_queue,
                on_message_callback=self.callback,
                auto_ack=False
            )
            
            logger.info("Started consuming alert messages...")
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
            logger.info("Alert consumer stopped")
        except Exception as e:
            logger.error(f"Error stopping consumer: {str(e)}")
