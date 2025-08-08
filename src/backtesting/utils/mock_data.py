import pandas as pd
import numpy as np
import backtrader as bt
from datetime import datetime, timedelta


def generate_mock_data(symbol, start_date, end_date):
    """Generate mock data for testing when real data is not available"""
    
    # Convert dates to datetime
    start_dt = pd.to_datetime(start_date)
    end_dt = pd.to_datetime(end_date)
    
    # Generate date range
    date_range = pd.date_range(start=start_dt, end=end_dt, freq='D')
    
    # Generate mock price data
    np.random.seed(42)  # For reproducible results
    
    # Start with a base price
    base_price = 100.0
    
    # Generate price movements
    returns = np.random.normal(0.0005, 0.02, len(date_range))  # Daily returns
    prices = [base_price]
    
    for ret in returns[1:]:
        new_price = prices[-1] * (1 + ret)
        prices.append(max(new_price, 1.0))  # Ensure price doesn't go below 1
    
    # Create OHLC data
    data = pd.DataFrame({
        'Open': prices,
        'High': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
        'Low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
        'Close': prices,
        'Volume': np.random.randint(1000000, 10000000, len(date_range))
    }, index=date_range)
    
    # Ensure High >= Low and High >= Close >= Low
    data['High'] = data[['High', 'Close']].max(axis=1)
    data['Low'] = data[['Low', 'Close']].min(axis=1)
    
    # Convert to Backtrader format
    bt_data = bt.feeds.PandasData(dataname=data)
    
    return bt_data, data


def get_data_with_fallback(symbol, start_date, end_date):
    """Get data with fallback to mock data if real data fails"""
    try:
        from ..core.data_manager import DataManager
        return DataManager.fetch_data(symbol, start_date, end_date)
    except Exception as e:
        print(f"Warning: Could not fetch real data for {symbol}: {e}")
        print("Using mock data for demonstration...")
        return generate_mock_data(symbol, start_date, end_date)
