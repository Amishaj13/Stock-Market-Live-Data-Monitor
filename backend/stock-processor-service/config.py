"""
Configuration Module for Stock Processor Service
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
    
    # Redis configuration
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # PostgreSQL configuration (for stock history)
    DATABASE_URL = os.getenv(
        'DATABASE_URL',
        'postgresql://stockuser:stockpass123@localhost:5432/stockdb'
    )
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
