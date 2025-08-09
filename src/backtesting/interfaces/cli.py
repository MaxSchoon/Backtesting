#!/usr/bin/env python3
"""
Command-line interface for the Investment Strategy Backtester
"""

import argparse
import sys
import os
from typing import Any

# Optional HTTP cache for yfinance requests
try:  # noqa: SIM105
    import requests_cache  # type: ignore[import-not-found]
except Exception:  # pragma: no cover
    requests_cache = None  # type: Any

# Add the src directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, '..', '..')
sys.path.insert(0, src_dir)

from backtesting.core.engine import BacktestEngine
from backtesting.core.data_manager import DataManager


def main():
    # Enable HTTP caching to avoid repeating identical Yahoo Finance requests
    if requests_cache is not None:
        try:
            requests_cache.install_cache(
                cache_name='yfinance_cache',
                backend='sqlite',
                expire_after=3600,
            )
        except Exception:
            pass

    parser = argparse.ArgumentParser(
        description='Investment Strategy Backtester - CLI Version',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run RSI strategy on S&P 500
  python cli.py --strategy rsi --symbol ^GSPC --start 2020-01-01 --end 2023-01-01

  # Run Moving Average strategy with custom parameters
  python cli.py --strategy moving_average --symbol AAPL --fast-period 5 --slow-period 20

  # Run Dollar Cost Averaging
  python cli.py --strategy dca --symbol SPY --investment-amount 1000 --investment-freq monthly

  # List available strategies
  python cli.py --list-strategies

  # List popular tickers
  python cli.py --list-tickers
        """
    )
    
    # Strategy selection
    parser.add_argument(
        '--strategy', '-s',
        choices=['rsi', 'moving_average', 'bollinger_bands', 'dca'],
        help='Strategy to use for backtesting'
    )
    
    # Asset selection
    parser.add_argument(
        '--symbol', '-t',
        help='Ticker symbol (e.g., ^GSPC, AAPL, SPY)'
    )
    
    # Date range
    parser.add_argument(
        '--start', '-sd',
        help='Start date (YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--end', '-ed',
        help='End date (YYYY-MM-DD)'
    )
    
    # Investment settings
    parser.add_argument(
        '--initial-cash', '-ic',
        type=float,
        default=10000,
        help='Initial cash amount (default: 10000)'
    )
    
    parser.add_argument(
        '--investment-amount', '-ia',
        type=float,
        default=500,
        help='Amount to invest each period (default: 500)'
    )
    
    parser.add_argument(
        '--investment-freq', '-if',
        choices=['weekly', 'monthly', 'quarterly', 'yearly'],
        default='monthly',
        help='Investment frequency (default: monthly)'
    )
    
    # Strategy-specific parameters
    parser.add_argument(
        '--rsi-period', '-rp',
        type=int,
        default=14,
        help='RSI period (default: 14)'
    )
    
    parser.add_argument(
        '--rsi-threshold', '-rt',
        type=float,
        default=25.0,
        help='RSI threshold for investing (default: 25.0)'
    )
    
    parser.add_argument(
        '--fast-period', '-fp',
        type=int,
        default=10,
        help='Fast moving average period (default: 10)'
    )
    
    parser.add_argument(
        '--slow-period', '-sp',
        type=int,
        default=30,
        help='Slow moving average period (default: 30)'
    )
    
    parser.add_argument(
        '--bb-period', '-bp',
        type=int,
        default=20,
        help='Bollinger Bands period (default: 20)'
    )
    
    parser.add_argument(
        '--bb-dev', '-bd',
        type=float,
        default=2.0,
        help='Bollinger Bands standard deviation (default: 2.0)'
    )
    
    # Output options
    parser.add_argument(
        '--plot', '-p',
        action='store_true',
        help='Show performance plot'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    # Information commands
    parser.add_argument(
        '--list-strategies',
        action='store_true',
        help='List available strategies'
    )
    
    parser.add_argument(
        '--list-tickers',
        action='store_true',
        help='List popular ticker symbols'
    )
    
    parser.add_argument(
        '--clear-cache',
        action='store_true',
        help='Clear all cached data'
    )
    
    parser.add_argument(
        '--cache-info',
        action='store_true',
        help='Show cache information'
    )
    
    args = parser.parse_args()
    
    # Initialize engine
    engine = BacktestEngine()
    
    # Handle information commands
    if args.list_strategies:
        print("📊 Available Strategies:")
        print("=" * 50)
        strategies = engine.get_available_strategies()
        for key, strategy in strategies.items():
            print(f"\n🔹 {strategy['name']}")
            print(f"   Description: {strategy['description']}")
            if strategy['parameters']:
                print("   Parameters:")
                for param_name, param_config in strategy['parameters'].items():
                    print(f"     - {param_name}: {param_config['description']}")
        return
    
    if args.list_tickers:
        print("📈 Popular Ticker Symbols:")
        print("=" * 50)
        tickers = engine.get_popular_tickers()
        for symbol, description in tickers.items():
            print(f"  {symbol:<10} - {description}")
        return
    
    if args.clear_cache:
        DataManager.clear_cache()
        return
    
    if args.cache_info:
        print("📦 Cache Information:")
        print("=" * 50)
        print(DataManager.get_cache_info())
        return
    
    # Validate required arguments
    if not args.strategy:
        parser.error("--strategy is required")
    
    if not args.symbol:
        parser.error("--symbol is required")
    
    # Set default dates if not provided
    if not args.start or not args.end:
        default_start, default_end = DataManager.get_default_date_range()
        if not args.start:
            args.start = default_start
        if not args.end:
            args.end = default_end
    
    # Prepare strategy parameters
    strategy_params = {}
    if args.strategy == 'rsi':
        strategy_params = {
            'rsi_period': args.rsi_period,
            'rsi_threshold': args.rsi_threshold
        }
    elif args.strategy == 'moving_average':
        strategy_params = {
            'fast_period': args.fast_period,
            'slow_period': args.slow_period
        }
    elif args.strategy == 'bollinger_bands':
        strategy_params = {
            'bb_period': args.bb_period,
            'bb_dev': args.bb_dev
        }
    
    # Run backtest
    try:
        print(f"🚀 Running {args.strategy.upper()} strategy on {args.symbol}")
        print(f"📅 Period: {args.start} to {args.end}")
        print(f"💰 Initial Cash: ${args.initial_cash:,.2f}")
        print(f"💵 Investment Amount: ${args.investment_amount:,.2f} ({args.investment_freq})")
        print("-" * 60)
        
        metrics = engine.run_backtest(
            symbol=args.symbol,
            start_date=args.start,
            end_date=args.end,
            strategy_name=args.strategy,
            initial_cash=args.initial_cash,
            investment_amount=args.investment_amount,
            investment_freq=args.investment_freq,
            strategy_params=strategy_params
        )
        
        # Display results
        print("\n📊 BACKTEST RESULTS")
        print("=" * 60)
        print(f"Final Portfolio Value: ${metrics['final_value']:,.2f}")
        print(f"Total Invested:        ${metrics['total_invested']:,.2f}")
        print(f"Net Profit:            ${metrics['net_profit']:+,.2f}")
        print(f"Total Return:          {metrics['total_return_pct']:.2f}%")
        print(f"Annual Return:         {metrics['annual_return_pct']:.2f}%")
        print(f"Maximum Drawdown:      {metrics['max_drawdown_pct']:.2f}%")
        print(f"Sharpe Ratio:          {metrics['sharpe_ratio']:.2f}")
        print(f"Total Trades:          {metrics['total_trades']}")
        print(f"Win Rate:              {metrics['win_rate_pct']:.1f}%")
        
        # Show plot if requested
        if args.plot:
            print("\n📈 Generating performance chart...")
            try:
                engine.plot_results()
                print("✅ Chart displayed in browser window")
            except Exception as e:
                print(f"❌ Error generating chart: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
