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

