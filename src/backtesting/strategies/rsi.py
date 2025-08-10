import backtrader as bt
from .base import BaseStrategy


class RSIStrategy(BaseStrategy):
    """RSI-based investment strategy"""
    
    params = (
        ('rsi_period', 14),
        ('rsi_threshold', 25),
        ('rsi_sell_threshold', 70),
        ('investment_amount', 500),
        ('investment_freq', 'monthly'),
    )
    
    def setup_indicators(self):
        """Setup RSI indicator"""
        self.rsi = bt.indicators.RSI(self.data.close, period=self.params.rsi_period)
    
    def should_invest(self):
        """Invest when RSI is below threshold"""
        return self.rsi[0] < self.params.rsi_threshold
    
    def should_sell(self):
        """Sell when RSI is above sell threshold"""
        return self.rsi[0] > self.params.rsi_sell_threshold
    
    def _execute_strategy(self):
        """Execute RSI strategy logic"""
        # Add cash periodically
        cash_added = self.add_cash_periodically(self.params.investment_amount, self.params.investment_freq)
        
        # Check sell signals first
        if self.should_sell():
            sold_amount = self.sell_position()
            if sold_amount > 0:
                current_date = self.data.datetime.date(0)
                print(f"RSI above {self.params.rsi_sell_threshold}: Sold ${sold_amount:.2f} on {current_date}")
        
        # Invest when conditions are met
        if self.should_invest():
            invested_amount = self.invest_accumulated_cash()
            if invested_amount > 0:
                current_date = self.data.datetime.date(0)
                print(f"RSI below {self.params.rsi_threshold}: Invested ${invested_amount:.2f} on {current_date}")
    
    def get_description(self):
        """Get strategy description for UI"""
        return {
            'name': 'RSI Strategy',
            'description': 'Invests when RSI falls below a threshold, indicating oversold conditions',
            'parameters': {
                'rsi_period': {
                    'type': 'int',
                    'default': 14,
                    'min': 5,
                    'max': 50,
                    'description': 'Period for RSI calculation'
                },
                'rsi_threshold': {
                    'type': 'float',
                    'default': 25.0,
                    'min': 10.0,
                    'max': 40.0,
                    'description': 'RSI threshold for investing (lower = more aggressive)'
                }
            }
        }
