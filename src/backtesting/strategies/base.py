import backtrader as bt
from abc import abstractmethod


class BaseStrategy(bt.Strategy):
    """Base class for all investment strategies"""
    
    def __init__(self):
        self.total_invested = 0
        self.accumulated_cash = 0
        self.last_period = None
        self.portfolio_values = []
        self.dates = []
        self.investment_count = 0
        self.sell_count = 0
        self.current_position = 0  # Current number of shares held
        self.setup_indicators()
    
    @abstractmethod
    def setup_indicators(self):
        """Setup technical indicators for the strategy"""
        pass
    
    @abstractmethod
    def should_invest(self):
        """Determine if we should invest based on strategy logic"""
        pass
    
    @abstractmethod
    def should_sell(self):
        """Determine if we should sell based on strategy logic"""
        pass
    
    def add_cash_periodically(self, investment_amount, investment_freq):
        """Add cash to the account based on frequency"""
        current_date = self.data.datetime.date(0)
        
        if investment_freq == 'weekly':
            period_marker = (current_date.year, current_date.isocalendar()[1])
        elif investment_freq == 'monthly':
            period_marker = (current_date.year, current_date.month)
        elif investment_freq == 'quarterly':
            period_marker = (current_date.year, (current_date.month - 1) // 3)
        elif investment_freq == 'yearly':
            period_marker = (current_date.year,)
        else:
            period_marker = (current_date.year, current_date.month)
        
        if self.last_period is None or period_marker != self.last_period:
            self.broker.add_cash(investment_amount)
            self.accumulated_cash += investment_amount
            self.total_invested += investment_amount
            self.last_period = period_marker
            return True
        return False
    
    def invest_accumulated_cash(self):
        """Invest all accumulated cash"""
        if self.accumulated_cash > 0:
            size = int(self.accumulated_cash / self.data.close[0])
            if size > 0:
                self.buy(size=size)
                invested_amount = size * self.data.close[0]
                self.accumulated_cash -= invested_amount
                self.investment_count += 1
                self.current_position += size
                current_date = self.data.datetime.date(0)
                print(f"BUY: {size} shares at ${self.data.close[0]:.2f} = ${invested_amount:.2f} on {current_date}")
                return invested_amount
        return 0
    
    def sell_position(self, portion=1.0):
        """Sell a portion or all of the current position"""
        if self.current_position > 0:
            shares_to_sell = int(self.current_position * portion)
            if shares_to_sell > 0:
                self.sell(size=shares_to_sell)
                sold_amount = shares_to_sell * self.data.close[0]
                self.current_position -= shares_to_sell
                self.sell_count += 1
                current_date = self.data.datetime.date(0)
                print(f"SELL: {shares_to_sell} shares at ${self.data.close[0]:.2f} = ${sold_amount:.2f} on {current_date}")
                return sold_amount
        return 0
    
    def next(self):
        """Track portfolio value over time"""
        # Record portfolio value
        current_date = self.data.datetime.date(0)
        portfolio_value = self.broker.getvalue()
        
        self.portfolio_values.append(portfolio_value)
        self.dates.append(current_date)
        
        # Call the main strategy logic
        self._execute_strategy()
    
    def _execute_strategy(self):
        """Execute the main strategy logic - to be overridden by subclasses"""
        # Add cash periodically
        self.add_cash_periodically(self.params.investment_amount, self.params.investment_freq)
        
        # Check sell signals first (to free up cash if needed)
        if self.should_sell():
            self.sell_position()
        
        # Invest when conditions are met
        if self.should_invest():
            self.invest_accumulated_cash()
    
    def stop(self):
        """Called at the end of the strategy"""
        print(f"Total amount invested: ${self.total_invested:.2f}")
        print(f"Final accumulated cash not invested: ${self.accumulated_cash:.2f}")
        print(f"Final position: {self.current_position} shares")
        print(f"Total buy transactions: {self.investment_count}")
        print(f"Total sell transactions: {self.sell_count}")
