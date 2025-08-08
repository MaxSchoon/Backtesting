"""
Investment Strategy Backtesting Framework

A comprehensive backtesting framework for testing various investment strategies
using historical market data.
"""

__version__ = "1.0.0"
__author__ = "Investment Backtesting Team"

from .core.engine import BacktestEngine
from .core.data_manager import DataManager

__all__ = ['BacktestEngine', 'DataManager']
