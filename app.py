import time
import sys
import subprocess
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

def fetch_stock_data(ticker_symbol, start_date, end_date):
    time.sleep(2)  # Add delay to prevent rate limiting
    
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        history = ticker.history(start=start_date, end=end_date, auto_adjust=True)
    
        if not info:
            raise ValueError("Invalid stock symbol")
    
        if history.empty:
            raise ValueError("No historical data available")
        
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None, None
    
    return info, history

# App Configuration
st.set_page_config(page_title="Stock Analytics Pro", page_icon="📈", layout="wide")

# Sidebar Controls
with st.sidebar:
    st.markdown("## 🔍 Search Parameters")
    ticker_symbol = st.text_input("Enter Stock Symbol", "AAPL").upper()
    start_date = st.date_input("Start Date", datetime(2010, 5, 31))
    end_date = st.date_input("End Date", datetime.today())
    
    # Top Searched Tickers
    st.markdown("---")
    st.markdown("## 🏆 Top Searched")
    sorted_tickers = sorted(st.session_state.search_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    for rank, (ticker, count) in enumerate(sorted_tickers, 1):
        st.markdown(f"**#{rank} {ticker}: {count} searches**")

# Fetch Data
try:
    with st.spinner(f"📊 Analyzing {ticker_symbol}..."):
        track_search(ticker_symbol)
        info, history = fetch_stock_data(ticker_symbol, start_date, end_date)

    if info and history is not None:
        # Company Overview
        st.markdown("## 📋 Company Overview")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Sector", info.get("sector", "N/A"))
        with col2:
            st.metric("Current Price", f"{info.get('currency', '$')}{info.get('currentPrice', 'N/A')}")
        with col3:
            st.metric("Market Cap", f"{info.get('marketCap', 0) / 1e9:.1f}B")

        # Price Chart
        st.markdown("## 📈 Price Movement")
        st.line_chart(history['Close'])

        # Additional Statistics
        st.markdown("## 🔑 Key Statistics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("PE Ratio", info.get("trailingPE", "N/A"))
        with col2:
            st.metric("52W High", f"{info.get('currency', '$')}{info.get('fiftyTwoWeekHigh', 'N/A')}")
        with col3:
            st.metric("Beta", info.get("beta", "N/A"))
        
        # Trading Volume Chart
        st.markdown("## 📊 Trading Volume")
        st.bar_chart(history['Volume'])

        # Download Historical Data
        st.download_button("📥 Download Historical Data", history.to_csv().encode('utf-8'), f"{ticker_symbol}_data.csv", "text/csv")
    else:
        st.error("⚠️ Unable to fetch data. Please check the stock symbol and try again.")

except Exception as e:
    st.error(f"🚨 Error: {str(e)}")
    st.markdown("**💡 Troubleshooting Tips:**\n1. Verify stock symbol exists (e.g., AAPL, TSLA)\n2. Check date range validity\n3. Refresh the page")

# Footer
st.markdown("---")
st.markdown(f"📌 Data from Yahoo Finance | ⚠️ Not investment advice | 📅 Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
