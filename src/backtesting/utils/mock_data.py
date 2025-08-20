import pandas as pd
import numpy as np
import backtrader as bt
from datetime import datetime, timedelta


def _standardize_mock_dates(start_date, end_date):
    """Standardize dates for mock data generation"""
    try:
        # Convert to pandas datetime
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
        
        # Ensure dates are timezone-naive for consistent handling
        if start_dt.tz is not None:
            start_dt = start_dt.tz_localize(None)
        if end_dt.tz is not None:
            end_dt = end_dt.tz_localize(None)
        
        # Generate business days only (excludes weekends)
        date_range = pd.bdate_range(start=start_dt, end=end_dt, freq='D')
        
        return start_dt, end_dt, date_range
        
    except Exception as e:
        print(f"Warning: Could not standardize mock dates: {e}")
        # Fallback to simple date range
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
        date_range = pd.date_range(start=start_dt, end=end_dt, freq='D')
        return start_dt, end_dt, date_range


def generate_mock_data(symbol, start_date, end_date):
    """Generate mock data for testing when real data is not available"""
    
    # Standardize dates
    start_dt, end_dt, date_range = _standardize_mock_dates(start_date, end_date)
    
    # Generate mock price data
    np.random.seed(42)  # For reproducible results
    
    # Start with a base price (varies by symbol type)
    if symbol.startswith('^'):  # Index
        base_price = 1000.0
    elif symbol in ['SPY', 'QQQ', 'IWM', 'VTI', 'VOO']:  # ETFs
        base_price = 100.0
    else:  # Individual stocks
        base_price = 50.0
    
    # Generate price movements with realistic volatility
    if symbol.startswith('^'):  # Indices are less volatile
        daily_volatility = 0.015
    elif symbol in ['SPY', 'QQQ', 'IWM', 'VTI', 'VOO']:  # ETFs
        daily_volatility = 0.02
    else:  # Individual stocks
        daily_volatility = 0.025
    
    returns = np.random.normal(0.0005, daily_volatility, len(date_range))  # Daily returns
    prices = [base_price]
    
    for ret in returns[1:]:
        new_price = prices[-1] * (1 + ret)
        # Ensure price doesn't go below reasonable minimum
        min_price = base_price * 0.1  # 10% of base price
        prices.append(max(new_price, min_price))
    
    # Create OHLC data with realistic spreads
    data = pd.DataFrame({
        'Open': prices,
        'High': [p * (1 + abs(np.random.normal(0, 0.008))) for p in prices],
        'Low': [p * (1 - abs(np.random.normal(0, 0.008))) for p in prices],
        'Close': prices,
        'Volume': np.random.randint(1000000, 10000000, len(date_range))
    }, index=date_range)
    
    # Ensure High >= Low and High >= Close >= Low
    data['High'] = data[['High', 'Close']].max(axis=1)
    data['Low'] = data[['Low', 'Close']].min(axis=1)
    
    # Ensure Open is between High and Low
    data['Open'] = data['Open'].clip(lower=data['Low'], upper=data['High'])
    
    # Clean and standardize the data
    data = _clean_mock_data(data)
    
    # Convert to Backtrader format
    bt_data = bt.feeds.PandasData(dataname=data)
    
    return bt_data, data


def _clean_mock_data(data):
    """Clean and standardize mock data"""
    # Remove any timezone info from the index
    if data.index.tz is not None:
        data.index = data.index.tz_localize(None)
    
    # Ensure the index is datetime type
    if not isinstance(data.index, pd.DatetimeIndex):
        data.index = pd.to_datetime(data.index)
    
    # Remove any NaN values
    data.dropna(inplace=True)
    
    # Ensure all prices are positive
    data = data[data["Close"] > 0]
    
    # Ensure all required columns exist
    required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    for col in required_columns:
        if col not in data.columns:
            if col == 'Volume':
                data[col] = 1000000  # Default volume
            else:
                data[col] = data['Close']  # Use close price for missing OHLC
    
    # Sort by date to ensure chronological order
    data.sort_index(inplace=True)
    
    return data


def get_data_with_fallback(symbol, start_date, end_date):
    """Get data with fallback to mock data if real data fails"""
    try:
        from ..core.data_manager import DataManager
        return DataManager.fetch_data(symbol, start_date, end_date)
    except Exception as e:
        print(f"Warning: Could not fetch real data for {symbol}: {e}")
        print("Using mock data for demonstration...")
        return generate_mock_data(symbol, start_date, end_date)
