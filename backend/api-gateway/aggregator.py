"""
Data Aggregator Module
Aggregates data from multiple services
"""

import requests
import logging
from config import Config

logger = logging.getLogger(__name__)


class DataAggregator:
    """Aggregates data from multiple microservices"""
    
    def __init__(self):
        self.processor_url = Config.STOCK_PROCESSOR_URL
    
    def get_dashboard_data(self, watchlist):
        """
        Get aggregated dashboard data for user's watchlist
        
        Args:
            watchlist (list): List of watchlist items
            
        Returns:
            dict: Aggregated dashboard data
        """
        dashboard_data = {
            'stocks': [],
            'summary': {
                'total_stocks': len(watchlist),
                'gainers': 0,
                'losers': 0
            }
        }
        
        for item in watchlist:
            symbol = item['symbol']
            
            try:
                # Get latest stock data
                response = requests.get(
                    f"{self.processor_url}/api/stocks/latest/{symbol}",
                    timeout=5
                )
                
                if response.status_code == 200:
                    stock_data = response.json().get('data', {})
                    dashboard_data['stocks'].append(stock_data)
                    
                    # Update summary
                    change_percent = stock_data.get('change_percent', 0)
                    if change_percent > 0:
                        dashboard_data['summary']['gainers'] += 1
                    elif change_percent < 0:
                        dashboard_data['summary']['losers'] += 1
                        
            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {str(e)}")
        
        return dashboard_data
    
    def get_stock_full_data(self, symbol):
        """
        Get complete stock data (latest + history + analytics)
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            dict: Complete stock data
        """
        full_data = {}
        
        try:
            # Get latest data
            response = requests.get(
                f"{self.processor_url}/api/stocks/latest/{symbol}",
                timeout=5
            )
            if response.status_code == 200:
                full_data['latest'] = response.json().get('data', {})
            
            # Get history
            response = requests.get(
                f"{self.processor_url}/api/stocks/history/{symbol}",
                params={'limit': 50},
                timeout=5
            )
            if response.status_code == 200:
                full_data['history'] = response.json().get('data', [])
            
            # Get analytics
            response = requests.get(
                f"{self.processor_url}/api/stocks/analytics/{symbol}",
                timeout=5
            )
            if response.status_code == 200:
                full_data['analytics'] = response.json().get('analytics', {})
                
        except Exception as e:
            logger.error(f"Error aggregating data for {symbol}: {str(e)}")
        
        return full_data
