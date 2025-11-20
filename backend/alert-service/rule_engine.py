"""
Rule Engine Module
Evaluates stock data against user-defined alert rules
"""

import logging
from models import AlertRule

logger = logging.getLogger(__name__)


class RuleEngine:
    """Evaluates alert rules against stock data"""
    
    def __init__(self):
        logger.info("RuleEngine initialized")
    
    def evaluate_rules(self, stock_data):
        """
        Evaluate all active rules for a stock
        
        Args:
            stock_data (dict): Stock data to evaluate
            
        Returns:
            list: List of triggered rules
        """
        try:
            symbol = stock_data['symbol']
            price = stock_data['price']
            
            # Get all active rules for this symbol
            rules = AlertRule.query.filter_by(
                symbol=symbol,
                is_active=True
            ).all()
            
            triggered_rules = []
            
            for rule in rules:
                if self._evaluate_single_rule(rule, stock_data):
                    triggered_rules.append(rule.to_dict())
                    logger.info(f"Rule triggered: {rule.rule_type} for {symbol}")
            
            return triggered_rules
            
        except Exception as e:
            logger.error(f"Error evaluating rules: {str(e)}")
            return []
    
    def _evaluate_single_rule(self, rule, stock_data):
        """
        Evaluate a single rule
        
        Args:
            rule (AlertRule): Rule to evaluate
            stock_data (dict): Stock data
            
        Returns:
            bool: True if rule is triggered
        """
        price = stock_data['price']
        threshold = float(rule.threshold_value)
        
        if rule.rule_type == 'PRICE_ABOVE':
            return price > threshold
        
        elif rule.rule_type == 'PRICE_BELOW':
            return price < threshold
        
        elif rule.rule_type == 'SUDDEN_CHANGE':
            # Check if change percentage exceeds threshold
            change_percent = abs(stock_data.get('change_percent', 0))
            return change_percent > threshold
        
        return False
