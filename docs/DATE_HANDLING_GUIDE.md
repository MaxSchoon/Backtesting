# Date Handling and Standardization Guide

## Overview

This guide explains how the backtesting framework handles dates across different markets and timezones. Proper date handling is crucial for accurate backtesting results, especially when dealing with international markets.

## Market-Specific Date Handling

### US Markets (Eastern Time)
- **Symbols**: AAPL, MSFT, GOOGL, SPY, QQQ, ^GSPC, ^DJI, ^IXIC
- **Timezone**: America/New_York (ET)
- **Market Hours**: 9:30 AM - 4:00 PM ET (excluding holidays)
- **Date Handling**: Standard US market calendar

### European Markets (Central European Time)
- **Symbols**: ^STOXX50E, ^GDAXI, ^FCHI, ^FTSE
- **Timezone**: Europe/Berlin, Europe/Paris, Europe/London
- **Market Hours**: Varies by exchange (typically 9:00 AM - 5:30 PM CET)
- **Date Handling**: European market calendar with different holidays

### Asian Markets
- **Symbols**: ^N225 (Tokyo), ^HSI (Hong Kong), ^BSESN (Mumbai)
- **Timezone**: Asia/Tokyo, Asia/Hong_Kong, Asia/Kolkata
- **Market Hours**: Varies by exchange
- **Date Handling**: Local market calendars

## Date Standardization Process

### 1. Input Date Processing
```python
# The framework automatically standardizes input dates
start_date = "2023-01-01"
end_date = "2023-12-31"

# These are converted to the appropriate market timezone
# and then normalized to UTC for consistent processing
```

### 2. Market Timezone Detection
```python
# Each symbol is mapped to its appropriate timezone
MARKET_TIMEZONES = {
    'AAPL': 'America/New_York',
    '^GDAXI': 'Europe/Berlin',
    '^N225': 'Asia/Tokyo',
    'DEFAULT': 'America/New_York'
}
```

### 3. UTC Normalization
- All dates are converted to UTC for consistent processing
- This ensures accurate calculations regardless of local timezone
- Market-specific logic is applied during data processing

## Trading Day Calculations

### Business Days vs. Trading Days
- **Business Days**: Excludes weekends (Saturday, Sunday)
- **Trading Days**: Excludes weekends AND market holidays

### US Market Holidays
The framework automatically excludes these major US holidays:
- New Year's Day (January 1)
- Independence Day (July 4)
- Christmas Day (December 25)
- Thanksgiving (4th Thursday in November)

### International Market Holidays
- European markets have different holiday schedules
- Asian markets follow local holiday calendars
- The framework uses timezone-aware calculations

## Date Range Validation

### Automatic Adjustments
```python
# If end date is in the future, it's automatically adjusted
end_date = "2025-01-01"  # Future date
# Automatically adjusted to current time
```

### Reasonable Bounds
- **Minimum Start Date**: 1990-01-01 (earliest reliable data)
- **Maximum End Date**: Current time
- **Minimum Range**: 1 day
- **Recommended Range**: 1-5 years for optimal performance

## Investment Frequency Calculations

### Period Counting
The framework calculates investment periods based on trading days:

```python
if investment_freq == 'weekly':
    periods = max(1, trading_days // 7)
elif investment_freq == 'monthly':
    periods = max(1, (end_year - start_year) * 12 + (end_month - start_month) + 1)
elif investment_freq == 'quarterly':
    periods = max(1, ((end_year - start_year) * 4 + (end_month - start_month) // 3) + 1)
```

### Market-Aware Scheduling
- Cash is only added on market open days
- Weekend and holiday investments are automatically deferred
- This ensures realistic backtesting scenarios

## Data Fetching and Date Handling

### Yahoo Finance Integration
```python
# Dates are standardized before sending to Yahoo Finance
start_dt, end_dt = DataManager._standardize_dates(start_date, end_date, symbol)

# This ensures consistent data across different markets
data = yf.download(
    symbol,
    start=start_dt,  # Standardized start date
    end=end_dt,      # Standardized end date
    interval="1d"
)
```

### Cache Key Generation
```python
# Cache keys include date information for proper retrieval
cache_key = f"{symbol}_{start_date}_{end_date}.pkl"
```

## Common Date-Related Issues

### 1. Timezone Mismatches
**Problem**: Dates appear to be off by several hours
**Solution**: The framework automatically handles timezone conversion

### 2. Missing Data on Holidays
**Problem**: No data for certain dates
**Solution**: This is normal - markets are closed on holidays

### 3. Weekend Data
**Problem**: Data appears on weekends
**Solution**: The framework filters out weekend data automatically

### 4. Date Range Too Long
**Problem**: Very long date ranges may hit rate limits
**Solution**: Use shorter ranges (1-3 years) for better reliability

## Best Practices

### 1. Use Standard Date Formats
```python
# Recommended formats
start_date = "2023-01-01"      # YYYY-MM-DD
end_date = "2023-12-31"        # YYYY-MM-DD

# Also supported
start_date = "01/01/2023"      # MM/DD/YYYY
start_date = "2023-01-01T00:00:00"  # ISO format
```

### 2. Choose Appropriate Date Ranges
- **Testing**: 6 months - 1 year
- **Development**: 1-2 years
- **Production**: 2-5 years
- **Research**: 5+ years (may hit rate limits)

### 3. Consider Market Hours
- US markets: 9:30 AM - 4:00 PM ET
- European markets: 9:00 AM - 5:30 PM CET
- Asian markets: Vary by exchange

### 4. Handle Holidays Gracefully
```python
# The framework automatically handles holidays
# But you can check if a date is a trading day
if strategy._is_market_open(current_date):
    # Market is open, proceed with strategy
    pass
else:
    # Market is closed, skip this date
    pass
```

## Advanced Date Handling

### Custom Holiday Calendars
```python
# You can extend the holiday detection
def _is_trading_day(self, date):
    # Add custom holidays for your specific needs
    custom_holidays = [
        (12, 24),  # Christmas Eve
        (7, 3),    # Day before Independence Day
    ]
    
    for month, day in custom_holidays:
        if date.month == month and date.day == day:
            return False
    
    return True
```

### Market-Specific Logic
```python
# Different markets may have different trading hours
def get_market_hours(symbol):
    if symbol.startswith('^GDAXI'):
        return "9:00 AM - 5:30 PM CET"
    elif symbol.startswith('^N225'):
        return "9:00 AM - 3:00 PM JST"
    else:
        return "9:30 AM - 4:00 PM ET"
```

## Debugging Date Issues

### Enable Debug Logging
```python
# The framework provides detailed date information
print(f"Debug - Start Date: {start_date}, End Date: {end_date}")
print(f"Debug - Trading Days: {trading_days}")
print(f"Debug - Investment Frequency: {investment_freq}")
```

### Check Date Standardization
```python
from backtesting.core.data_manager import DataManager

# Check how dates are being processed
start_dt, end_dt = DataManager._standardize_dates(
    DataManager, "2023-01-01", "2023-12-31", "AAPL"
)
print(f"Standardized: {start_dt} to {end_dt}")
```

### Verify Trading Days
```python
# Check if specific dates are trading days
from backtesting.core.engine import BacktestEngine

engine = BacktestEngine()
is_trading = engine._is_trading_day(pd.to_datetime("2023-12-25"))
print(f"Christmas 2023 is trading day: {is_trading}")  # False
```

## Summary

The enhanced date handling system provides:

1. **Automatic timezone conversion** for different markets
2. **Market-aware trading day calculations** excluding weekends and holidays
3. **Consistent date processing** across all components
4. **Intelligent investment scheduling** based on market hours
5. **Comprehensive validation** with automatic adjustments

By following these guidelines and using the built-in date handling features, you can ensure accurate and reliable backtesting results across different markets and timezones.
