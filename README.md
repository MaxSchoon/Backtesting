# Investment Strategy Backtester

A comprehensive backtesting framework for testing various investment strategies using historical market data.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Launch the web interface
python3 scripts/launch_app.py

# Or run the CLI version
python3 src/backtesting/interfaces/cli.py --help
```

## 📁 Project Structure

```
backtesting/
├── src/backtesting/           # Main package
│   ├── core/                  # Core backtesting components
│   │   ├── engine.py         # Main backtesting engine
│   │   └── data_manager.py   # Data fetching and management
│   ├── strategies/            # Investment strategies
│   │   ├── base.py           # Base strategy class
│   │   ├── rsi.py            # RSI strategy
│   │   ├── moving_average.py # Moving average strategy
│   │   ├── bollinger_bands.py # Bollinger bands strategy
│   │   ├── dollar_cost_averaging.py # DCA strategy
│   │   └── factory.py        # Strategy factory
│   ├── utils/                 # Utility functions
│   │   └── mock_data.py      # Mock data generation
│   └── interfaces/            # User interfaces
│       ├── web_app.py        # Streamlit web interface
│       └── cli.py            # Command-line interface
├── src/examples/              # Example usage
│   └── basic_usage.py        # Basic usage examples
├── tests/                     # Test suite
├── docs/                      # Documentation
├── scripts/                   # Utility scripts
│   └── launch_app.py         # App launcher
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```

## 🎯 Features

- **Multiple Strategies**: RSI, Moving Average, Bollinger Bands, Dollar Cost Averaging
- **Web Interface**: User-friendly Streamlit app for beginners
- **CLI Interface**: Command-line interface for power users
- **Comprehensive Analytics**: Performance metrics, risk analysis, and strategy comparisons
- **Real Data**: Yahoo Finance integration with fallback to mock data
- **Modular Design**: Easy to extend with new strategies

## 📊 Available Strategies

1. **RSI Strategy**: Invests when RSI falls below threshold (oversold conditions)
2. **Moving Average Crossover**: Invests when fast MA crosses above slow MA
3. **Bollinger Bands**: Invests when price touches lower band
4. **Dollar Cost Averaging**: Simple periodic investment strategy

## 🛠️ Installation

```bash
git clone <repository-url>
cd backtesting
pip install -r requirements.txt
```

## 📖 Usage

### Web Interface (Recommended for Beginners)

```bash
python3 scripts/launch_app.py
```

### Command Line Interface

```bash
# List available strategies
python3 src/backtesting/interfaces/cli.py --list-strategies

# Run RSI strategy
python3 src/backtesting/interfaces/cli.py --strategy rsi --symbol AAPL --start 2020-01-01 --end 2023-01-01

# Run with custom parameters
python3 src/backtesting/interfaces/cli.py --strategy moving_average --symbol SPY --fast-period 5 --slow-period 20
```

### Programmatic Usage

```python
from src.backtesting.core.engine import BacktestEngine

engine = BacktestEngine()
metrics = engine.run_backtest(
    symbol='AAPL',
    start_date='2020-01-01',
    end_date='2023-01-01',
    strategy_name='rsi',
    initial_cash=10000,
    investment_amount=500
)
```

## 📈 Performance Metrics

- **Final Portfolio Value**: Total value at end of period
- **Total Return**: Percentage gain/loss
- **Max Drawdown**: Largest peak-to-trough decline
- **Sharpe Ratio**: Risk-adjusted return measure
- **Win Rate**: Percentage of profitable trades
- **Annual Return**: Annualized return rate

## 🔧 Development

### Adding New Strategies

1. Create a new strategy class inheriting from `BaseStrategy`
2. Implement `setup_indicators()` and `should_invest()` methods
3. Add to the strategy factory
4. Update the web interface and CLI

### Running Tests

```bash
python3 -m pytest tests/
```

## 📚 Documentation

- [Quick Start Guide](docs/QUICK_START.md)
- [API Documentation](docs/README.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Built with [Backtrader](https://www.backtrader.com/)
- Data from [Yahoo Finance](https://finance.yahoo.com/)
- Web interface powered by [Streamlit](https://streamlit.io/)
