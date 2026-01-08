import streamlit as st
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

from data import load_price_data
from metrics import buy_and_hold_metrics, moving_average_strategy, compute_rsi
from metrics import compute_equity_curve


# PAGE CONFIG
st.set_page_config(page_title="Market Analytics", layout="wide")
st.title("Quant A – Single Asset")

# Auto-refresh every 5 minutes
st_autorefresh(interval=300000, key="refresh")


# SIDEBAR
ticker = st.sidebar.text_input("Ticker", "AAPL.US")
period = st.sidebar.selectbox("Period", ["6mo", "1y", "2y", "5y"])

st.sidebar.subheader("Moving Average Strategy")
short_window = st.sidebar.slider("Short MA", 5, 50, 20)
long_window = st.sidebar.slider("Long MA", 20, 200, 50)

# LOAD DATA (CACHED)
@st.cache_data(ttl=300)
def cached_load_data(ticker, period):
    return load_price_data(ticker, period)

data = cached_load_data(ticker, period)

if data.empty:
    st.error("No data available for this ticker.")
    st.stop()

# CURRENT PRICE
current_price = data["Close"].iloc[-1]
st.metric("Current Price", f"{current_price:.2f}")

# BUY & HOLD METRICS

bh_metrics = buy_and_hold_metrics(data["Close"])

# BUY & HOLD EQUITY CURVE
bh_returns = data["Close"].pct_change()
bh_equity = compute_equity_curve(bh_returns)

st.subheader("Buy & Hold Performance")
c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Total Return", f"{bh_metrics['Total Return']*100:.2f}%")
c2.metric("Annualized Return", f"{bh_metrics['Annualized Return']*100:.2f}%")
c3.metric("Volatility", f"{bh_metrics['Volatility']*100:.2f}%")
c4.metric("Sharpe Ratio", f"{bh_metrics['Sharpe Ratio']:.2f}")
c5.metric("Max Drawdown", f"{bh_metrics['Max Drawdown']*100:.2f}%")


# MOVING AVERAGE STRATEGY

ma_results = moving_average_strategy(
    data["Close"],
    short_window=short_window,
    long_window=long_window
)

df_ma = ma_results["Data"]
df_ma["RSI"] = compute_rsi(df_ma["Price"])

ma_metrics = ma_results["Metrics"]

st.subheader("Moving Average Strategy Performance")
c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Total Return", f"{ma_metrics['Total Return']*100:.2f}%")
c2.metric("Annualized Return", f"{ma_metrics['Annualized Return']*100:.2f}%")
c3.metric("Volatility", f"{ma_metrics['Volatility']*100:.2f}%")
c4.metric("Sharpe Ratio", f"{ma_metrics['Sharpe Ratio']:.2f}")
c5.metric("Max Drawdown", f"{ma_metrics['Max Drawdown']*100:.2f}%")


# MAIN CHART — PRICE + STRATEGY EQUITY 

st.subheader("Price & Strategy Cumulative Performance")

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df_ma.index,
    y=df_ma["Price"],
    name="Price",
    line=dict(color="blue")
))

fig.add_trace(go.Scatter(
    x=df_ma.index,
    y=df_ma["Equity"],
    name="Strategy Equity (Base 100)",
    line=dict(color="green"),
    yaxis="y2"
))

fig.update_layout(
    yaxis=dict(title="Price"),
    yaxis2=dict(
        title="Strategy Value",
        overlaying="y",
        side="right"
    ),
    legend=dict(orientation="h")
)

st.plotly_chart(fig, use_container_width=True)


# PRICE + MA + BUY / SELL SIGNALS

st.subheader("Price, Moving Averages & Trading Signals")

buy_signals = df_ma[df_ma["Position"] == 1]
sell_signals = df_ma[df_ma["Position"] == -1]

fig2 = go.Figure()

fig2.add_trace(go.Scatter(
    x=df_ma.index,
    y=df_ma["Price"],
    name="Price",
    line=dict(color="blue")
))

fig2.add_trace(go.Scatter(
    x=df_ma.index,
    y=df_ma["MA_Short"],
    name="Short MA",
    line=dict(color="orange")
))

fig2.add_trace(go.Scatter(
    x=df_ma.index,
    y=df_ma["MA_Long"],
    name="Long MA",
    line=dict(color="purple")
))

fig2.add_trace(go.Scatter(
    x=buy_signals.index,
    y=buy_signals["Price"],
    mode="markers",
    name="BUY",
    marker=dict(symbol="triangle-up", size=12, color="green")
))

fig2.add_trace(go.Scatter(
    x=sell_signals.index,
    y=sell_signals["Price"],
    mode="markers",
    name="SELL",
    marker=dict(symbol="triangle-down", size=12, color="red")
))

fig2.update_layout(
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

st.plotly_chart(fig2, use_container_width=True)

# EQUITY CURVES COMPARISON — STRATEGY VS BUY & HOLD

st.subheader("Equity Curves Comparison: Strategy vs Buy & Hold")

fig_eq = go.Figure()

fig_eq.add_trace(go.Scatter(
    x=bh_equity.index,
    y=bh_equity,
    name="Buy & Hold Equity (Base 100)",
    line=dict(color="blue")
))

fig_eq.add_trace(go.Scatter(
    x=df_ma.index,
    y=df_ma["Equity"],
    name="Strategy Equity (Base 100)",
    line=dict(color="green")
))

fig_eq.update_layout(
    yaxis=dict(title="Equity Value"),
    xaxis=dict(title="Date"),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

st.plotly_chart(fig_eq, use_container_width=True)

# LATEST DATA TABLE

st.subheader("Latest Available Data")

latest_data = data.tail(10).copy()

latest_data["Return (%)"] = latest_data["Close"].pct_change() * 100

latest_data = latest_data[[
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
    "Return (%)"
]]

st.dataframe(
    latest_data.style.format({
        "Open": "{:.2f}",
        "High": "{:.2f}",
        "Low": "{:.2f}",
        "Close": "{:.2f}",
        "Volume": "{:,.0f}",
        "Return (%)": "{:.2f}"
    }),
    use_container_width=True
)

