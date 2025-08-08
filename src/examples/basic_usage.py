#!/usr/bin/env python3
"""
Example script demonstrating the Investment Strategy Backtester
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.backtesting.core.engine import BacktestEngine
from src.backtesting.core.data_manager import DataManager


def run_example_backtests():
    """Run example backtests to demonstrate the system"""
    
    print("🚀 Investment Strategy Backtester - Examples")
    print("=" * 60)
    
    # Initialize engine
    engine = BacktestEngine()
    
    # Example 1: RSI Strategy on S&P 500
    print("\n📊 Example 1: RSI Strategy on S&P 500")
    print("-" * 40)
    
    try:
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
        
        print(f"Final Value: ${metrics['final_value']:,.2f}")
        print(f"Total Return: {metrics['total_return_pct']:.2f}%")
        print(f"Max Drawdown: {metrics['max_drawdown_pct']:.2f}%")
        print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 2: Moving Average Strategy on Apple
    print("\n📊 Example 2: Moving Average Strategy on Apple")
    print("-" * 40)
    
    try:
        metrics = engine.run_backtest(
            symbol='AAPL',
            start_date='2020-01-01',
            end_date='2023-01-01',
            strategy_name='moving_average',
            initial_cash=10000,
            investment_amount=500,
            investment_freq='monthly',
            strategy_params={'fast_period': 10, 'slow_period': 30}
        )
        
        print(f"Final Value: ${metrics['final_value']:,.2f}")
        print(f"Total Return: {metrics['total_return_pct']:.2f}%")
        print(f"Max Drawdown: {metrics['max_drawdown_pct']:.2f}%")
        print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 3: Dollar Cost Averaging on SPY
    print("\n📊 Example 3: Dollar Cost Averaging on SPY")
    print("-" * 40)
    
    try:
        metrics = engine.run_backtest(
            symbol='SPY',
            start_date='2020-01-01',
            end_date='2023-01-01',
            strategy_name='dca',
            initial_cash=10000,
            investment_amount=500,
            investment_freq='monthly'
        )
        
        print(f"Final Value: ${metrics['final_value']:,.2f}")
        print(f"Total Return: {metrics['total_return_pct']:.2f}%")
        print(f"Max Drawdown: {metrics['max_drawdown_pct']:.2f}%")
        print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 4: Bollinger Bands Strategy on QQQ
    print("\n📊 Example 4: Bollinger Bands Strategy on QQQ")
    print("-" * 40)
    
    try:
        metrics = engine.run_backtest(
            symbol='QQQ',
            start_date='2020-01-01',
            end_date='2023-01-01',
            strategy_name='bollinger_bands',
            initial_cash=10000,
            investment_amount=500,
            investment_freq='monthly',
            strategy_params={'bb_period': 20, 'bb_dev': 2.0}
        )
        
        print(f"Final Value: ${metrics['final_value']:,.2f}")
        print(f"Total Return: {metrics['total_return_pct']:.2f}%")
        print(f"Max Drawdown: {metrics['max_drawdown_pct']:.2f}%")
        print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n✅ Examples completed!")
    print("\n💡 Try running the web interface with: streamlit run app.py")
    print("💡 Or use the CLI with: python cli.py --help")


def show_available_strategies():
    """Display available strategies"""
    
    print("\n📊 Available Strategies:")
    print("=" * 50)
    
    engine = BacktestEngine()
    strategies = engine.get_available_strategies()
    
    for key, strategy in strategies.items():
        print(f"\n🔹 {strategy['name']}")
        print(f"   Description: {strategy['description']}")
        if strategy['parameters']:
            print("   Parameters:")
            for param_name, param_config in strategy['parameters'].items():
                print(f"     - {param_name}: {param_config['description']}")


def show_popular_tickers():
    """Display popular ticker symbols"""
    
    print("\n📈 Popular Ticker Symbols:")
    print("=" * 50)
    
    engine = BacktestEngine()
    tickers = engine.get_popular_tickers()
    
    for symbol, description in tickers.items():
        print(f"  {symbol:<10} - {description}")


if __name__ == "__main__":
    # Show available strategies and tickers
    show_available_strategies()
    show_popular_tickers()
    
    # Run example backtests
    run_example_backtests()
