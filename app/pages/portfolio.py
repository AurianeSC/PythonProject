import plotly.graph_objects as go
import streamlit as st
from src.data.fred import fetch_multi, DataFetchError
from src.metrics.portfolio_metrics import (
    correlation_matrix,
    annualized_return,
    annualized_volatility,
    max_drawdown,
)

from src.strategies.portfolio_construction import (
    compute_returns,
    normalize_weights,
    portfolio_returns,
    portfolio_value,
)

st.set_page_config(page_title="Quant B — Portfolio", layout="wide")
st.title("Quant B — Portfolio Analysis\nData Source : https://fred.stlouisfed.org")

# Asset catalog
CATALOG = {
    "EUR/USD (DEXUSEU)": "DEXUSEU",
    "S&P 500 (SP500)": "SP500",
    "US 10Y Rate (DGS10)": "DGS10",
    "WTI Oil (DCOILWTICO)": "DCOILWTICO",
}

# Sidebar
st.sidebar.header("Assets")
selected_labels = st.sidebar.multiselect(
    "Select at least 3 assets",
    options=list(CATALOG.keys()),
    default=["EUR/USD (DEXUSEU)", "S&P 500 (SP500)", "US 10Y Rate (DGS10)"],
)

if len(selected_labels) < 3:
    st.warning("Please select at least 3 assets for Quant B.")
    st.stop()

series_ids = [CATALOG[x] for x in selected_labels]

st.sidebar.header("Portfolio settings")
rebalance = st.sidebar.selectbox("Rebalancing", ["Monthly", "None"], index=0)

st.sidebar.subheader("Weights (auto-normalized)")
raw_weights = []
for lab in selected_labels:
    raw_weights.append(
        st.sidebar.number_input(lab, min_value=0.0, max_value=1.0, value=1.0 / len(selected_labels), step=0.05)
    )
weights = normalize_weights(raw_weights)

# Load data with cache (refresh every 5 min)
@st.cache_data(ttl=300)
def load_levels(ids_tuple):
    return fetch_multi(list(ids_tuple))

try:
    levels = load_levels(tuple(series_ids))
except DataFetchError as e:
    st.error(f"Data fetch failed (app did not crash):\n\n{e}")
    st.stop()

levels = levels.dropna()
levels.columns = selected_labels

st.subheader("Latest observations")
st.dataframe(levels.tail(30), use_container_width=True)

# Compute returns and portfolio
rets = compute_returns(levels)
port_ret = portfolio_returns(rets, weights, rebalance=rebalance)
port_val = portfolio_value(port_ret, start_value=1.0)

# Main chart
st.subheader("Main chart: asset levels + portfolio value (base=1)")
fig = go.Figure()

for col in levels.columns:
    fig.add_trace(go.Scatter(x=levels.index, y=levels[col], mode="lines", name=col))

fig.add_trace(
    go.Scatter(
        x=port_val.index,
        y=port_val.values,
        mode="lines",
        name="Portfolio (base=1)",
        yaxis="y2",
    )
)

fig.update_layout(
    height=520,
    xaxis=dict(title="Date"),
    yaxis=dict(title="Series level"),
    yaxis2=dict(title="Portfolio value", overlaying="y", side="right"),
    legend=dict(orientation="h"),
)
st.plotly_chart(fig, use_container_width=True)

# Metrics
st.subheader("Portfolio metrics")
c1, c2, c3 = st.columns(3)
c1.metric("Annualized return", f"{annualized_return(port_ret):.2%}")
c2.metric("Annualized volatility", f"{annualized_volatility(port_ret):.2%}")
c3.metric("Max drawdown", f"{max_drawdown(port_val):.2%}")

# Correlation
st.subheader("Correlation matrix")
st.dataframe(correlation_matrix(rets).style.format("{:.2f}"), use_container_width=True)

# Cumulative comparison
st.subheader("Cumulative comparison (assets vs portfolio)")
cum_assets = (1 + rets).cumprod()
cum_assets["Portfolio"] = port_val.reindex(cum_assets.index).ffill()
st.line_chart(cum_assets)
