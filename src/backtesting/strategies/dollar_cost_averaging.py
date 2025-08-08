import backtrader as bt
from .base import BaseStrategy


class DollarCostAveragingStrategy(BaseStrategy):
    """Simple Dollar Cost Averaging strategy"""
    
    params = (
        ('investment_amount', 500),
        ('investment_freq', 'monthly'),
    )
    
    def setup_indicators(self):
        """No indicators needed for DCA"""
        pass
    
    def should_invest(self):
        """Always invest in DCA strategy"""
        return True
    
    def _execute_strategy(self):
        """Execute DCA strategy logic"""
        # Add cash periodically
        cash_added = self.add_cash_periodically(self.params.investment_amount, self.params.investment_freq)
        
        # Always invest the accumulated cash
        if cash_added or self.accumulated_cash > 0:
            invested_amount = self.invest_accumulated_cash()
            if invested_amount > 0:
                current_date = self.data.datetime.date(0)
                print(f"DCA: Invested ${invested_amount:.2f} on {current_date}")
    
    def get_description(self):
        """Get strategy description for UI"""
        return {
            'name': 'Dollar Cost Averaging',
            'description': 'Simple strategy that invests a fixed amount at regular intervals regardless of market conditions',
            'parameters': {}
        }
