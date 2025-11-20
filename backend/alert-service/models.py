"""
Database Models for Alert Service
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Alert(db.Model):
    """Alert model for storing triggered alerts"""
    
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    symbol = db.Column(db.String(10), nullable=False)
    alert_type = db.Column(db.String(20), nullable=False)
    threshold = db.Column(db.Numeric(10, 2))
    triggered_at = db.Column(db.DateTime, default=datetime.utcnow)
    message = db.Column(db.Text)
    is_read = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'symbol': self.symbol,
            'alert_type': self.alert_type,
            'threshold': float(self.threshold) if self.threshold else None,
            'triggered_at': self.triggered_at.isoformat(),
            'message': self.message,
            'is_read': self.is_read
        }


class AlertRule(db.Model):
    """Alert rule model for user-defined alert conditions"""
    
    __tablename__ = 'alert_rules'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    symbol = db.Column(db.String(10), nullable=False)
    rule_type = db.Column(db.String(20), nullable=False)  # PRICE_ABOVE, PRICE_BELOW, SUDDEN_CHANGE
    threshold_value = db.Column(db.Numeric(10, 2), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'symbol': self.symbol,
            'rule_type': self.rule_type,
            'threshold_value': float(self.threshold_value),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }
