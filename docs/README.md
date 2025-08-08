# 📈 Investment Strategy Backtester

A comprehensive, modular backtesting system with a beautiful web interface for testing different investment strategies using historical market data.

## 🚀 Features

- **Multiple Investment Strategies**: RSI, Moving Average Crossover, Bollinger Bands, and Dollar Cost Averaging
- **Beautiful Web Interface**: User-friendly Streamlit app with interactive controls
- **Comprehensive Analytics**: Performance metrics, risk analysis, and strategy comparisons
- **Popular Assets**: Pre-configured list of popular stocks and ETFs
- **Modular Architecture**: Easy to add new strategies and extend functionality

## 🏗️ Architecture

```
Backtesting/
├── app.py                    # Main Streamlit web application
├── backtest_engine.py        # Core backtesting engine
├── data_manager.py          # Data fetching and management
├── strategies/              # Strategy implementations
│   ├── __init__.py
│   ├── base_strategy.py     # Base strategy class
│   ├── rsi_strategy.py      # RSI-based strategy
│   ├── moving_average_strategy.py
│   ├── bollinger_bands_strategy.py
│   ├── dollar_cost_averaging_strategy.py
│   └── strategy_factory.py  # Strategy factory
├── requirements.txt
└── README.md
```

## 📊 Available Strategies

### 1. RSI Strategy
- **Description**: Invests when RSI falls below a threshold (oversold conditions)
- **Parameters**: RSI period, RSI threshold
- **Best for**: Value investing, contrarian approaches

### 2. Moving Average Crossover
- **Description**: Invests when fast MA crosses above slow MA (bullish signal)
- **Parameters**: Fast period, slow period
- **Best for**: Trend following, momentum strategies

### 3. Bollinger Bands Strategy
- **Description**: Invests when price touches lower band (oversold)
- **Parameters**: BB period, standard deviation multiplier
- **Best for**: Mean reversion, volatility-based strategies

### 4. Dollar Cost Averaging
- **Description**: Simple strategy investing fixed amounts at regular intervals
- **Parameters**: None (uses investment settings)
- **Best for**: Baseline comparison, conservative investing

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Backtesting
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the web application**:
   ```bash
   streamlit run app.py
   ```

4. **Open your browser** and navigate to `http://localhost:8501`

## 🎯 Usage

### Web Interface

1. **Choose a Strategy**: Select from the dropdown in the sidebar
2. **Configure Parameters**: Adjust strategy-specific settings using the sliders
3. **Select Asset**: Pick from popular stocks/ETFs or enter a custom ticker
4. **Set Investment Plan**: Define initial cash and regular investment amounts
5. **Choose Date Range**: Select the historical period to test
6. **Run Backtest**: Click "Run Backtest" to see results

### Programmatic Usage

```python
from backtest_engine import BacktestEngine

# Initialize engine
engine = BacktestEngine()

# Run backtest
metrics = engine.run_backtest(
    symbol='^GSPC',
    start_date='2020-01-01',
    end_date='2023-01-01',
    strategy_name='rsi',
    initial_cash=10000,
    investment_amount=500,
    investment_freq='monthly',
    strategy_params={'rsi_period': 14, 'rsi_threshold': 25}
)

# View results
print(f"Final Value: ${metrics['final_value']:,.2f}")
print(f"Total Return: {metrics['total_return_pct']:.2f}%")
```

## 📈 Performance Metrics

The system provides comprehensive performance analysis:

- **Final Portfolio Value**: Total value at end of backtest
- **Total Return**: Percentage gain/loss over the period
- **Annual Return**: Annualized return rate
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Sharpe Ratio**: Risk-adjusted return measure
- **Trade Statistics**: Number of trades, win rate, etc.

## 🔧 Adding New Strategies

To add a new strategy:

1. **Create a new strategy file** in `strategies/`:
   ```python
   from .base_strategy import BaseStrategy
   import backtrader as bt
   
   class MyStrategy(BaseStrategy):
       params = (
           ('my_param', 10),
           ('investment_amount', 500),
           ('investment_freq', 'monthly'),
       )
       
       def setup_indicators(self):
           # Setup your indicators
           pass
       
       def should_invest(self):
           # Define your investment logic
           return True
       
       def get_description(self):
           return {
               'name': 'My Strategy',
               'description': 'Description of my strategy',
               'parameters': {
                   'my_param': {
                       'type': 'int',
                       'default': 10,
                       'min': 5,
                       'max': 20,
                       'description': 'My parameter description'
                   }
               }
           }
   ```

2. **Register the strategy** in `strategy_factory.py`:
   ```python
   from .my_strategy import MyStrategy
   
   strategies = {
       'my_strategy': MyStrategy,
       # ... other strategies
   }
   ```

## 🎨 Customization

### Adding New Assets
Edit `data_manager.py` to add more popular tickers:
```python
POPULAR_TICKERS = {
    'YOUR_TICKER': 'Your Description',
    # ... existing tickers
}
```

### Modifying Investment Frequencies
The system supports weekly, monthly, quarterly, and yearly investment frequencies. Modify the `add_cash_periodically` method in `base_strategy.py` to add new frequencies.

### Custom Performance Metrics
Extend the `_calculate_performance_metrics` method in `backtest_engine.py` to add custom metrics.

## 🚨 Important Notes

- **Historical Data**: Uses Yahoo Finance for data. Some tickers may have limited historical data.
- **Commission**: Default 0.05% commission is applied to all trades.
- **Data Quality**: System automatically filters out invalid data points.
- **Performance**: Backtests are simulations and past performance doesn't guarantee future results.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your strategy or improvements
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Built with [Backtrader](https://www.backtrader.com/) for backtesting
- Data provided by [Yahoo Finance](https://finance.yahoo.com/)
- Web interface powered by [Streamlit](https://streamlit.io/)
- Charts created with [Plotly](https://plotly.com/)
