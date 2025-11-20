"""
Configuration Module for API Gateway
"""

import os


class Config:
    """Application configuration"""
    
    # Flask configuration
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = FLASK_ENV == 'development'
    
    # Service URLs
    USER_SERVICE_URL = os.getenv('USER_SERVICE_URL', 'http://localhost:5004')
    STOCK_PROCESSOR_URL = os.getenv('STOCK_PROCESSOR_URL', 'http://localhost:5002')
    ALERT_SERVICE_URL = os.getenv('ALERT_SERVICE_URL', 'http://localhost:5003')
    
    # Redis configuration
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # JWT configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
