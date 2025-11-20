"""
Middleware Module
JWT token creation and validation
"""

import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from models import User
from config import Config
import logging

logger = logging.getLogger(__name__)


def create_token(user_id):
    """
    Create JWT token for user
    
    Args:
        user_id (int): User ID
        
    Returns:
        str: JWT token
    """
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=1),  # Token expires in 24 hours
        'iat': datetime.utcnow()
    }
    
    token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')
    return token


def decode_token(token):
    """
    Decode and validate JWT token
    
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


def token_required(f):
    """
    Decorator to protect routes with JWT authentication
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid authorization header format'
                }), 401
        
        if not token:
            return jsonify({
                'status': 'error',
                'message': 'Token is missing'
            }), 401
        
        # Decode token
        payload = decode_token(token)
        
        if not payload:
            return jsonify({
                'status': 'error',
                'message': 'Token is invalid or expired'
            }), 401
        
        # Get user from database
        current_user = User.query.get(payload['user_id'])
        
        if not current_user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 401
        
        # Pass current user to the route
        return f(current_user, *args, **kwargs)
    
    return decorated
