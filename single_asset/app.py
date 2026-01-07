import streamlit as st
import plotly.graph_objects as go

from data import load_price_data
from metrics import buy_and_hold_metrics, moving_average_strategy

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Market Analytics", layout="wide")
st.title("Quant A – Single Asset")

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
ticker = st.sidebar.text_input("Ticker", "AAPL.US")
period = st.sidebar.selectbox("Period", ["6mo", "1y", "2y", "5y"])

st.sidebar.subheader("Moving Average Strategy")
short_window = st.sidebar.slider("Short MA", 5, 50, 20)
long_window = st.sidebar.slider("Long MA", 20, 200, 50)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
data = load_price_data(ticker, period)

if data.empty:
    st.error("No data available for this ticker.")
    st.stop()

# --------------------------------------------------
# PRICE CHART
# --------------------------------------------------
st.subheader(f"Price evolution for {ticker}")

st.line_chart(data.rename(columns={"Close": "Price"}))

# --------------------------------------------------
# BUY & HOLD METRICS
# --------------------------------------------------
bh_metrics = buy_and_hold_metrics(data["Close"])

st.subheader("Buy & Hold Performance")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Return", f"{bh_metrics['Total Return']*100:.2f}%")
c2.metric("Annualized Return", f"{bh_metrics['Annualized Return']*100:.2f}%")
c3.metric("Volatility", f"{bh_metrics['Volatility']*100:.2f}%")
c4.metric("Sharpe Ratio", f"{bh_metrics['Sharpe Ratio']:.2f}")

# --------------------------------------------------
# MOVING AVERAGE STRATEGY
# --------------------------------------------------
ma_results = moving_average_strategy(
    data["Close"],
    short_window=short_window,
    long_window=long_window
)

df_ma = ma_results["Data"]
ma_metrics = ma_results["Metrics"]

st.subheader("Moving Average Strategy Performance")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Return", f"{ma_metrics['Total Return']*100:.2f}%")
c2.metric("Annualized Return", f"{ma_metrics['Annualized Return']*100:.2f}%")
c3.metric("Volatility", f"{ma_metrics['Volatility']*100:.2f}%")
c4.metric("Sharpe Ratio", f"{ma_metrics['Sharpe Ratio']:.2f}")

# --------------------------------------------------
# PRICE + MA + BUY / SELL SIGNALS
# --------------------------------------------------
st.subheader("Price, Moving Averages & Trading Signals")

buy_signals = df_ma[df_ma["Position"] == 1]
sell_signals = df_ma[df_ma["Position"] == -1]

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df_ma.index,
    y=df_ma["Price"],
    name="Price",
    line=dict(color="blue")
))

fig.add_trace(go.Scatter(
    x=df_ma.index,
    y=df_ma["MA_Short"],
    name="Short MA",
    line=dict(color="orange")
))

fig.add_trace(go.Scatter(
    x=df_ma.index,
    y=df_ma["MA_Long"],
    name="Long MA",
    line=dict(color="purple")
))

fig.add_trace(go.Scatter(
    x=buy_signals.index,
    y=buy_signals["Price"],
    mode="markers",
    name="BUY",
    marker=dict(symbol="triangle-up", size=12, color="green")
))

fig.add_trace(go.Scatter(
    x=sell_signals.index,
    y=sell_signals["Price"],
    mode="markers",
    name="SELL",
    marker=dict(symbol="triangle-down", size=12, color="red")
))

fig.update_layout(
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

st.plotly_chart(fig, use_container_width=True)
