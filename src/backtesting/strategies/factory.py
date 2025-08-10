from .rsi import RSIStrategy
from .moving_average import MovingAverageStrategy
from .bollinger_bands import BollingerBandsStrategy
from .dollar_cost_averaging import DollarCostAveragingStrategy


class StrategyFactory:
    """Factory class to manage all available strategies"""
    
    @staticmethod
    def get_available_strategies():
        """Get all available strategies with their descriptions"""
        strategies = {
            'rsi': RSIStrategy,
            'moving_average': MovingAverageStrategy,
            'bollinger_bands': BollingerBandsStrategy,
            'dca': DollarCostAveragingStrategy,
        }
        
        strategy_descriptions = {}
        for key, strategy_class in strategies.items():
            # Get description from class without instantiating
            strategy_descriptions[key] = StrategyFactory._get_strategy_description(strategy_class)
        
        return strategy_descriptions
    
    @staticmethod
    def _get_strategy_description(strategy_class):
        """Get strategy description without instantiating"""
        if strategy_class == RSIStrategy:
            return {
                'name': 'RSI Strategy',
                'description': 'Invests when RSI falls below a threshold, indicating oversold conditions',
                'detailed_description': """
                **RSI (Relative Strength Index) Strategy** 📊
                
                This strategy uses the Relative Strength Index, a momentum oscillator that measures the speed and magnitude of price changes. 
                
                **How it works:**
                - **BUY Signal**: When RSI falls below the threshold (default: 25), it indicates the asset is oversold and potentially undervalued
                - **SELL Signal**: When RSI rises above 70, it indicates the asset is overbought and potentially overvalued
                - **Risk Management**: RSI helps identify extreme market conditions to avoid buying at peaks
                
                **Best for**: Volatile markets, swing trading, identifying entry points during market corrections
                **Parameters**: Adjust the RSI period and threshold to make the strategy more or less aggressive
                """,
                'parameters': {
                    'rsi_period': {
                        'type': 'int',
                        'default': 14,
                        'min': 5,
                        'max': 50,
                        'description': 'Period for RSI calculation'
                    },
                    'rsi_threshold': {
                        'type': 'float',
                        'default': 25.0,
                        'min': 10.0,
                        'max': 40.0,
                        'description': 'RSI threshold for investing (lower = more aggressive)'
                    }
                }
            }
        elif strategy_class == MovingAverageStrategy:
            return {
                'name': 'Moving Average Crossover',
                'description': 'Invests when fast moving average crosses above slow moving average',
                'detailed_description': """
                **Moving Average Crossover Strategy** 📈
                
                This strategy uses two moving averages of different periods to identify trend changes and momentum shifts.
                
                **How it works:**
                - **BUY Signal**: When the fast moving average crosses above the slow moving average (golden cross)
                - **SELL Signal**: When the fast moving average crosses below the slow moving average (death cross)
                - **Trend Following**: The strategy follows established trends and avoids choppy sideways markets
                
                **Best for**: Trending markets, long-term investments, reducing false signals
                **Parameters**: 
                - Fast period: Shorter-term trend (more sensitive)
                - Slow period: Longer-term trend (more stable)
                """,
                'parameters': {
                    'fast_period': {
                        'type': 'int',
                        'default': 10,
                        'min': 5,
                        'max': 50,
                        'description': 'Fast moving average period'
                    },
                    'slow_period': {
                        'type': 'int',
                        'default': 30,
                        'min': 15,
                        'max': 100,
                        'description': 'Slow moving average period'
                    }
                }
            }
        elif strategy_class == BollingerBandsStrategy:
            return {
                'name': 'Bollinger Bands Strategy',
                'description': 'Invests when price touches the lower Bollinger Band (oversold condition)',
                'detailed_description': """
                **Bollinger Bands Strategy** 📊
                
                This strategy uses Bollinger Bands, which consist of a moving average with upper and lower bands based on standard deviation.
                
                **How it works:**
                - **BUY Signal**: When price touches or falls below the lower Bollinger Band, indicating oversold conditions
                - **SELL Signal**: When price touches or rises above the upper Bollinger Band, indicating overbought conditions
                - **Mean Reversion**: Based on the principle that prices tend to revert to the mean
                - **Volatility Awareness**: Bands expand during high volatility and contract during low volatility
                
                **Best for**: Range-bound markets, mean reversion strategies, volatility-based trading
                **Parameters**: 
                - Period: Length of the moving average
                - Standard deviation: Width of the bands (higher = wider bands)
                """,
                'parameters': {
                    'bb_period': {
                        'type': 'int',
                        'default': 20,
                        'min': 10,
                        'max': 50,
                        'description': 'Period for Bollinger Bands calculation'
                    },
                    'bb_dev': {
                        'type': 'float',
                        'default': 2.0,
                        'min': 1.5,
                        'max': 3.0,
                        'description': 'Standard deviation multiplier for bands'
                    }
                }
            }
        elif strategy_class == DollarCostAveragingStrategy:
            return {
                'name': 'Dollar Cost Averaging',
                'description': 'Simple strategy that invests a fixed amount at regular intervals regardless of market conditions',
                'detailed_description': """
                **Dollar Cost Averaging (DCA) Strategy** 💰
                
                This is a passive investment strategy that invests a fixed amount at regular intervals, regardless of market conditions.
                
                **How it works:**
                - **BUY Signal**: Automatically invests at regular intervals (weekly, monthly, quarterly, yearly)
                - **SELL Signal**: No automatic selling - this is a long-term buy-and-hold strategy
                - **Market Timing**: Eliminates the need to time the market
                - **Risk Reduction**: Spreads investment over time to reduce impact of market volatility
                
                **Best for**: Long-term investors, beginners, retirement accounts, reducing emotional decision-making
                **Advantages**: 
                - Simple to implement and understand
                - Reduces risk of investing all money at market peaks
                - Encourages consistent saving habits
                - Historically proven strategy for long-term wealth building
                """,
                'parameters': {}
            }
        else:
            return {
                'name': 'Unknown Strategy',
                'description': 'Strategy description not available',
                'detailed_description': 'Detailed description not available for this strategy.',
                'parameters': {}
            }
    
    @staticmethod
    def create_strategy(strategy_name, **kwargs):
        """Create a strategy instance with the given parameters"""
        strategies = {
            'rsi': RSIStrategy,
            'moving_average': MovingAverageStrategy,
            'bollinger_bands': BollingerBandsStrategy,
            'dca': DollarCostAveragingStrategy,
        }
        
        if strategy_name not in strategies:
            raise ValueError(f"Unknown strategy: {strategy_name}")
        
        return strategies[strategy_name], kwargs
