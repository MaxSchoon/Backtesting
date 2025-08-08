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
                'parameters': {}
            }
        else:
            return {
                'name': 'Unknown Strategy',
                'description': 'Strategy description not available',
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
