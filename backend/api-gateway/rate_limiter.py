"""
Rate Limiter Module
Redis-based rate limiting
"""

import redis
from config import Config
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter using Redis"""
    
    def __init__(self):
        self.redis_client = redis.from_url(Config.REDIS_URL)
        self.limits = {
            'default': (100, 60),  # 100 requests per 60 seconds
            'login': (5, 60),      # 5 login attempts per 60 seconds
            'signup': (3, 300)     # 3 signups per 5 minutes
        }
    
    def check_rate_limit(self, endpoint='default', identifier=None):
        """
        Check if request is within rate limit
        
        Args:
            endpoint (str): Endpoint name
            identifier (str): User identifier (IP, user_id, etc.)
            
        Returns:
            bool: True if within limit, False if exceeded
        """
        try:
            # Get limit configuration
            max_requests, window = self.limits.get(endpoint, self.limits['default'])
            
            # Use IP as identifier if not provided
            if not identifier:
                from flask import request
                identifier = request.remote_addr
            
            # Create Redis key
            key = f"ratelimit:{endpoint}:{identifier}"
            
            # Get current count
            current = self.redis_client.get(key)
            
            if current is None:
                # First request in window
                self.redis_client.setex(key, window, 1)
                return True
            
            current = int(current)
            
            if current >= max_requests:
                logger.warning(f"Rate limit exceeded for {endpoint} by {identifier}")
                return False
            
            # Increment counter
            self.redis_client.incr(key)
            return True
            
        except Exception as e:
            logger.error(f"Rate limiter error: {str(e)}")
            # Fail open - allow request if rate limiter fails
            return True
