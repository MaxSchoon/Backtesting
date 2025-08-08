import backtrader as bt
from .base import BaseStrategy


class BollingerBandsStrategy(BaseStrategy):
    """Bollinger Bands investment strategy"""
    
    params = (
        ('bb_period', 20),
        ('bb_dev', 2.0),
        ('investment_amount', 500),
        ('investment_freq', 'monthly'),
    )
    
    def setup_indicators(self):
        """Setup Bollinger Bands indicators"""
        self.bb = bt.indicators.BollingerBands(
            self.data.close, 
            period=self.params.bb_period, 
            devfactor=self.params.bb_dev
        )
    
    def should_invest(self):
        """Invest when price touches or goes below lower band (oversold)"""
        return self.data.close[0] <= self.bb.lines.bot[0]
    
    def _execute_strategy(self):
        """Execute Bollinger Bands strategy logic"""
        # Add cash periodically
        cash_added = self.add_cash_periodically(self.params.investment_amount, self.params.investment_freq)
        
        # Invest when conditions are met
        if self.should_invest():
            invested_amount = self.invest_accumulated_cash()
            if invested_amount > 0:
                current_date = self.data.datetime.date(0)
                print(f"Bollinger Bands: Invested ${invested_amount:.2f} on {current_date}")
    
    def get_description(self):
        """Get strategy description for UI"""
        return {
            'name': 'Bollinger Bands Strategy',
            'description': 'Invests when price touches the lower Bollinger Band (oversold condition)',
            'parameters': {
                'bb_period': {
                    'type': 'int',
                    'default': 20,
                    'min': 10,
                    'max': 50,
                    'description': 'Period for Bollinger Bands calculation'
                },
                'bb_dev': {
                    'type': 'float',
                    'default': 2.0,
                    'min': 1.5,
                    'max': 3.0,
                    'description': 'Standard deviation multiplier for bands'
                }
            }
        }
