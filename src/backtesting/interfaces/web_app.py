import streamlit as st
from typing import Any

# Optional HTTP cache for yfinance requests
try:  # noqa: SIM105
    import requests_cache  # type: ignore[import-not-found]
except Exception:  # pragma: no cover
    requests_cache = None  # type: Any
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os

# Add the current directory to the path so we can import our modules
import sys
import os

# Add the src directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, '..', '..')
sys.path.insert(0, src_dir)

from backtesting.core.engine import BacktestEngine
from backtesting.core.data_manager import DataManager


def main():
    st.set_page_config(
        page_title="Investment Strategy Backtester",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize persistent UI state
    if 'chart_data' not in st.session_state:
        st.session_state['chart_data'] = None
    if 'has_run_backtest' not in st.session_state:
        st.session_state['has_run_backtest'] = False
    if 'show_detailed_chart' not in st.session_state:
        st.session_state['show_detailed_chart'] = False
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        color: #ffffff !important;
    }
    .metric-card h4 {
        color: #000000 !important;
        margin-bottom: 0.5rem;
    }
    .metric-card ul {
        color: #ffffff !important;
    }
    .metric-card li {
        color: #ffffff !important;
    }
    .strategy-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
        color: #333333 !important;
    }
    .strategy-card h4 {
        color: #333333 !important;
        margin-bottom: 0.5rem;
    }
    .strategy-card p {
        color: #333333 !important;
        margin: 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Set up HTTP caching to reduce repeated calls to Yahoo Finance
    if requests_cache is not None:
        try:
            requests_cache.install_cache(
                cache_name='yfinance_cache',
                backend='sqlite',
                expire_after=3600,  # 1 hour
            )
        except Exception:
            pass

    # Header
    st.markdown('<h1 class="main-header">📈 Investment Strategy Backtester</h1>', unsafe_allow_html=True)
    st.markdown("### Test different investment strategies with historical data")
    
    # Initialize backtest engine
    engine = BacktestEngine()
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Strategy selection
        st.subheader("Strategy")
        strategies = engine.get_available_strategies()
        strategy_names = {desc['name']: key for key, desc in strategies.items()}
        selected_strategy_name = st.selectbox(
            "Choose a strategy:",
            options=list(strategy_names.keys()),
            index=0
        )
        selected_strategy_key = strategy_names[selected_strategy_name]
        
        # Display strategy description
        strategy_desc = strategies[selected_strategy_key]
        st.info(f"**{strategy_desc['description']}**")
        
        # Strategy parameters
        if strategy_desc['parameters']:
            st.subheader("Strategy Parameters")
            strategy_params = {}
            for param_name, param_config in strategy_desc['parameters'].items():
                if param_config['type'] == 'int':
                    value = st.slider(
                        param_config['description'],
                        min_value=param_config['min'],
                        max_value=param_config['max'],
                        value=param_config['default'],
                        key=f"param_{param_name}"
                    )
                elif param_config['type'] == 'float':
                    value = st.slider(
                        param_config['description'],
                        min_value=float(param_config['min']),
                        max_value=float(param_config['max']),
                        value=float(param_config['default']),
                        step=0.1,
                        key=f"param_{param_name}"
                    )
                strategy_params[param_name] = value
        
        # Investment settings
        st.subheader("Investment Settings")
        initial_cash = st.number_input(
            "Initial Cash ($)",
            min_value=1000,
            max_value=1000000,
            value=10000,
            step=1000
        )
        
        investment_amount = st.number_input(
            "Investment Amount ($)",
            min_value=100,
            max_value=10000,
            value=500,
            step=100
        )
        
        investment_freq = st.selectbox(
            "Investment Frequency",
            options=['weekly', 'monthly', 'quarterly', 'yearly'],
            index=1
        )
        
        # Asset selection
        st.subheader("Asset")
        popular_tickers = engine.get_popular_tickers()
        
        # Create a more user-friendly selection
        ticker_options = {f"{symbol} - {desc}": symbol for symbol, desc in popular_tickers.items()}
        selected_ticker_display = st.selectbox(
            "Choose an asset:",
            options=list(ticker_options.keys()),
            index=0
        )
        selected_ticker = ticker_options[selected_ticker_display]
        
        # Custom ticker input
        custom_ticker = st.text_input(
            "Or enter custom ticker:",
            placeholder="e.g., AAPL, MSFT, ^GSPC"
        )
        
        if custom_ticker.strip():
            selected_ticker = custom_ticker.strip().upper()
        
        # Display selected ticker prominently
        st.markdown(f"""
        <div style="background-color: #d4edda; padding: 0.5rem; border-radius: 0.5rem; border-left: 4px solid #28a745; margin: 1rem 0;">
            <strong style="color: #155724;">📈 Selected Asset: {selected_ticker}</strong>
        </div>
        """, unsafe_allow_html=True)
        
        # Date range
        st.subheader("Date Range")
        default_start, default_end = DataManager.get_default_date_range()

        # Initialize session defaults for date inputs (versioned keys + version flag)
        if st.session_state.get('date_defaults_version') != '3y_v1':
            st.session_state['start_date_input_v2'] = pd.to_datetime(default_start).date()
            st.session_state['end_date_input_v2'] = pd.to_datetime(default_end).date()
            st.session_state['date_defaults_version'] = '3y_v1'

        # Reset to last 3 years button
        if st.button("↩️ Reset to last 3 years"):
            st.session_state['start_date_input_v2'] = pd.to_datetime(default_start).date()
            st.session_state['end_date_input_v2'] = pd.to_datetime(default_end).date()
            st.rerun()

        start_date = st.date_input(
            "Start Date",
            value=st.session_state['start_date_input_v2'],
            min_value=pd.to_datetime('1990-01-01').date(),
            max_value=datetime.now().date(),
            key="start_date_input_v2"
        )
        
        end_date = st.date_input(
            "End Date",
            value=st.session_state['end_date_input_v2'],
            min_value=pd.to_datetime('1990-01-01').date(),
            max_value=datetime.now().date(),
            key="end_date_input_v2"
        )
        
        # Cache information
        st.subheader("📦 Cache")
        cache_info = DataManager.get_cache_info()
        st.info(cache_info)
        
        # Cache management buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear Cache"):
                DataManager.clear_cache()
                st.success("Cache cleared!")
                st.rerun()
        
        with col2:
            if st.button("🔄 Refresh Cache Info"):
                st.rerun()
        
        # Run backtest button
        st.markdown("---")
        run_backtest = st.button(
            "🚀 Run Backtest",
            type="primary",
            use_container_width=True
        )
    
    # Main content area
    if run_backtest:
        try:
            with st.spinner("Running backtest..."):
                # Run the backtest
                metrics = engine.run_backtest(
                    symbol=selected_ticker,
                    start_date=start_date.strftime('%Y-%m-%d'),
                    end_date=end_date.strftime('%Y-%m-%d'),
                    strategy_name=selected_strategy_key,
                    initial_cash=initial_cash,
                    investment_amount=investment_amount,
                    investment_freq=investment_freq,
                    strategy_params=strategy_params if 'strategy_params' in locals() else None
                )
            
            # Persist chart data and flags for subsequent interactions
            st.session_state['chart_data'] = engine.get_chart_data()
            st.session_state['has_run_backtest'] = True
            # Reset chart visibility on a fresh run to avoid confusion
            st.session_state['show_detailed_chart'] = False

            # Display results with ticker information
            if 'data_source' in metrics and metrics['data_source'] == 'mock':
                st.warning("⚠️ **Demo Mode Active** - Using simulated data due to API rate limits or data availability issues. Results are for demonstration purposes only.")
            else:
                st.success("✅ Backtest completed successfully!")
            
            # Display ticker information prominently
            data_source_info = ""
            if 'data_source' in metrics and metrics['data_source'] == 'mock':
                data_source_info = f"""
                <div style="background-color: #fff3cd; padding: 0.5rem; border-radius: 0.25rem; margin-top: 0.5rem; border-left: 3px solid #ffc107;">
                    <p style="margin: 0; color: #856404; font-size: 0.9em;">⚠️ <strong>Demo Mode:</strong> Using simulated data due to API rate limits or data availability issues</p>
                </div>
                """
            
            st.markdown(f"""
            <div style="background-color: #e8f4fd; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #1f77b4; margin-bottom: 1rem;">
                <h3 style="margin: 0; color: #1f77b4;">📊 Backtest Results for {selected_ticker}</h3>
                <p style="margin: 0.5rem 0 0 0; color: #666;">Period: {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}</p>
                <p style="margin: 0.5rem 0 0 0; color: #666;">Strategy: {strategy_desc['name']}</p>
                {data_source_info}
            </div>
            """, unsafe_allow_html=True)
            
            # Performance metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Final Value",
                    f"${metrics['final_value']:,.2f}",
                    f"${metrics['net_profit']:+,.2f}"
                )
            
            with col2:
                st.metric(
                    "Total Return",
                    f"{metrics['total_return_pct']:.2f}%",
                    f"{metrics['annual_return_pct']:.2f}% annual"
                )
            
            with col3:
                st.metric(
                    "Max Drawdown",
                    f"{metrics['max_drawdown_pct']:.2f}%"
                )
            
            with col4:
                st.metric(
                    "Sharpe Ratio",
                    f"{metrics['sharpe_ratio']:.2f}"
                )
            
            # Detailed metrics
            st.subheader("📊 Detailed Performance")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div class="metric-card">
                <h4 style="color: #000000; margin-bottom: 0.5rem;">Investment Summary</h4>
                <ul style="color: #ffffff;">
                """, unsafe_allow_html=True)
                st.markdown(f"<li style='color: #ffffff;'>Total Invested: ${metrics['total_invested']:,.2f}</li>", unsafe_allow_html=True)
                st.markdown(f"<li style='color: #ffffff;'>Net Profit: ${metrics['net_profit']:+,.2f}</li>", unsafe_allow_html=True)
                st.markdown(f"<li style='color: #ffffff;'>Total Return: {metrics['total_return_pct']:.2f}%</li>", unsafe_allow_html=True)
                st.markdown("</ul></div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="metric-card">
                <h4 style="color: #000000; margin-bottom: 0.5rem;">Trading Statistics</h4>
                <p style="color: #000000; font-size: 0.9em; margin-bottom: 0.5rem;">Investment events represent each time the strategy made a purchase</p>
                <ul style="color: #ffffff;">
                """, unsafe_allow_html=True)
                st.markdown(f"<li style='color: #ffffff;'>Investment Events: {metrics['total_trades']}</li>", unsafe_allow_html=True)
                st.markdown(f"<li style='color: #ffffff;'>Winning Trades: {metrics['winning_trades']}</li>", unsafe_allow_html=True)
                st.markdown(f"<li style='color: #ffffff;'>Win Rate: {metrics['win_rate_pct']:.1f}%</li>", unsafe_allow_html=True)
                st.markdown("</ul></div>", unsafe_allow_html=True)
            
            # Strategy comparison (skip extra backtest if using mock data to avoid repeated API hits)
            if not ('data_source' in metrics and metrics['data_source'] == 'mock'):
                st.subheader(f"🔄 Strategy Comparison for {selected_ticker}")
                st.info(f"Compare this strategy with a simple buy-and-hold approach for {selected_ticker}")
                try:
                    with st.spinner("Running comparison..."):
                        buy_hold_metrics = engine.run_backtest(
                            symbol=selected_ticker,
                            start_date=start_date.strftime('%Y-%m-%d'),
                            end_date=end_date.strftime('%Y-%m-%d'),
                            strategy_name='dca',
                            initial_cash=initial_cash,
                            investment_amount=investment_amount,
                            investment_freq=investment_freq
                        )

                    # Create 2x2 grid of comparison charts
                    # 1. Final Value Comparison (in dollars)
                    final_value_data = pd.DataFrame({
                        'Strategy': ['Selected Strategy', 'Buy & Hold'],
                        'Final Value ($)': [
                            float(metrics['final_value']),
                            float(buy_hold_metrics['final_value'])
                        ]
                    })

                    fig_final_value = go.Figure()
                    fig_final_value.add_trace(go.Bar(
                        x=final_value_data['Strategy'],
                        y=final_value_data['Final Value ($)'],
                        marker_color=['#1f77b4', '#ff7f0e']
                    ))

                    fig_final_value.update_layout(
                        title=f"Final Portfolio Value - {selected_ticker}",
                        yaxis_title="Final Value ($)",
                        height=350
                    )

                    # 2. Total Return Comparison
                    fig_total_return = go.Figure()
                    fig_total_return.add_trace(go.Bar(
                        x=['Selected Strategy', 'Buy & Hold'],
                        y=[float(metrics['total_return_pct']), float(buy_hold_metrics['total_return_pct'])],
                        marker_color=['#1f77b4', '#ff7f0e']
                    ))

                    fig_total_return.update_layout(
                        title=f"Total Return (%) - {selected_ticker}",
                        yaxis_title="Return (%)",
                        height=350
                    )

                    # 3. Max Drawdown Comparison
                    fig_drawdown = go.Figure()
                    fig_drawdown.add_trace(go.Bar(
                        x=['Selected Strategy', 'Buy & Hold'],
                        y=[float(metrics['max_drawdown_pct']), float(buy_hold_metrics['max_drawdown_pct'])],
                        marker_color=['#1f77b4', '#ff7f0e']
                    ))

                    fig_drawdown.update_layout(
                        title=f"Maximum Drawdown (%) - {selected_ticker}",
                        yaxis_title="Drawdown (%)",
                        height=350
                    )

                    # 4. Sharpe Ratio Comparison
                    fig_sharpe = go.Figure()
                    fig_sharpe.add_trace(go.Bar(
                        x=['Selected Strategy', 'Buy & Hold'],
                        y=[float(metrics['sharpe_ratio']), float(buy_hold_metrics['sharpe_ratio'])],
                        marker_color=['#1f77b4', '#ff7f0e']
                    ))

                    fig_sharpe.update_layout(
                        title=f"Sharpe Ratio - {selected_ticker}",
                        yaxis_title="Sharpe Ratio",
                        height=350
                    )

                    # Display charts in 2x2 grid
                    col1, col2 = st.columns(2)

                    with col1:
                        st.plotly_chart(fig_final_value, use_container_width=True)
                        st.plotly_chart(fig_drawdown, use_container_width=True)

                    with col2:
                        st.plotly_chart(fig_total_return, use_container_width=True)
                        st.plotly_chart(fig_sharpe, use_container_width=True)

                except Exception as e:
                    st.warning(f"Could not run comparison: {str(e)}")
                    st.info("Comparison requires both strategies to run successfully. Try adjusting your parameters.")
            
            # Note: The detailed chart UI is rendered after this block using session state
        
        except Exception as e:
            # Display error with ticker information
            st.error(f"❌ Error running backtest for {selected_ticker}: {str(e)}")
            
            # Show ticker information even in error case
            st.markdown(f"""
            <div style="background-color: #fff3cd; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #ffc107; margin-bottom: 1rem;">
                <h3 style="margin: 0; color: #856404;">⚠️ Backtest Failed for {selected_ticker}</h3>
                <p style="margin: 0.5rem 0 0 0; color: #856404;">Period: {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}</p>
                <p style="margin: 0.5rem 0 0 0; color: #856404;">Strategy: {strategy_desc['name']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.info("""
            **Troubleshooting tips:**
            - Try a different date range (some tickers have limited historical data)
            - Check if the ticker symbol is correct
            - Try a different asset from the dropdown
            - Some tickers may have rate limits from Yahoo Finance
            - For demonstration purposes, try using popular tickers like AAPL, MSFT, or SPY
            - If you see "Demo Mode" warnings, the app is using simulated data due to API limitations
            """)
    
    else:
        # Show welcome message and instructions
        st.markdown("""
        ## 🎯 Welcome to the Investment Strategy Backtester!
        
        This tool allows you to test different investment strategies using historical market data. 
        Here's how to get started:
        
        ### 📋 Steps:
        1. **Choose a Strategy**: Select from our pre-built investment strategies in the sidebar
        2. **Configure Parameters**: Adjust strategy-specific parameters to your preference
        3. **Select Asset**: Pick from popular stocks/ETFs or enter your own ticker
        4. **Set Investment Plan**: Define your initial cash and regular investment amounts
        5. **Choose Date Range**: Select the historical period to test
        6. **Run Backtest**: Click the "Run Backtest" button to see results
        
        ### 📊 Available Strategies:
        """)
        
        # Display available strategies
        strategies = engine.get_available_strategies()
        for key, strategy in strategies.items():
            with st.container():
                st.markdown(f"""
                <div class="strategy-card">
                <h4 style="color: #333333; margin-bottom: 0.5rem;">{strategy['name']}</h4>
                <p style="color: #333333; margin: 0;">{strategy['description']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("""
        ### 💡 Tips:
        - Start with the **Dollar Cost Averaging** strategy for a baseline comparison
        - Use longer time periods (5+ years) for more reliable results
        - Compare different strategies on the same asset and time period
        - Consider the Sharpe ratio and maximum drawdown when evaluating performance
        - If you see "Demo Mode" warnings, the app is using simulated data due to API rate limits
        
        Ready to start? Configure your settings in the sidebar and run your first backtest!
        """)

    # Persistent Detailed Chart section (works across reruns)
    st.subheader(f"📈 Performance Chart for {selected_ticker}")
    if not st.session_state.get('chart_data'):
        st.info(f"Run a backtest to enable the detailed chart for {selected_ticker}.")
    else:
        cols = st.columns(2)
        with cols[0]:
            if not st.session_state.get('show_detailed_chart', False):
                if st.button("Show Detailed Chart", key="btn_show_chart"):
                    st.session_state['show_detailed_chart'] = True
                    st.rerun()
            else:
                if st.button("Hide Detailed Chart", key="btn_hide_chart"):
                    st.session_state['show_detailed_chart'] = False
                    st.rerun()

        # Render chart if toggled on
        if st.session_state.get('show_detailed_chart', False):
            try:
                chart_data = st.session_state.get('chart_data')
                if chart_data and chart_data['dates'] and chart_data['portfolio_values']:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=chart_data['dates'],
                        y=chart_data['portfolio_values'],
                        mode='lines',
                        name='Portfolio Value',
                        line=dict(color='#1f77b4', width=2)
                    ))

                    initial_value = chart_data['portfolio_values'][0] if chart_data['portfolio_values'] else initial_cash
                    fig.add_hline(
                        y=initial_value,
                        line_dash="dash",
                        line_color="gray",
                        annotation_text="Initial Investment",
                        annotation_position="bottom right"
                    )

                    fig.update_layout(
                        title=f"Portfolio Performance Over Time - {selected_ticker}",
                        xaxis_title="Date",
                        yaxis_title="Portfolio Value ($)",
                        height=500,
                        showlegend=True,
                        hovermode='x unified'
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if len(chart_data['portfolio_values']) > 1:
                            max_value = max(chart_data['portfolio_values'])
                            st.metric("Peak Portfolio Value", f"${max_value:,.2f}")
                    with col2:
                        if len(chart_data['portfolio_values']) > 1:
                            min_value = min(chart_data['portfolio_values'])
                            st.metric("Lowest Portfolio Value", f"${min_value:,.2f}")
                    with col3:
                        if len(chart_data['portfolio_values']) > 1:
                            final_value = chart_data['portfolio_values'][-1]
                            st.metric("Final Portfolio Value", f"${final_value:,.2f}")
                else:
                    st.warning("No portfolio data available for charting. Try running a backtest first.")
            except Exception as e:
                st.error(f"Error generating chart: {str(e)}")
                st.info("Chart functionality is being improved. Check the metrics above for detailed results.")


if __name__ == "__main__":
    main()
