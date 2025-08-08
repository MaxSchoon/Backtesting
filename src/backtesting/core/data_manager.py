import yfinance as yf
import backtrader as bt
import pandas as pd
import os
import pickle
from datetime import datetime, timedelta


class DataManager:
    """Manages data fetching and preprocessing"""
    
    # Cache directory
    CACHE_DIR = "cache"
    
    # Popular ticker symbols with descriptions
    POPULAR_TICKERS = {
        '^GSPC': 'S&P 500 Index',
        '^DJI': 'Dow Jones Industrial Average',
        '^IXIC': 'NASDAQ Composite',
        '^RUT': 'Russell 2000 Index',
        'SPY': 'SPDR S&P 500 ETF',
        'QQQ': 'Invesco QQQ Trust',
        'IWM': 'iShares Russell 2000 ETF',
        'VTI': 'Vanguard Total Stock Market ETF',
        'VOO': 'Vanguard S&P 500 ETF',
        'AAPL': 'Apple Inc.',
        'MSFT': 'Microsoft Corporation',
        'GOOGL': 'Alphabet Inc.',
        'AMZN': 'Amazon.com Inc.',
        'TSLA': 'Tesla Inc.',
        'NVDA': 'NVIDIA Corporation',
        'META': 'Meta Platforms Inc.',
        'BRK-B': 'Berkshire Hathaway Inc.',
        'JNJ': 'Johnson & Johnson',
        'JPM': 'JPMorgan Chase & Co.',
        'V': 'Visa Inc.',
    }
    
    @staticmethod
    def get_popular_tickers():
        """Get list of popular tickers with descriptions"""
        return DataManager.POPULAR_TICKERS
    
    @staticmethod
    def _get_cache_key(symbol, start_date, end_date):
        """Generate cache key for data"""
        return f"{symbol}_{start_date}_{end_date}.pkl"
    
    @staticmethod
    def _get_cache_path(symbol, start_date, end_date):
        """Get cache file path"""
        if not os.path.exists(DataManager.CACHE_DIR):
            os.makedirs(DataManager.CACHE_DIR)
        cache_key = DataManager._get_cache_key(symbol, start_date, end_date)
        return os.path.join(DataManager.CACHE_DIR, cache_key)
    
    @staticmethod
    def _load_from_cache(symbol, start_date, end_date):
        """Load data from cache if available"""
        cache_path = DataManager._get_cache_path(symbol, start_date, end_date)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    cached_data = pickle.load(f)
                print(f"📦 Loaded cached data for {symbol}")
                return cached_data
            except Exception as e:
                print(f"⚠️  Cache corrupted for {symbol}, fetching fresh data: {e}")
        return None
    
    @staticmethod
    def _save_to_cache(symbol, start_date, end_date, data):
        """Save data to cache"""
        cache_path = DataManager._get_cache_path(symbol, start_date, end_date)
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
            print(f"💾 Cached data for {symbol}")
        except Exception as e:
            print(f"⚠️  Failed to cache data for {symbol}: {e}")
    
    @staticmethod
    def fetch_data(symbol, start_date, end_date):
        """Fetch data from Yahoo Finance and prepare for backtesting"""
        try:
            # Try to load from cache first
            cached_data = DataManager._load_from_cache(symbol, start_date, end_date)
            if cached_data is not None:
                return cached_data
            
            # Download data from Yahoo Finance
            print(f"🌐 Fetching data for {symbol} from Yahoo Finance...")
            data = yf.download(
                symbol,
                interval="1d",
                start=start_date,
                end=end_date,
                auto_adjust=False,
                group_by="column",
            )
            
            # Check if data is empty
            if data.empty:
                raise ValueError(f"No data found for {symbol} between {start_date} and {end_date}")
            
            # Clean data
            data.dropna(inplace=True)
            data = data[data["Close"] > 0]
            
            # Check if we have enough data after cleaning
            if len(data) < 10:
                raise ValueError(f"Insufficient data for {symbol} after cleaning. Only {len(data)} data points available.")
            
            # Flatten MultiIndex columns if present
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            
            # Convert to Backtrader format
            bt_data = bt.feeds.PandasData(dataname=data)
            
            # Cache the data
            DataManager._save_to_cache(symbol, start_date, end_date, (bt_data, data))
            
            return bt_data, data
            
        except Exception as e:
            error_msg = str(e)
            if "Rate limited" in error_msg or "Too Many Requests" in error_msg:
                raise ValueError(f"Rate limit error for {symbol}: Yahoo Finance API is temporarily limiting requests. Please try again later or use a different ticker.")
            else:
                raise ValueError(f"Error fetching data for {symbol}: {error_msg}")
    
    @staticmethod
    def validate_date_range(start_date, end_date):
        """Validate the date range"""
        try:
            start = pd.to_datetime(start_date)
            end = pd.to_datetime(end_date)
            
            if start >= end:
                raise ValueError("Start date must be before end date")
            
            if start < pd.to_datetime('1990-01-01'):
                raise ValueError("Start date cannot be before 1990")
            
            if end > datetime.now():
                raise ValueError("End date cannot be in the future")
            
            return True
            
        except Exception as e:
            raise ValueError(f"Invalid date range: {str(e)}")
    
    @staticmethod
    def get_default_date_range():
        """Get a sensible default date range"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=5*365)  # 5 years
        return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
    
    @staticmethod
    def clear_cache():
        """Clear all cached data"""
        if os.path.exists(DataManager.CACHE_DIR):
            import shutil
            shutil.rmtree(DataManager.CACHE_DIR)
            print(f"🗑️  Cleared cache directory: {DataManager.CACHE_DIR}")
        else:
            print("ℹ️  No cache directory found to clear")
    
    @staticmethod
    def get_cache_info():
        """Get information about cached data"""
        if not os.path.exists(DataManager.CACHE_DIR):
            return "No cache directory found"
        
        cache_files = os.listdir(DataManager.CACHE_DIR)
        total_files = len(cache_files)
        total_size = sum(os.path.getsize(os.path.join(DataManager.CACHE_DIR, f)) for f in cache_files)
        
        return f"Cache contains {total_files} files ({total_size / 1024:.1f} KB)"
