"""
Authentication Middleware for API Gateway
"""

import jwt
from config import Config
import logging

logger = logging.getLogger(__name__)


def verify_token(token):
    """
    Verify JWT token
    
    Args:
        token (str): JWT token
        
    Returns:
        dict: Decoded payload or None if invalid
    """
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        return None
    except jwt.InvalidTokenError:
        logger.warning("Invalid token")
        return None
