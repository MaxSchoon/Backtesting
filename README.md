# Momentum Backtest

This project implements a momentum-based backtesting strategy using the Relative Strength Index (RSI) for investing. The strategy is designed to accumulate cash at a user-defined interval and invest when the RSI falls below a specified threshold.

## Strategy Overview

The `RSIAccumulationStrategy` class defines the strategy, which operates as follows:
1. **Regular Cash Accumulation**: Adds a user-defined amount to the cash balance at the start of each investment period (monthly or quarterly).
2. **RSI-Based Investing**: Invests the accumulated cash when the RSI of the asset falls below a user-defined threshold.

## Key Components

### RSIAccumulationStrategy

- **Parameters**:
    - `rsi_period`: The period for calculating the RSI (default is 14).
    - `rsi_threshold`: The RSI threshold for making investments (default is 25).
    - `investment_amount`: The amount to add to the cash balance each period (default is $500).
    - `investment_freq`: The frequency of new investments, either 'monthly' or 'quarterly' (default is 'monthly').

- **Methods**:
    - `__init__`: Initializes the strategy, setting up the RSI indicator.
    - `start`: Placeholder for any initialization logic at the start of the strategy.
    - `next`: Executes the strategy logic on each new data point, including cash accumulation and investment based on RSI.
    - `stop`: Reports the final accumulated cash not invested.

### Data Fetching

- **get_yahoo_data(symbol, start_date, end_date)**: Fetches historical data for the specified symbol from Yahoo Finance, cleans it, and returns it in a format suitable for Backtrader.

### Main Function

- **run_strategy(...)**: Sets up the backtesting environment, adds the strategy and data, runs the backtest, and prints performance metrics including final portfolio value, net profit, maximum drawdown, and Sharpe ratio. It also plots the results.

## Usage

1. Ensure you have the required libraries installed:
     ```bash
     pip install yfinance backtrader pandas
     ```

2. Run the script with your desired parameters. For example:
     ```bash
     python momentum_backtest.py --symbol ^GSPC --start 2010-01-01 --end 2020-01-01 --initial-cash 20000 --investment-amount 1000 --investment-freq quarterly --rsi-period 10 --rsi-threshold 30
     ```

### Available Command-Line Arguments

- `--symbol`: Ticker symbol (default: ^GSPC)
- `--start`: Start date in YYYY-MM-DD format (default: 2000-01-01)
- `--end`: End date in YYYY-MM-DD format (default: 2023-01-01)
- `--initial-cash`: Initial cash to start with (default: 10000)
- `--investment-amount`: Amount to add to cash each period (default: 500)
- `--investment-freq`: Investment frequency, either 'weekly', 'monthly', 'quarterly', or 'yearly' (default: monthly)
- `--rsi-period`: RSI period (default: 14)
- `--rsi-threshold`: RSI threshold for investing (default: 25)

## Performance Metrics

The script provides the following performance metrics:
- **Final Portfolio Value**: The value of the portfolio at the end of the backtest.
- **Net Profit**: The profit made over the initial investment.
- **Maximum Drawdown**: The maximum observed loss from a peak to a trough.
- **Sharpe Ratio**: A measure of risk-adjusted return.
- **Trade Analysis**: Detailed analysis of trades made during the backtest.

## Plotting

The script plots the performance of the strategy using a candlestick chart.

## Example Output
```plaintext
Final Portfolio Value: $105,000
Net Profit: $5,000
Maximum Drawdown: 10%
Sharpe Ratio: 1.5
```
