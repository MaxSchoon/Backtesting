# 🚀 Quick Start Guide

## Getting Started with the Investment Strategy Backtester

### Option 1: Web Interface (Recommended for Beginners)

1. **Navigate to the Backtesting directory**:
   ```bash
   cd Backtesting
   ```

2. **Install dependencies** (if not already installed):
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the web interface**:
   ```bash
   streamlit run app.py
   ```

4. **Open your browser** and go to `http://localhost:8501`

5. **Start backtesting**:
   - Choose a strategy from the sidebar
   - Select an asset (stock/ETF)
   - Configure parameters
   - Click "Run Backtest"

### Option 2: Command Line Interface (For Advanced Users)

1. **List available strategies**:
   ```bash
   python3 cli.py --list-strategies
   ```

2. **Run a backtest**:
   ```bash
   python3 cli.py --strategy rsi --symbol ^GSPC --start 2020-01-01 --end 2023-01-01
   ```

3. **Get help**:
   ```bash
   python3 cli.py --help
   ```

### Option 3: Examples

Run the example script to see the system in action:
```bash
python3 -m Backtesting.example
```

## 🎯 Available Strategies

### 1. RSI Strategy
- **Best for**: Value investing, contrarian approaches
- **Logic**: Invests when RSI is oversold (below threshold)
- **Parameters**: RSI period, RSI threshold

### 2. Moving Average Crossover
- **Best for**: Trend following, momentum strategies
- **Logic**: Invests when fast MA crosses above slow MA
- **Parameters**: Fast period, slow period

### 3. Bollinger Bands Strategy
- **Best for**: Mean reversion, volatility-based strategies
- **Logic**: Invests when price touches lower band
- **Parameters**: BB period, standard deviation

### 4. Dollar Cost Averaging
- **Best for**: Baseline comparison, conservative investing
- **Logic**: Invests fixed amounts at regular intervals
- **Parameters**: None (uses investment settings)

## 📊 Popular Assets

The system includes pre-configured popular assets:
- **^GSPC**: S&P 500 Index
- **SPY**: SPDR S&P 500 ETF
- **QQQ**: Invesco QQQ Trust
- **AAPL**: Apple Inc.
- **MSFT**: Microsoft Corporation
- **And many more...**

## 💡 Tips for Beginners

1. **Start with DCA**: Use Dollar Cost Averaging as a baseline
2. **Use longer periods**: 5+ years for more reliable results
3. **Compare strategies**: Test different approaches on the same asset
4. **Focus on metrics**: Pay attention to Sharpe ratio and maximum drawdown
5. **Experiment**: Try different parameters to see their impact

## 🔧 Troubleshooting

### Common Issues

1. **Import errors**: Make sure you're in the Backtesting directory
2. **Missing dependencies**: Run `pip install -r requirements.txt`
3. **Data errors**: Some tickers may have limited historical data
4. **Rate limits**: Yahoo Finance may limit requests during high traffic

### Getting Help

- Check the main README.md for detailed documentation
- Look at example.py for usage examples
- Use the CLI help: `python3 cli.py --help`

## 🎉 Success!

Once you see the web interface running, you can:
- ✅ Choose from 4 different investment strategies
- ✅ Test on 20+ popular stocks and ETFs
- ✅ Compare strategy performance
- ✅ Analyze comprehensive metrics
- ✅ Learn about different investment approaches

Happy backtesting! 📈
