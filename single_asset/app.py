from metrics import moving_average_strategy
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

st.sidebar.subheader("Moving Average Strategy")

short_window = st.sidebar.slider("Short MA", 5, 50, 20)
long_window = st.sidebar.slider("Long MA", 20, 200, 50)
ma_metrics = moving_average_strategy(
    data["Close"],
    short_window=short_window,
    long_window=long_window
)

st.subheader("Moving Average Strategy Performance")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Return", f"{ma_metrics['Total Return']*100:.2f}%")
col2.metric("Annualized Return", f"{ma_metrics['Annualized Return']*100:.2f}%")
col3.metric("Volatility", f"{ma_metrics['Volatility']*100:.2f}%")
col4.metric("Sharpe Ratio", f"{ma_metrics['Sharpe Ratio']:.2f}")
st.subheader("Price & Moving Averages")

st.line_chart(
    ma_metrics["Data"][["Price", "MA_Short", "MA_Long"]]
)
