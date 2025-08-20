import backtrader as bt
from abc import abstractmethod
import pandas as pd
from datetime import datetime, date


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
    
    def _get_market_date(self):
        """Get the current market date, handling different market timezones"""
        try:
            # Get the current datetime from the data feed
            current_datetime = self.data.datetime.datetime(0)
            
            # If it's a datetime object, convert to date
            if isinstance(current_datetime, datetime):
                return current_datetime.date()
            elif isinstance(current_datetime, date):
                return current_datetime
            else:
                # Fallback: try to get date directly
                return self.data.datetime.date(0)
        except Exception as e:
            print(f"Warning: Could not get market date: {e}")
            # Fallback to simple date extraction
            return self.data.datetime.date(0)
    
    def _is_market_open(self, current_date):
        """Check if the market is open on the given date"""
        try:
            # Ensure we have a datetime object
            if isinstance(current_date, str):
                current_date = pd.to_datetime(current_date)
            
            # Convert to pandas datetime for easier manipulation
            pd_date = pd.to_datetime(current_date)
            
            # Check if it's a weekend (Saturday = 5, Sunday = 6)
            if pd_date.weekday() >= 5:
                return False
            
            # Check for major US market holidays (simplified)
            # In a production system, you'd want a proper holiday calendar
            month = pd_date.month
            day = pd_date.day
            
            # New Year's Day (January 1)
            if month == 1 and day == 1:
                return False
            
            # Independence Day (July 4)
            if month == 7 and day == 4:
                return False
            
            # Christmas Day (December 25)
            if month == 12 and day == 25:
                return False
            
            # Thanksgiving (4th Thursday in November)
            if month == 11 and pd_date.weekday() == 3:
                # Check if it's the 4th Thursday
                week_of_month = (day - 1) // 7 + 1
                if week_of_month == 4:
                    return False
            
            return True
            
        except Exception as e:
            print(f"Warning: Could not determine market status: {e}")
            return True  # Assume open if we can't determine
    
    def add_cash_periodically(self, investment_amount, investment_freq):
        """Add cash to the account based on frequency"""
        current_date = self._get_market_date()
        
        # Only add cash on market open days
        if not self._is_market_open(current_date):
            return False
        
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
                current_date = self._get_market_date()
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
                current_date = self._get_market_date()
                print(f"SELL: {shares_to_sell} shares at ${self.data.close[0]:.2f} = ${sold_amount:.2f} on {current_date}")
                return sold_amount
        return 0
    
    def next(self):
        """Track portfolio value over time"""
        # Record portfolio value
        current_date = self._get_market_date()
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
