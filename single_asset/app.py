from metrics import buy_and_hold_metrics
import streamlit as st
from data import load_price_data

st.set_page_config(page_title="Market Analytics", layout="wide")

st.title("Quant A – Single Asset")

ticker = st.sidebar.text_input("Ticker", "AAPL.US")
period = st.sidebar.selectbox("Period", ["6mo", "1y", "2y", "5y"])

data = load_price_data(ticker, period)

if data.empty:
    st.error("No data available for this ticker.")
else:
    st.subheader(f"Price evolution for {ticker}")
    st.line_chart(data.rename(columns={"Close": "Price"}))

metrics = buy_and_hold_metrics(data["Close"])

st.subheader("Buy & Hold Performance")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Return", f"{metrics['Total Return']*100:.2f}%")
col2.metric("Annualized Return", f"{metrics['Annualized Return']*100:.2f}%")
col3.metric("Volatility", f"{metrics['Volatility']*100:.2f}%")
col4.metric("Sharpe Ratio", f"{metrics['Sharpe Ratio']:.2f}")
