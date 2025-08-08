import backtrader as bt
from .base import BaseStrategy


class MovingAverageStrategy(BaseStrategy):
    """Moving Average Crossover investment strategy"""
    
    params = (
        ('fast_period', 10),
        ('slow_period', 30),
        ('investment_amount', 500),
        ('investment_freq', 'monthly'),
    )
    
    def setup_indicators(self):
        """Setup moving average indicators"""
        self.fast_ma = bt.indicators.SMA(self.data.close, period=self.params.fast_period)
        self.slow_ma = bt.indicators.SMA(self.data.close, period=self.params.slow_period)
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)
    
    def should_invest(self):
        """Invest when fast MA crosses above slow MA (bullish signal)"""
        return self.crossover > 0  # Fast MA crosses above slow MA
    
    def _execute_strategy(self):
        """Execute Moving Average strategy logic"""
        # Add cash periodically
        cash_added = self.add_cash_periodically(self.params.investment_amount, self.params.investment_freq)
        
        # Invest when conditions are met
        if self.should_invest():
            invested_amount = self.invest_accumulated_cash()
            if invested_amount > 0:
                current_date = self.data.datetime.date(0)
                print(f"MA Crossover: Invested ${invested_amount:.2f} on {current_date}")
    
    def get_description(self):
        """Get strategy description for UI"""
        return {
            'name': 'Moving Average Crossover',
            'description': 'Invests when fast moving average crosses above slow moving average',
            'parameters': {
                'fast_period': {
                    'type': 'int',
                    'default': 10,
                    'min': 5,
                    'max': 50,
                    'description': 'Fast moving average period'
                },
                'slow_period': {
                    'type': 'int',
                    'default': 30,
                    'min': 15,
                    'max': 100,
                    'description': 'Slow moving average period'
                }
            }
        }
