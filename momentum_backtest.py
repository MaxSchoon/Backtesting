import yfinance as yf
import backtrader as bt
import pandas as pd
import argparse


class RSIAccumulationStrategy(bt.Strategy):
    params = (
        ('rsi_period', 14),    # RSI period
        ('rsi_threshold', 25),  # RSI threshold for investing
        ('investment_amount', 500),  # Amount to invest each period
        ('investment_freq', 'monthly'),  # Frequency: weekly, monthly, quarterly, yearly
    )

    def __init__(self):
        self.last_period = None
        self.total_invested = 0
        self.accumulated_cash = 0
        self.rsi = bt.indicators.RSI(self.data.close, period=self.params.rsi_period)

    def start(self):
        pass

    def next(self):
        # Determine if it's time to add new cash based on frequency
        current_date = self.data.datetime.date(0)
        if self.params.investment_freq == 'weekly':
            period_marker = (current_date.year, current_date.isocalendar()[1])  # ISO week number
        elif self.params.investment_freq == 'monthly':
            period_marker = (current_date.year, current_date.month)
        elif self.params.investment_freq == 'quarterly':
            period_marker = (current_date.year, (current_date.month - 1) // 3)
        elif self.params.investment_freq == 'yearly':
            period_marker = (current_date.year,)
        else:
            period_marker = (current_date.year, current_date.month)  # Default to monthly

        if self.last_period is None:
            self.last_period = period_marker
            self.broker.add_cash(self.params.investment_amount)
            self.accumulated_cash += self.params.investment_amount
            self.total_invested += self.params.investment_amount
            print(f"Added ${self.params.investment_amount} to cash balance on {current_date}")
        elif period_marker != self.last_period:
            self.broker.add_cash(self.params.investment_amount)
            self.accumulated_cash += self.params.investment_amount
            self.total_invested += self.params.investment_amount
            print(f"Added ${self.params.investment_amount} to cash balance on {current_date}")
            self.last_period = period_marker

        # Invest accumulated cash when RSI is below threshold
        if self.rsi[0] < self.params.rsi_threshold and self.accumulated_cash > 0:
            size = int(self.accumulated_cash / self.data.close[0])
            if size > 0:
                self.buy(size=size)
                invested_amount = size * self.data.close[0]
                self.accumulated_cash -= invested_amount
                print(f"RSI below {self.params.rsi_threshold}: Invested ${invested_amount:.2f} on {current_date}")
            else:
                print(f"Not enough cash to buy shares on {current_date}")

    def stop(self):
        print(f"Total amount invested: ${self.total_invested:.2f}")
        print(f"Final accumulated cash not invested: ${self.accumulated_cash:.2f}")

# Function to fetch data
def get_yahoo_data(symbol, start_date, end_date):
    """Fetch data from Yahoo Finance and sanitize column names."""
    data = yf.download(
        symbol,
        interval="1d",
        start=start_date,
        end=end_date,
        auto_adjust=False,
        group_by="column",
    )
    data.dropna(inplace=True)  # Remove rows with NaN values
    data = data[data["Close"] > 0]  # Remove rows with zero prices

    # If yfinance returns a MultiIndex, flatten to single level
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    return bt.feeds.PandasData(dataname=data)

# Main function to run the strategy
def run_strategy(
    symbol,
    start_date,
    end_date,
    initial_cash,
    investment_amount,
    investment_freq,
    rsi_period,
    rsi_threshold
):
    data = get_yahoo_data(symbol, start_date, end_date)
    cerebro = bt.Cerebro()
    cerebro.adddata(data)
    cerebro.addstrategy(
        RSIAccumulationStrategy,
        rsi_period=rsi_period,
        rsi_threshold=rsi_threshold,
        investment_amount=investment_amount,
        investment_freq=investment_freq,
    )
    cerebro.broker.setcash(initial_cash)
    cerebro.broker.setcommission(commission=0.0005)
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trade_analyzer')

    print("\nRunning RSI Accumulation Strategy...")
    results = cerebro.run()
    final_value = cerebro.broker.getvalue()
    analyzers = results[0].analyzers
    print("\n=== RSI Accumulation Strategy Performance ===")
    print(f"Final Portfolio Value: ${final_value:.2f}")
    # Calculate the total amount invested over the period
    total_months = (data.datetime.date(-1).year - data.datetime.date(0).year) * 12 + (data.datetime.date(-1).month - data.datetime.date(0).month)
    if investment_freq == 'weekly':
        total_days = (data.datetime.date(-1) - data.datetime.date(0)).days
        periods = (total_days // 7) + 1
    elif investment_freq == 'monthly':
        periods = total_months + 1
    elif investment_freq == 'quarterly':
        periods = ((total_months + 1) // 3)
    elif investment_freq == 'yearly':
        periods = (data.datetime.date(-1).year - data.datetime.date(0).year) + 1
    else:
        periods = total_months + 1
    total_invested = initial_cash + (periods * investment_amount)
    print(f"Net Profit: ${final_value - total_invested:.2f}")
    print(f"Maximum Drawdown: {analyzers.drawdown.get_analysis()['max']['drawdown']:.2f}%")
    print(f"Sharpe Ratio: {analyzers.sharpe.get_analysis().get('sharperatio', 0):.2f}")
    print(f"Trade Analysis: {analyzers.trade_analyzer.get_analysis()}")
    print("\nPlotting RSI Accumulation Strategy...")
    cerebro.plot(style='candlestick')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='RSI Accumulation Backtest')
    parser.add_argument('--symbol', type=str, default='^GSPC', help='Ticker symbol (default: ^GSPC)')
    parser.add_argument('--start', type=str, default='2000-01-01', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, default='2023-01-01', help='End date (YYYY-MM-DD)')
    parser.add_argument('--initial-cash', type=float, default=10000, help='Initial cash (default: 10000)')
    parser.add_argument('--investment-amount', type=float, default=500, help='Amount to invest each period (default: 500)')
    parser.add_argument('--investment-freq', type=str, choices=['weekly', 'monthly', 'quarterly', 'yearly'], default='monthly', help='Investment frequency (weekly, monthly, quarterly, or yearly)')
    parser.add_argument('--rsi-period', type=int, default=14, help='RSI period (default: 14)')
    parser.add_argument('--rsi-threshold', type=float, default=25, help='RSI threshold for investing (default: 25)')
    args = parser.parse_args()
    run_strategy(
        symbol=args.symbol,
        start_date=args.start,
        end_date=args.end,
        initial_cash=args.initial_cash,
        investment_amount=args.investment_amount,
        investment_freq=args.investment_freq,
        rsi_period=args.rsi_period,
        rsi_threshold=args.rsi_threshold,
    )
