import yfinance as yf
import backtrader as bt

from datetime import timedelta

# Define the Benchmark Strategy with RSI-Based Investing


from datetime import timedelta

# Define the Benchmark Strategy with RSI-Based Investing

# Define the RSI Accumulation Strategy with RSI-Based Investing


class RSIAccumulationStrategy(bt.Strategy):
    params = (
        ('rsi_period', 14),    # RSI period
        ('rsi_threshold', 25),  # RSI threshold for investing (changed to 25)
    )

    def __init__(self):
        self.last_month = None
        self.total_invested = 0
        self.accumulated_cash = 0  # Initialize accumulated_cash
        self.rsi = bt.indicators.RSI(self.data.close, period=self.params.rsi_period)

    def start(self):
        # No initial investment at t0
        pass

    def next(self):
        # Add $500 each month to accumulated cash
        current_month = self.data.datetime.date(0).month
        if self.last_month is None:
            self.last_month = current_month
            self.broker.add_cash(500)
            self.accumulated_cash += 500
            self.total_invested += 500
            print(f"Added $500 to cash balance on {self.data.datetime.date(0)}")
        elif current_month != self.last_month:
            # New month has started
            self.broker.add_cash(500)
            self.accumulated_cash += 500



            self.total_invested += 500


            print(f"Added $500 to cash balance on {self.data.datetime.date(0)}")
            self.last_month = current_month

        # Invest accumulated cash when RSI is below threshold (25)
        if self.rsi[0] < self.params.rsi_threshold and self.accumulated_cash > 0:

            cash = self.broker.get_cash()
            size = int(cash / self.data.close[0])
            if size > 0:
                self.buy(size=size)
                invested_amount = size * self.data.close[0]
                self.accumulated_cash = cash - invested_amount  # Update accumulated cash
                print(f"RSI below {self.params.rsi_threshold}: Invested ${invested_amount:.2f} on {self.data.datetime.date(0)}")


            size = int(self.accumulated_cash / self.data.close[0])
            if size > 0:
                self.buy(size=size)
                invested_amount = size * self.data.close[0]
                self.accumulated_cash -= invested_amount  # Update accumulated cash
                print(
                    f"RSI below {self.params.rsi_threshold}: Invested ${invested_amount:.2f} on {self.data.datetime.date(0)}"
                )


            else:
                print(f"Not enough cash to buy shares on {self.data.datetime.date(0)}")

    def stop(self):
        print(f"Total amount invested: ${self.total_invested:.2f}")
        print(f"Final accumulated cash not invested: ${self.accumulated_cash:.2f}")

# Function to fetch data
def get_yahoo_data(symbol, start_date, end_date):
    data = yf.download(symbol, interval='1d', start=start_date, end=end_date)
    data.dropna(inplace=True)  # Remove rows with NaN values
    data = data[data['Close'] > 0]  # Remove rows with zero prices
    return bt.feeds.PandasData(dataname=data)

# Main function to run the strategy
def run_strategy():
    # Fetch data
    data = get_yahoo_data('^GSPC', '2000-01-01', '2023-01-01')

    # Set up Cerebro for the benchmark strategy
    cerebro = bt.Cerebro()
    cerebro.adddata(data)
    cerebro.addstrategy(RSIAccumulationStrategy)
    cerebro.broker.setcash(10000)
    cerebro.broker.setcommission(commission=0.0005)
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trade_analyzer')

    # Run strategy
    print("\nRunning RSI Accumulation Strategy...")
    results = cerebro.run()

    # Get final portfolio value
    final_value = cerebro.broker.getvalue()

    # Extract analyzers
    analyzers = results[0].analyzers

    # Print performance metrics
    print("\n=== RSI Accumulation Strategy Performance ===")
    print(f"Final Portfolio Value: ${final_value:.2f}")
    # Calculate the total amount invested over the period
    total_months = (data.datetime.date(-1).year - data.datetime.date(0).year) * 12 + (data.datetime.date(-1).month - data.datetime.date(0).month)
    total_invested = 10000 + ((total_months + 1) * 500)  # Include the initial month

    print(f"Net Profit: ${final_value - total_invested:.2f}")
    print(f"Maximum Drawdown: {analyzers.drawdown.get_analysis()['max']['drawdown']:.2f}%")
    print(f"Sharpe Ratio: {analyzers.sharpe.get_analysis().get('sharperatio', 0):.2f}")
    print(f"Trade Analysis: {analyzers.trade_analyzer.get_analysis()}")

    # Plot results
    print("\nPlotting RSI Accumulation Strategy...")
    cerebro.plot(style='candlestick')

# Run the strategy
if __name__ == '__main__':
    run_strategy()
