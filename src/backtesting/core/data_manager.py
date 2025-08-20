import yfinance as yf
import backtrader as bt
import pandas as pd
import os
import pickle
from datetime import datetime, timedelta
import time
import random
import pytz


class DataManager:
    """Manages data fetching and preprocessing"""
    
    # Cache directory
    CACHE_DIR = "cache"
    # In-memory cooldown store for symbols that recently hit rate limits
    _RATE_LIMIT_COOLDOWN_SECONDS = 600  # Increased to 10 minutes
    _symbol_last_rate_limit_ts = {}
    
    # Market timezone mappings for proper date handling
    MARKET_TIMEZONES = {
        # US Markets (Eastern Time)
        '^GSPC': 'America/New_York', '^DJI': 'America/New_York', '^IXIC': 'America/New_York',
        '^RUT': 'America/New_York', 'SPY': 'America/New_York', 'QQQ': 'America/New_York',
        'IWM': 'America/New_York', 'VTI': 'America/New_York', 'VOO': 'America/New_York',
        'AAPL': 'America/New_York', 'MSFT': 'America/New_York', 'GOOGL': 'America/New_York',
        'AMZN': 'America/New_York', 'TSLA': 'America/New_York', 'NVDA': 'America/New_York',
        'META': 'America/New_York', 'BRK-B': 'America/New_York', 'JNJ': 'America/New_York',
        'JPM': 'America/New_York', 'V': 'America/New_York',
        
        # European Markets (Central European Time)
        '^STOXX50E': 'Europe/Berlin', '^GDAXI': 'Europe/Berlin', '^FCHI': 'Europe/Paris',
        '^FTSE': 'Europe/London', '^N225': 'Asia/Tokyo', '^HSI': 'Asia/Hong_Kong',
        '^BSESN': 'Asia/Kolkata', '^AXJO': 'Australia/Sydney',
        
        # Default to US timezone for unknown symbols
        'DEFAULT': 'America/New_York'
    }
    
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
    def _get_market_timezone(symbol):
        """Get the appropriate timezone for a given symbol"""
        return DataManager.MARKET_TIMEZONES.get(symbol, DataManager.MARKET_TIMEZONES['DEFAULT'])
    
    @staticmethod
    def _standardize_dates(self, start_date, end_date, symbol):
        """Standardize dates to the appropriate market timezone"""
        try:
            # Convert to pandas datetime
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)
            
            # Get market timezone
            market_tz = self._get_market_timezone(symbol)
            market_tz_obj = pytz.timezone(market_tz)
            
            # Localize dates to market timezone if they don't have timezone info
            if start_dt.tz is None:
                start_dt = market_tz_obj.localize(start_dt)
            if end_dt.tz is None:
                end_dt = market_tz_obj.localize(end_dt)
            
            # Convert to UTC for consistent handling
            start_dt_utc = start_dt.tz_convert('UTC')
            end_dt_utc = end_dt.tz_convert('UTC')
            
            # Ensure end date is end of day in market timezone
            end_dt_utc = end_dt_utc.replace(hour=23, minute=59, second=59)
            
            return start_dt_utc, end_dt_utc
            
        except Exception as e:
            print(f"Warning: Could not standardize dates for {symbol}: {e}")
            # Fallback to simple conversion
            return pd.to_datetime(start_date), pd.to_datetime(end_date)
    
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
    def _smart_retry_delay(attempt, base_delay=2.0, max_delay=60.0):
        """Calculate smart retry delay with exponential backoff and jitter"""
        # Exponential backoff: 2^attempt * base_delay
        delay = min(base_delay * (2 ** attempt), max_delay)
        
        # Add jitter (±25% random variation) to prevent thundering herd
        jitter = delay * 0.25 * random.uniform(-1, 1)
        delay += jitter
        
        # Ensure minimum delay
        return max(delay, 1.0)
    
    @staticmethod
    def _is_rate_limit_error(error_msg):
        """Check if error is a rate limit error"""
        rate_limit_indicators = [
            "rate limit", "rate-limited", "too many requests", "429",
            "max retries", "quota exceeded", "throttled", "throttling"
        ]
        return any(indicator in error_msg.lower() for indicator in rate_limit_indicators)
    
    @staticmethod
    def _enhanced_rate_limit_handling(symbol, attempt, max_attempts, base_delay):
        """Enhanced rate limit handling with better backoff strategies"""
        if attempt < max_attempts - 1:
            # Progressive delay strategy
            if attempt <= 2:
                # First few attempts: shorter delays
                delay = base_delay * (1.5 ** attempt)
            else:
                # Later attempts: longer delays with exponential backoff
                delay = base_delay * (2.5 ** attempt)
            
            # Add random jitter
            jitter = delay * 0.3 * random.uniform(-1, 1)
            delay += jitter
            
            # Ensure reasonable bounds
            delay = max(delay, 1.0)
            delay = min(delay, 120.0)  # Cap at 2 minutes
            
            print(f"⚠️  Rate limit detected for {symbol}, attempt {attempt + 1}/{max_attempts}")
            print(f"⏳ Waiting {delay:.1f} seconds before retry...")
            time.sleep(delay)
            return True
        else:
            # Final attempt failed, record rate limit
            DataManager._symbol_last_rate_limit_ts[symbol] = datetime.now().timestamp()
            return False
    
    @staticmethod
    def fetch_data(symbol, start_date, end_date):
        """Fetch data from Yahoo Finance and prepare for backtesting"""
        try:
            # Try to load from cache first
            cached_data = DataManager._load_from_cache(symbol, start_date, end_date)
            if cached_data is not None:
                return cached_data
            
            # If we recently detected a rate limit for this symbol, avoid hitting the API again immediately
            last_rl_ts = DataManager._symbol_last_rate_limit_ts.get(symbol)
            if last_rl_ts is not None:
                if (datetime.now().timestamp() - last_rl_ts) < DataManager._RATE_LIMIT_COOLDOWN_SECONDS:
                    raise ValueError(
                        f"Rate limit recently detected for {symbol}. Skipping network call during cooldown. "
                        f"Try again in {DataManager._RATE_LIMIT_COOLDOWN_SECONDS // 60} minutes."
                    )
            
            # Standardize dates for the specific market
            start_dt, end_dt = DataManager._standardize_dates(DataManager, start_date, end_date, symbol)
            
            # Download data from Yahoo Finance with improved retry logic
            print(f"🌐 Fetching data for {symbol} from Yahoo Finance...")
            print(f"📅 Date range: {start_dt.strftime('%Y-%m-%d %H:%M:%S %Z')} to {end_dt.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            
            max_attempts = 10  # Increased from 8
            base_delay = 2.0   # Reduced base delay for faster initial retries
            
            data = None
            
            # Use a cached HTTP session if available for better cache hits
            session = None
            try:
                import requests_cache
                try:
                    session = requests_cache.CachedSession(
                        cache_name='yfinance_cache', 
                        backend='sqlite', 
                        expire_after=7200,  # Increased cache time to 2 hours
                        allowable_methods=('GET', 'POST')
                    )
                except Exception:
                    session = None
            except Exception:
                session = None
            
            for attempt in range(max_attempts):
                try:
                    # Add small random delay between attempts to avoid overwhelming the API
                    if attempt > 0:
                        time.sleep(random.uniform(0.5, 1.5))
                    
                    data = yf.download(
                        symbol,
                        interval="1d",
                        start=start_dt,
                        end=end_dt,
                        auto_adjust=False,
                        group_by="column",
                        progress=False,
                        session=session,
                        threads=False,  # Disable threading to reduce concurrent requests
                        prepost=False,   # Disable pre/post market data to reduce load
                    )
                    
                    # Check if we got valid data
                    if data is not None and not data.empty and len(data) > 0:
                        break
                    else:
                        # Empty data might indicate a soft rate limit
                        raise ValueError("Received empty data - possible rate limit")
                        
                except Exception as inner_exc:
                    error_text = str(inner_exc)
                    
                    # Check if this is a rate limit error
                    if DataManager._is_rate_limit_error(error_text):
                        if not DataManager._enhanced_rate_limit_handling(symbol, attempt, max_attempts, base_delay):
                            raise ValueError(
                                f"Rate limit error for {symbol} after {max_attempts} attempts. "
                                f"Yahoo Finance API is temporarily limiting requests. "
                                f"Try again in {DataManager._RATE_LIMIT_COOLDOWN_SECONDS // 60} minutes, "
                                f"or use a different ticker/date range."
                            )
                        continue
                    else:
                        # Non-rate-limit error, don't retry
                        raise
            
            # Final check for empty data
            if data is None or data.empty:
                raise ValueError(f"No data found for {symbol} between {start_date} and {end_date}")
            
            # Clean and standardize the data
            data = DataManager._clean_and_standardize_data(data, symbol)
            
            # Check if we have enough data after cleaning
            if len(data) < 10:
                raise ValueError(f"Insufficient data for {symbol} after cleaning. Only {len(data)} data points available.")
            
            # Convert to Backtrader format
            bt_data = bt.feeds.PandasData(dataname=data)
            
            # Cache the data
            DataManager._save_to_cache(symbol, start_date, end_date, (bt_data, data))
            
            return bt_data, data
            
        except Exception as e:
            error_msg = str(e)
            if DataManager._is_rate_limit_error(error_msg):
                # Record rate limit time for cooldown
                DataManager._symbol_last_rate_limit_ts[symbol] = datetime.now().timestamp()
                raise ValueError(
                    f"Rate limit error for {symbol}: Yahoo Finance API is temporarily limiting requests. "
                    f"Try again in {DataManager._RATE_LIMIT_COOLDOWN_SECONDS // 60} minutes, "
                    f"reduce frequency, or use a different ticker/date range."
                )
            else:
                raise ValueError(f"Error fetching data for {symbol}: {error_msg}")
    
    @staticmethod
    def _clean_and_standardize_data(data, symbol):
        """Clean and standardize the downloaded data"""
        # Remove any timezone info from the index to ensure consistency
        if data.index.tz is not None:
            data.index = data.index.tz_localize(None)
        
        # Ensure the index is datetime type
        if not isinstance(data.index, pd.DatetimeIndex):
            data.index = pd.to_datetime(data.index)
        
        # Clean data
        data.dropna(inplace=True)
        data = data[data["Close"] > 0]
        
        # Flatten MultiIndex columns if present
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        
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
        start_date = end_date - timedelta(days=3*365)  # 3 years
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
        
        if total_files == 0:
            return "Cache directory is empty"
        
        # Calculate total cache size
        total_size = 0
        for filename in cache_files:
            filepath = os.path.join(DataManager.CACHE_DIR, filename)
            if os.path.isfile(filepath):
                total_size += os.path.getsize(filepath)
        
        return f"Cache contains {total_files} files, total size: {total_size / 1024 / 1024:.2f} MB"
    
    @staticmethod
    def get_rate_limit_status():
        """Get current rate limiting status and recommendations"""
        now = datetime.now().timestamp()
        rate_limited_symbols = []
        
        for symbol, last_rl_ts in DataManager._symbol_last_rate_limit_ts.items():
            time_since_rl = now - last_rl_ts
            if time_since_rl < DataManager._RATE_LIMIT_COOLDOWN_SECONDS:
                remaining_cooldown = DataManager._RATE_LIMIT_COOLDOWN_SECONDS - time_since_rl
                rate_limited_symbols.append({
                    'symbol': symbol,
                    'remaining_cooldown_minutes': int(remaining_cooldown / 60),
                    'remaining_cooldown_seconds': int(remaining_cooldown % 60)
                })
        
        if not rate_limited_symbols:
            return {
                'status': 'healthy',
                'message': 'No rate limiting detected. Yahoo Finance API is accessible.',
                'rate_limited_symbols': []
            }
        
        return {
            'status': 'rate_limited',
            'message': f'{len(rate_limited_symbols)} symbol(s) are currently rate limited.',
            'rate_limited_symbols': rate_limited_symbols,
            'recommendations': [
                'Wait for the cooldown period to expire before retrying',
                'Use different ticker symbols that haven\'t been rate limited',
                'Reduce the frequency of data requests',
                'Consider using cached data when available',
                'Try shorter date ranges to reduce data volume'
            ]
        }
    
    @staticmethod
    def get_alternative_tickers():
        """Get alternative tickers that are less likely to be rate limited"""
        # These are major indices and ETFs that typically have better availability
        return {
            '^GSPC': 'S&P 500 Index (usually most reliable)',
            '^DJI': 'Dow Jones Industrial Average',
            '^IXIC': 'NASDAQ Composite',
            'SPY': 'SPDR S&P 500 ETF',
            'QQQ': 'Invesco QQQ Trust',
            'VTI': 'Vanguard Total Stock Market ETF',
            'VOO': 'Vanguard S&P 500 ETF'
        }
