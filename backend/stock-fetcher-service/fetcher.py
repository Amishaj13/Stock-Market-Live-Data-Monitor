"""
Stock Fetcher Module
Fetches live stock data from Yahoo Finance API with retry logic
"""

import yfinance as yf
from datetime import datetime
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class StockFetcher:
    """Fetches stock data from Yahoo Finance API"""
    
    def __init__(self):
        logger.info("StockFetcher initialized")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def fetch_stock_data(self, symbol):
        """
        Fetch current stock data for a given symbol
        
        Args:
            symbol (str): Stock symbol (e.g., 'AAPL')
            
        Returns:
            dict: Stock data including price, volume, timestamp
        """
        try:
            logger.info(f"Fetching data for {symbol}")
            
            # Create ticker object
            ticker = yf.Ticker(symbol)
            
            # Get current data
            info = ticker.info
            
            # Get latest price from fast_info (more reliable)
            try:
                current_price = ticker.fast_info.last_price
            except:
                # Fallback to regular price
                current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            
            if not current_price:
                logger.error(f"No price data available for {symbol}")
                return None
            
            # Prepare stock data
            stock_data = {
                'symbol': symbol,
                'price': float(current_price),
                'volume': info.get('volume', 0),
                'market_cap': info.get('marketCap', 0),
                'timestamp': datetime.utcnow().isoformat(),
                'source': 'yahoo_finance'
            }
            
            # Add optional fields if available
            if 'open' in info:
                stock_data['open'] = float(info['open'])
            if 'dayHigh' in info:
                stock_data['high'] = float(info['dayHigh'])
            if 'dayLow' in info:
                stock_data['low'] = float(info['dayLow'])
            if 'previousClose' in info:
                stock_data['previous_close'] = float(info['previousClose'])
            
            logger.info(f"Successfully fetched {symbol}: ${current_price}")
            return stock_data
            
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {str(e)}")
            raise
    
    def fetch_multiple_stocks(self, symbols):
        """
        Fetch data for multiple stock symbols
        
        Args:
            symbols (list): List of stock symbols
            
        Returns:
            dict: Dictionary mapping symbols to their data
        """
        results = {}
        
        for symbol in symbols:
            try:
                data = self.fetch_stock_data(symbol)
                if data:
                    results[symbol] = data
            except Exception as e:
                logger.error(f"Failed to fetch {symbol}: {str(e)}")
                results[symbol] = None
        
        return results
