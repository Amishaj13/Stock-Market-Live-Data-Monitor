"""
Redis Cache Module
Handles caching of latest stock prices
"""

import redis
import json
import logging
from config import Config

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis cache for stock data"""
    
    def __init__(self):
        self.redis_url = Config.REDIS_URL
        self.client = None
        self._connect()
    
    def _connect(self):
        """Connect to Redis"""
        try:
            self.client = redis.from_url(
                self.redis_url,
                decode_responses=True
            )
            # Test connection
            self.client.ping()
            logger.info("Connected to Redis")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            raise
    
    def ping(self):
        """Check Redis connection"""
        try:
            return self.client.ping()
        except:
            return False
    
    def set_latest_stock(self, symbol, stock_data, ttl=300):
        """
        Cache latest stock data
        
        Args:
            symbol (str): Stock symbol
            stock_data (dict): Stock data to cache
            ttl (int): Time to live in seconds (default: 5 minutes)
        """
        try:
            key = f"stock:latest:{symbol}"
            value = json.dumps(stock_data)
            
            # Set with TTL
            self.client.setex(key, ttl, value)
            logger.debug(f"Cached {symbol} with TTL {ttl}s")
            
        except Exception as e:
            logger.error(f"Error caching stock data: {str(e)}")
            raise
    
    def get_latest_stock(self, symbol):
        """
        Get latest stock data from cache
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            dict: Stock data or None if not found
        """
        try:
            key = f"stock:latest:{symbol}"
            value = self.client.get(key)
            
            if value:
                return json.loads(value)
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving from cache: {str(e)}")
            return None
    
    def get_multiple_stocks(self, symbols):
        """
        Get multiple stocks at once
        
        Args:
            symbols (list): List of stock symbols
            
        Returns:
            dict: Dictionary mapping symbols to their data
        """
        result = {}
        
        for symbol in symbols:
            data = self.get_latest_stock(symbol)
            if data:
                result[symbol] = data
        
        return result
    
    def delete_stock(self, symbol):
        """Delete stock from cache"""
        try:
            key = f"stock:latest:{symbol}"
            self.client.delete(key)
            logger.debug(f"Deleted {symbol} from cache")
            
        except Exception as e:
            logger.error(f"Error deleting from cache: {str(e)}")
