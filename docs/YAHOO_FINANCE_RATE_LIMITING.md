# Yahoo Finance Rate Limiting Guide

## Overview

This guide explains how to handle rate limiting issues when using Yahoo Finance data in the backtesting framework. Rate limiting occurs when too many requests are made to the Yahoo Finance API in a short period.

## What is Rate Limiting?

Rate limiting is a protection mechanism that prevents abuse of the Yahoo Finance API. When you hit the rate limit, you'll see errors like:
- "Too Many Requests. Rate limited. Try after a while."
- "429 Too Many Requests"
- "Rate limit exceeded"

## Enhanced Rate Limiting Features

The framework now includes several improvements to handle rate limiting:

### 1. Smart Retry Logic
- **Progressive Delays**: Starts with shorter delays and increases them progressively
- **Exponential Backoff**: Later attempts use longer delays to avoid overwhelming the API
- **Random Jitter**: Adds randomness to prevent multiple clients from retrying simultaneously
- **Increased Attempts**: Now tries up to 10 times before giving up

### 2. Symbol-Specific Cooldowns
- When a symbol hits a rate limit, it's marked for a 10-minute cooldown
- Other symbols can still be fetched during this period
- Prevents repeated failures on the same symbol

### 3. Enhanced Error Detection
- Better detection of rate limit errors vs. other types of errors
- Automatic fallback to mock data when rate limits are hit
- Clear error messages with actionable advice

## Best Practices

### 1. Use Caching
```python
# The framework automatically caches data
# Cached data is used when available, reducing API calls
```

### 2. Batch Your Requests
```python
# Instead of fetching multiple symbols one by one
# Consider fetching them in a single session
```

### 3. Use Alternative Tickers
When a popular ticker is rate limited, try these alternatives:
- **^GSPC** (S&P 500) instead of **SPY**
- **^DJI** (Dow Jones) instead of **DIA**
- **^IXIC** (NASDAQ) instead of **QQQ**

### 4. Reduce Date Ranges
- Shorter date ranges require less data and are less likely to hit limits
- Start with 1-2 years instead of 5+ years
- Use the most recent data when possible

### 5. Avoid Peak Hours
- US market hours (9:30 AM - 4:00 PM ET) tend to have higher traffic
- Try fetching data during off-hours or weekends

## Troubleshooting

### Check Rate Limit Status
```python
from backtesting.core.data_manager import DataManager

status = DataManager.get_rate_limit_status()
print(status)
```

### Clear Cache
```python
from backtesting.core.data_manager import DataManager

DataManager.clear_cache()
```

### Get Alternative Tickers
```python
from backtesting.core.data_manager import DataManager

alternatives = DataManager.get_alternative_tickers()
print(alternatives)
```

## Error Messages and Solutions

### "Rate limit recently detected for SYMBOL"
**Solution**: Wait for the cooldown period (10 minutes) or use a different symbol

### "Rate limit error after X attempts"
**Solution**: 
1. Wait 10+ minutes before retrying
2. Use a different ticker symbol
3. Reduce the date range
4. Use cached data if available

### "No data found for SYMBOL"
**Solution**:
1. Check if the symbol is valid
2. Verify the date range
3. Try a different symbol
4. Use mock data for testing

## Advanced Configuration

### Custom Rate Limit Settings
You can modify these settings in `src/backtesting/core/data_manager.py`:

```python
class DataManager:
    _RATE_LIMIT_COOLDOWN_SECONDS = 600  # 10 minutes
    # Increase for more conservative rate limiting
    # Decrease for more aggressive retries
```

### Session Configuration
The framework uses `requests-cache` for HTTP caching:
- Cache duration: 2 hours
- Backend: SQLite
- Automatically reduces API calls

## Fallback Strategies

### 1. Mock Data
When rate limits are hit, the framework automatically falls back to mock data:
- Realistic price movements
- Proper OHLC structure
- Business day generation (excludes weekends)

### 2. Cached Data
- Previously fetched data is automatically cached
- Cache persists between sessions
- Significantly reduces API calls

### 3. Alternative Data Sources
Consider these alternatives for production use:
- Alpha Vantage
- IEX Cloud
- Polygon.io
- Financial Modeling Prep

## Monitoring and Logging

The framework provides detailed logging for rate limiting:
- Rate limit detection messages
- Retry attempt counts
- Cooldown period information
- Cache hit/miss statistics

## Example Usage

```python
from backtesting.core.engine import BacktestEngine

engine = BacktestEngine()

try:
    # This will automatically handle rate limiting
    metrics = engine.run_backtest(
        symbol='AAPL',
        start_date='2023-01-01',
        end_date='2023-12-31',
        strategy_name='rsi',
        initial_cash=10000,
        investment_amount=500
    )
    print("Backtest completed successfully")
    
except ValueError as e:
    if "Rate limit" in str(e):
        print("Rate limit hit. Try again later or use a different symbol.")
        print("Using mock data for demonstration...")
        # The framework will automatically use mock data
    else:
        print(f"Error: {e}")
```

## Summary

The enhanced rate limiting handling provides:
1. **Automatic retries** with smart backoff
2. **Symbol-specific cooldowns** to prevent repeated failures
3. **Automatic fallbacks** to mock data
4. **Comprehensive caching** to reduce API calls
5. **Clear error messages** with actionable advice

By following these best practices and using the enhanced features, you can minimize rate limiting issues and ensure your backtesting runs smoothly.
