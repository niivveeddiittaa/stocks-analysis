import yfinance as yf
yf.pdr_override()  # Fixes common data fetch issues
import sys
import subprocess

try:
    import distutils
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "setuptools==69.2.0"])
    import setuptools  # noqa: F401

import yfinance as yf
import streamlit as st
import pandas as pd
from datetime import datetime

# Initialize search tracking
if 'search_counts' not in st.session_state:
    st.session_state.search_counts = {'AAPL': 5, 'GOOGL': 4, 'TSLA': 3, 'MSFT': 2, 'AMZN': 1}

def track_search(ticker):
    ticker = ticker.upper()
    st.session_state.search_counts[ticker] = st.session_state.search_counts.get(ticker, 0) + 1

# App Configuration
st.set_page_config(
    page_title="Stock Analytics Pro",
    page_icon="📈",
    layout="wide"
)

# Custom CSS Styling
st.markdown("""
<style>
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .top-tickers {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
    }
    .ticker-item {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem 0;
    }
    .ticker-rank {
        color: #2B3467;
        font-weight: bold;
    }
    .chart-header {
        margin-top: 2rem;
        margin-bottom: 1rem;
        color: #2B3467;
    }
</style>
""", unsafe_allow_html=True)

# Main Header
st.markdown("# 📈 Stock Analysis Dashboard")

# Sidebar Controls
with st.sidebar:
    st.markdown("## 🔍 Search Parameters")
    ticker_symbol = st.text_input("Enter Stock Symbol", "AAPL").upper()
    start_date = st.date_input("Start Date", datetime(2010, 5, 31))
    end_date = st.date_input("End Date", datetime.today())
    
    # Top Searched Tickers
    st.markdown("---")
    st.markdown("## 🏆 Top Searched")
    st.markdown('<div class="top-tickers">', unsafe_allow_html=True)
    
    sorted_tickers = sorted(st.session_state.search_counts.items(), 
                          key=lambda x: x[1], reverse=True)[:5]
    
    for rank, (ticker, count) in enumerate(sorted_tickers, 1):
        st.markdown(f"""
        <div class="ticker-item">
            <span class="ticker-rank">#{rank}</span>
            <span>{ticker}</span>
            <span>{count} searches</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Main Content
try:
    with st.spinner(f"📊 Analyzing {ticker_symbol}..."):
        track_search(ticker_symbol)
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        history = ticker.history(start=start_date, end=end_date, auto_adjust=True)
        
        if not info:
            st.error("⚠️ Invalid stock symbol")
            st.stop()
            
        if history.empty:
            st.warning("📭 No historical data available")
            st.stop()

    # Company Metrics
    st.markdown("## 📋 Company Overview")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div style='color:#666; font-size:0.9rem'>Sector</div>
            <div style='font-size:1.2rem; color:#2B3467;'>{info.get('sector', 'N/A')}</div>
        </div>""", unsafe_allow_html=True)
    
    with col2:
        current_price = info.get('currentPrice', 'N/A')
        currency = info.get('currency', 'USD')
        st.markdown(f"""
        <div class="metric-card">
            <div style='color:#666; font-size:0.9rem'>Current Price</div>
            <div style='font-size:1.2rem; color:#2B3467;'>
                {f"{currency} {current_price:,.2f}" if isinstance(current_price, float) else 'N/A'}
            </div>
        </div>""", unsafe_allow_html=True)
    
    with col3:
        market_cap = info.get('marketCap', 0)
        st.markdown(f"""
        <div class="metric-card">
            <div style='color:#666; font-size:0.9rem'>Market Cap</div>
            <div style='font-size:1.2rem; color:#2B3467;'>
                {f"{currency} {market_cap/1e9:,.1f}B" if market_cap else 'N/A'}
            </div>
        </div>""", unsafe_allow_html=True)

    # Price Chart
    st.markdown("## 📈 Price Movement")
    st.line_chart(history['Close'], height=400, use_container_width=True)
    
    # Additional Metrics
    st.markdown("## 🔑 Key Statistics")
    
    stats_col1, stats_col2, stats_col3 = st.columns(3)
    with stats_col1:
        st.markdown(f"""
        <div class="metric-card">
            <div style='color:#666; font-size:0.9rem'>PE Ratio</div>
            <div style='font-size:1.2rem; color:#2B3467;'>{info.get('trailingPE', 'N/A'):,.1f}</div>
        </div>""", unsafe_allow_html=True)
    
    with stats_col2:
        st.markdown(f"""
        <div class="metric-card">
            <div style='color:#666; font-size:0.9rem'>52W High</div>
            <div style='font-size:1.2rem; color:#2B3467;'>{info.get('currency', '$')}{info.get('fiftyTwoWeekHigh', 'N/A'):,.2f}</div>
        </div>""", unsafe_allow_html=True)
    
    with stats_col3:
        st.markdown(f"""
        <div class="metric-card">
            <div style='color:#666; font-size:0.9rem'>Beta</div>
            <div style='font-size:1.2rem; color:#2B3467;'>{info.get('beta', 'N/A'):.2f}</div>
        </div>""", unsafe_allow_html=True)

    # Volume Chart
    st.markdown("## 📊 Trading Volume")
    st.bar_chart(history['Volume'], height=300, use_container_width=True)

    # Data Export
    st.markdown("---")
    st.download_button(
        label="📥 Download Historical Data",
        data=history.reset_index().to_csv(index=False).encode('utf-8'),
        file_name=f"{ticker_symbol}_data.csv",
        mime='text/csv'
    )

except Exception as e:
    st.error(f"🚨 Error: {str(e)}")
    st.markdown("""
    **💡 Troubleshooting Tips:**
    1. Verify stock symbol exists (e.g., AAPL, TSLA)
    2. Check date range validity
    3. Refresh the page
    """)

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    📌 Data provided by Yahoo Finance | ⚠️ Not investment advice | 📅 Updated: {datetime.now().strftime("%Y-%m-%d %H:%M")}
</div>
""", unsafe_allow_html=True)
