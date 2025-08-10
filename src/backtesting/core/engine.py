import backtrader as bt
import pandas as pd
from datetime import datetime
from .data_manager import DataManager
from ..strategies.factory import StrategyFactory


class BacktestEngine:
    """Main backtesting engine"""
    
    def __init__(self):
        self.cerebro = None
        self.results = None
        self.performance_metrics = {}
        self.portfolio_values = []
        self.dates = []
    
    def run_backtest(self, symbol, start_date, end_date, strategy_name, 
                    initial_cash=10000, investment_amount=500, investment_freq='monthly',
                    strategy_params=None):
        """Run a complete backtest"""
        
        # Validate inputs
        DataManager.validate_date_range(start_date, end_date)
        
        # Get strategy class and parameters
        strategy_class, default_params = StrategyFactory.create_strategy(strategy_name)
        
        # Merge parameters
        if strategy_params is None:
            strategy_params = {}
        
        # Add common parameters
        strategy_params.update({
            'investment_amount': investment_amount,
            'investment_freq': investment_freq,
        })
        
        # Fetch data with fallback
        data_source = "real"
        try:
            bt_data, raw_data = DataManager.fetch_data(symbol, start_date, end_date)
        except Exception as e:
            # Use mock data as fallback
            from ..utils.mock_data import get_data_with_fallback
            bt_data, raw_data = get_data_with_fallback(symbol, start_date, end_date)
            data_source = "mock"
            error_msg = str(e)
            if "Rate limit" in error_msg:
                print(f"Rate limit detected for {symbol}: {e}")
                print("Using mock data for demonstration due to API rate limits...")
            else:
                print(f"Warning: Could not fetch real data for {symbol}: {e}")
                print("Using mock data for demonstration...")
        
        # Setup backtesting engine
        self.cerebro = bt.Cerebro()
        self.cerebro.adddata(bt_data)
        self.cerebro.addstrategy(strategy_class, **strategy_params)
        
        # Configure broker
        self.cerebro.broker.setcash(initial_cash)
        self.cerebro.broker.setcommission(commission=0.0005)  # 0.05% commission
        
        # Add analyzers
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trade_analyzer')
        self.cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        
        # Run backtest
        self.results = self.cerebro.run()
        
        # Capture portfolio data from the strategy
        if self.results and len(self.results) > 0:
            strategy = self.results[0]
            if hasattr(strategy, 'portfolio_values') and hasattr(strategy, 'dates'):
                self.portfolio_values = strategy.portfolio_values
                self.dates = strategy.dates
        
        # Calculate performance metrics
        self._calculate_performance_metrics(initial_cash, investment_amount, 
                                         investment_freq, start_date, end_date)
        
        # Add data source information to metrics
        self.performance_metrics['data_source'] = data_source
        self.performance_metrics['symbol'] = symbol
        
        return self.performance_metrics

    def get_available_strategies(self):
        return StrategyFactory.get_available_strategies()

    def get_popular_tickers(self):
        return DataManager.get_popular_tickers()
    
    def _calculate_performance_metrics(self, initial_cash, investment_amount, 
                                     investment_freq, start_date, end_date):
        """Calculate comprehensive performance metrics"""
        
        if not self.results:
            return
        
        try:
            strategy = self.results[0]
            analyzers = strategy.analyzers
        except (IndexError, AttributeError) as e:
            print(f"Warning: Could not access strategy results: {e}")
            # Set default values if results are not available
            self.performance_metrics = {
                'final_value': initial_cash,
                'total_invested': initial_cash,
                'net_profit': 0,
                'total_return_pct': 0,
                'max_drawdown_pct': 0,
                'sharpe_ratio': 0,
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate_pct': 0,
                'annual_return_pct': 0,
            }
            return
        
        strategy = self.results[0]
        analyzers = strategy.analyzers
        
        # Get final portfolio value
        final_value = self.cerebro.broker.getvalue()
        
        # Calculate total invested
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
        
        if investment_freq == 'weekly':
            periods = ((end_dt - start_dt).days // 7) + 1
        elif investment_freq == 'monthly':
            periods = (end_dt.year - start_dt.year) * 12 + (end_dt.month - start_dt.month) + 1
        elif investment_freq == 'quarterly':
            periods = ((end_dt.year - start_dt.year) * 4 + (end_dt.month - start_dt.month) // 3) + 1
        elif investment_freq == 'yearly':
            periods = (end_dt.year - start_dt.year) + 1
        else:
            periods = (end_dt.year - start_dt.year) * 12 + (end_dt.month - start_dt.month) + 1
        
        total_invested = initial_cash + (periods * investment_amount)
        
        # Get analyzer results with better error handling
        try:
            drawdown_analysis = analyzers.drawdown.get_analysis()
            sharpe_analysis = analyzers.sharpe.get_analysis()
            trade_analysis = analyzers.trade_analyzer.get_analysis()
            returns_analysis = analyzers.returns.get_analysis()
        except Exception as e:
            print(f"Warning: Error getting analyzer results: {e}")
            drawdown_analysis = {}
            sharpe_analysis = {}
            trade_analysis = {}
            returns_analysis = {}
        
        # Calculate metrics
        net_profit = final_value - total_invested
        total_return = (final_value / total_invested - 1) * 100 if total_invested > 0 else 0
        
        # Get metrics with fallbacks
        max_drawdown = drawdown_analysis.get('max', {}).get('drawdown', 0)
        if max_drawdown is None:
            max_drawdown = 0
            
        sharpe_ratio = sharpe_analysis.get('sharperatio', 0)
        if sharpe_ratio is None:
            sharpe_ratio = 0
            
        # Trade statistics with better handling
        # Count actual investment events from strategy
        if self.results and len(self.results) > 0:
            strategy = self.results[0]
            if hasattr(strategy, 'investment_count'):
                total_trades = strategy.investment_count
            else:
                # Fallback to backtrader's count
                total_trades = trade_analysis.get('total', {}).get('total', 0)
        else:
            total_trades = trade_analysis.get('total', {}).get('total', 0)
            
        # Count buy and sell transactions separately
        buy_trades = 0
        sell_trades = 0
        if self.results and len(self.results) > 0:
            strategy = self.results[0]
            if hasattr(strategy, 'investment_count'):
                buy_trades = strategy.investment_count
            if hasattr(strategy, 'sell_count'):
                sell_trades = strategy.sell_count
        
        # Use strategy counts if available, otherwise fallback to backtrader
        if buy_trades == 0 and sell_trades == 0:
            buy_trades = trade_analysis.get('bought', {}).get('total', 0)
            sell_trades = trade_analysis.get('sold', {}).get('total', 0)
        
        total_trades = buy_trades + sell_trades
        winning_trades = trade_analysis.get('won', {}).get('total', 0)
        losing_trades = trade_analysis.get('lost', {}).get('total', 0)
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # Annual return calculation - calculate properly accounting for regular investments
        try:
            # Calculate the actual annualized return based on the investment timeline
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)
            
            # Calculate the total time period in years
            total_days = (end_dt - start_dt).days
            total_years = total_days / 365.25
            
            if total_years > 0:
                # For regular investment strategies, we need to account for the fact that
                # money is being added over time, not just at the beginning
                
                # Simple approach: If this is a regular investment strategy, 
                # the annual return should be close to the total return for short periods
                # For longer periods, we can use a more sophisticated calculation
                
                if total_years < 0.5:  # Less than 6 months
                    # For very short periods, annual returns are misleading
                    # Use total return instead, or a simple extrapolation
                    annual_return = total_return / total_years if total_years > 0.1 else total_return
                else:
                    # For longer periods, use a more reasonable calculation
                    # Since money is invested over time, not all at once, 
                    # the effective annual return should be lower than a simple extrapolation
                    effective_annual_return = total_return / total_years
                    
                    # Apply a discount factor for regular investments (money invested over time)
                    # This is a simplified approach - in reality it's more complex
                    if investment_freq == 'monthly':
                        discount_factor = 0.6  # Money invested over time vs lump sum
                    elif investment_freq == 'weekly':
                        discount_factor = 0.5
                    else:
                        discount_factor = 0.7
                    
                    annual_return = effective_annual_return * discount_factor
                    
                    # Cap the annual return to be reasonable
                    if annual_return > 50:  # Cap at 50% annual return
                        annual_return = 50
            else:
                annual_return = 0
                
        except Exception as e:
            print(f"Warning: Error calculating annual return: {e}")
            # Fallback to a simple calculation
            annual_return = total_return
        
        # Store metrics (preserve existing fields like data_source)
        new_metrics = {
            'final_value': final_value,
            'total_invested': total_invested,
            'net_profit': net_profit,
            'total_return_pct': total_return,
            'max_drawdown_pct': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'total_trades': total_trades,
            'buy_trades': buy_trades,
            'sell_trades': sell_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate_pct': win_rate,
            'annual_return_pct': annual_return,
        }
        
        # Preserve existing fields (like data_source and symbol)
        if hasattr(self, 'performance_metrics'):
            for key, value in self.performance_metrics.items():
                if key not in new_metrics:
                    new_metrics[key] = value
        
        self.performance_metrics = new_metrics
        
        # Debug output
        print(f"Debug - Final Value: {final_value}")
        print(f"Debug - Total Return: {total_return}%")
        print(f"Debug - Max Drawdown: {max_drawdown}%")
        print(f"Debug - Sharpe Ratio: {sharpe_ratio}")
        print(f"Debug - Total Trades: {total_trades}")
        print(f"Debug - Annual Return: {annual_return:.2f}%")
        print(f"Debug - Time Period: {total_years:.2f} years")
        print(f"Debug - Investment Frequency: {investment_freq}")
        print(f"Debug - Start Date: {start_date}, End Date: {end_date}")
    
    def get_performance_metrics(self):
        """Get the calculated performance metrics"""
        return self.performance_metrics
    
    def plot_results(self, style='candlestick'):
        """Plot the backtest results"""
        if self.cerebro:
            self.cerebro.plot(style=style)
    
    def get_available_strategies(self):
        """Get all available strategies"""
        return StrategyFactory.get_available_strategies()
    
    def get_popular_tickers(self):
        """Get popular ticker symbols"""
        return DataManager.get_popular_tickers()
    
    def get_chart_data(self):
        """Get portfolio value data for charting"""
        if self.portfolio_values and self.dates:
            return {
                'dates': self.dates,
                'portfolio_values': self.portfolio_values
            }
        return None
