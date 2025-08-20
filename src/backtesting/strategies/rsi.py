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
        # Track if we have a position
        self.has_position = False
    
    def should_invest(self):
        """Invest when RSI is below threshold (oversold)"""
        return self.rsi[0] < self.params.rsi_threshold and not self.has_position
    
    def should_sell(self):
        """Sell when RSI is above sell threshold (overbought)"""
        return self.rsi[0] > self.params.rsi_sell_threshold and self.has_position
    
    def _execute_strategy(self):
        """Execute RSI strategy logic"""
        # Add cash periodically for new investments
        cash_added = self.add_cash_periodically(self.params.investment_amount, self.params.investment_freq)
        
        # Check sell signals first (to free up cash if needed)
        if self.should_sell():
            sold_amount = self.sell_position()
            if sold_amount > 0:
                self.has_position = False
                current_date = self._get_market_date()
                print(f"RSI above {self.params.rsi_sell_threshold}: Sold ${sold_amount:.2f} on {current_date}")
        
        # Invest when conditions are met
        if self.should_invest():
            # Use accumulated cash to buy
            if self.accumulated_cash > 0:
                # Calculate how many shares we can buy
                current_price = self.data.close[0]
                shares_to_buy = int(self.accumulated_cash / current_price)
                
                if shares_to_buy > 0:
                    # Buy the shares
                    self.buy(size=shares_to_buy)
                    invested_amount = shares_to_buy * current_price
                    self.accumulated_cash -= invested_amount
                    self.investment_count += 1
                    self.current_position += shares_to_buy
                    self.has_position = True
                    
                    current_date = self._get_market_date()
                    print(f"RSI below {self.params.rsi_threshold}: Bought {shares_to_buy} shares at ${current_price:.2f} = ${invested_amount:.2f} on {current_date}")
    
    def get_description(self):
        """Get strategy description for UI"""
        return {
            'name': 'RSI Strategy',
            'description': 'Buys when RSI is oversold (below threshold) and sells when overbought (above threshold)',
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
                    'description': 'RSI threshold for buying (lower = more aggressive)'
                },
                'rsi_sell_threshold': {
                    'type': 'float',
                    'default': 70.0,
                    'min': 60.0,
                    'max': 90.0,
                    'description': 'RSI threshold for selling (higher = more aggressive)'
                }
            }
        }
