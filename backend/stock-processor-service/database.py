"""
PostgreSQL Database Module
Handles storage of historical stock data
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import logging
from config import Config

logger = logging.getLogger(__name__)

Base = declarative_base()


class StockHistory(Base):
    """Stock history model"""
    
    __tablename__ = 'stock_history'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), nullable=False, index=True)
    price = Column(Float, nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    volume = Column(Integer)
    change = Column(Float)
    change_percent = Column(Float)
    trend = Column(String(20))
    volatility = Column(String(20))
    timestamp = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Composite index for efficient queries
    __table_args__ = (
        Index('idx_symbol_timestamp', 'symbol', 'timestamp'),
        Index('idx_created_at', 'created_at'),
    )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'price': self.price,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'volume': self.volume,
            'change': self.change,
            'change_percent': self.change_percent,
            'trend': self.trend,
            'volatility': self.volatility,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class PostgreSQLDB:
    """PostgreSQL handler for historical stock data"""
    
    def __init__(self):
        self.database_url = Config.DATABASE_URL
        self.engine = None
        self.Session = None
        self._connect()
    
    def _connect(self):
        """Connect to PostgreSQL"""
        try:
            self.engine = create_engine(self.database_url)
            self.Session = sessionmaker(bind=self.engine)
            
            # Create tables
            Base.metadata.create_all(self.engine)
            
            logger.info("Connected to PostgreSQL for stock history")
            
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {str(e)}")
            raise
    
    def ping(self):
        """Check PostgreSQL connection"""
        try:
            session = self.Session()
            session.execute('SELECT 1')
            session.close()
            return True
        except:
            return False
    
    def insert_stock_data(self, stock_data):
        """
        Insert stock data into PostgreSQL
        
        Args:
            stock_data (dict): Stock data to insert
        """
        try:
            session = self.Session()
            
            # Parse timestamp
            timestamp = stock_data.get('timestamp')
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            # Create stock history record
            stock_record = StockHistory(
                symbol=stock_data['symbol'],
                price=stock_data['price'],
                open=stock_data.get('open'),
                high=stock_data.get('high'),
                low=stock_data.get('low'),
                volume=stock_data.get('volume'),
                change=stock_data.get('change'),
                change_percent=stock_data.get('change_percent'),
                trend=stock_data.get('trend'),
                volatility=stock_data.get('volatility'),
                timestamp=timestamp or datetime.utcnow()
            )
            
            session.add(stock_record)
            session.commit()
            
            logger.debug(f"Inserted {stock_data['symbol']} with ID: {stock_record.id}")
            session.close()
            
        except Exception as e:
            logger.error(f"Error inserting stock data: {str(e)}")
            if session:
                session.rollback()
                session.close()
            raise
    
    def get_stock_history(self, symbol, hours=24, limit=100):
        """
        Get historical stock data for a symbol
        
        Args:
            symbol (str): Stock symbol
            hours (int): Number of hours to look back
            limit (int): Maximum number of records
            
        Returns:
            list: List of stock data dictionaries
        """
        try:
            session = self.Session()
            
            # Calculate time threshold
            time_threshold = datetime.utcnow() - timedelta(hours=hours)
            
            # Query with time filter
            records = session.query(StockHistory).filter(
                StockHistory.symbol == symbol,
                StockHistory.created_at >= time_threshold
            ).order_by(StockHistory.created_at.desc()).limit(limit).all()
            
            # Convert to list of dicts
            history = [record.to_dict() for record in records]
            
            logger.debug(f"Retrieved {len(history)} records for {symbol}")
            session.close()
            return history
            
        except Exception as e:
            logger.error(f"Error retrieving stock history: {str(e)}")
            if session:
                session.close()
            return []
    
    def get_latest_record(self, symbol):
        """
        Get the most recent record for a symbol
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            dict: Latest stock data or None
        """
        try:
            session = self.Session()
            
            record = session.query(StockHistory).filter(
                StockHistory.symbol == symbol
            ).order_by(StockHistory.created_at.desc()).first()
            
            result = record.to_dict() if record else None
            session.close()
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving latest record: {str(e)}")
            if session:
                session.close()
            return None
    
    def delete_old_records(self, days=30):
        """
        Delete records older than specified days
        
        Args:
            days (int): Number of days to keep
        """
        try:
            session = self.Session()
            threshold = datetime.utcnow() - timedelta(days=days)
            
            result = session.query(StockHistory).filter(
                StockHistory.created_at < threshold
            ).delete()
            
            session.commit()
            logger.info(f"Deleted {result} old records")
            session.close()
            
        except Exception as e:
            logger.error(f"Error deleting old records: {str(e)}")
            if session:
                session.rollback()
                session.close()
