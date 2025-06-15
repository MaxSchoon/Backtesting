import importlib.util
import os

import backtrader as bt
import pandas as pd

# Helper function to compute RSI similarly to the strategy

def compute_rsi(series, period=2):
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    roll_up = up.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    roll_down = down.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    rs = roll_up / roll_down
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Import strategy from project root
import sys
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT_DIR)
from momentum_backtest import RSIAccumulationStrategy

class RecordBuyStrategy(RSIAccumulationStrategy):
    """Subclass that records buy dates for assertions."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.buy_dates = []

    def notify_order(self, order):
        if order.status == order.Completed and order.isbuy():
            self.buy_dates.append(self.data.datetime.date(0))
        return super().notify_order(order)

def test_rsi_strategy_behavior():
    # Create predictable price data across three months
    prices = [10, 9, 8, 7, 6, 7, 8, 9, 10, 11] * 7  # 70 days
    index = pd.date_range("2020-01-01", periods=len(prices), freq="D")

    df = pd.DataFrame({
        "Open": prices,
        "High": [p + 1 for p in prices],
        "Low": [p - 1 for p in prices],
        "Close": prices,
        "Volume": [1000] * len(prices),
    }, index=index)

    # Precompute RSI values to know when it falls below threshold
    rsi_series = compute_rsi(df["Close"], period=2)
    first_low_rsi_ts = rsi_series[rsi_series < 25].index[0]
    expected_buy_date = (first_low_rsi_ts + pd.Timedelta(days=1)).date()

    cerebro = bt.Cerebro()
    cerebro.adddata(bt.feeds.PandasData(dataname=df))
    cerebro.addstrategy(RecordBuyStrategy, rsi_period=2, rsi_threshold=25)
    cerebro.broker.setcash(10000)

    results = cerebro.run()
    strat = results[0]

    # Three months of data -> $1500 accumulated and invested
    assert strat.total_invested == 1500

    # Verify a buy happened when RSI dropped below threshold (next bar execution)
    assert expected_buy_date in strat.buy_dates

