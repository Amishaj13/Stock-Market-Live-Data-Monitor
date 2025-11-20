"""
Configuration Module for Stock Fetcher Service
"""

import os


class Config:
    """Application configuration"""
    
    # Flask configuration
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = FLASK_ENV == 'development'
    
    # RabbitMQ configuration
    RABBITMQ_URL = os.getenv(
        'RABBITMQ_URL',
        'amqp://stockuser:stockpass123@localhost:5672/'
    )
    
    # Fetch interval in seconds
    FETCH_INTERVAL = int(os.getenv('FETCH_INTERVAL', 30))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
