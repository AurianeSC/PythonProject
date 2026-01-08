from datetime import date

import plotly.graph_objects as go
import streamlit as st

from src.data.fred import fetch_multi, DataFetchError
from src.data.fred_search import search_series, FredSearchError

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
st.title("Quant B — Portfolio Analysis")
st.caption("Data Source: https://fred.stlouisfed.org")

if "dynamic_catalog" not in st.session_state:
    st.session_state.dynamic_catalog = {}

# Base catalog
CATALOG = {
    # FX
    "EUR/USD (DEXUSEU)": "DEXUSEU",
    "GBP/USD (DEXUSUK)": "DEXUSUK",
    "JPY/USD (DEXJPUS)": "DEXJPUS",
    # Indices / vol
    "S&P 500 (SP500)": "SP500",
    "NASDAQ Composite (NASDAQCOM)": "NASDAQCOM",
    "Dow Jones (DJIA)": "DJIA",
    "VIX (VIXCLS)": "VIXCLS",
    # Rates
    "US 10Y Treasury (DGS10)": "DGS10",
    "US 2Y Treasury (DGS2)": "DGS2",
    "Fed Funds Rate (FEDFUNDS)": "FEDFUNDS",
    # Commodities
    "WTI Oil (DCOILWTICO)": "DCOILWTICO",
    "Gold (GOLDAMGBD228NLBM)": "GOLDAMGBD228NLBM",
    # Macro
    "US CPI (CPIAUCSL)": "CPIAUCSL",
    "US Unemployment (UNRATE)": "UNRATE",
    "US Real GDP (GDPC1)": "GDPC1",
}
CATALOG.update(st.session_state.dynamic_catalog)

# Sidebar 
st.sidebar.header("Assets")

st.sidebar.subheader("Find FRED series (search online)")
q = st.sidebar.text_input("Search keyword (e.g., gold, oil, sp500, cpi)")
limit = st.sidebar.slider("Max results", 5, 50, 15)

if q:
    try:
        results = search_series(q, limit=limit)

        if len(results) == 0:
            st.sidebar.info("No results. (Tip: FRED is macro data, not stock tickers like AAPL.)")
        else:
            # Build label -> id
            options = {
                f"{item.get('title','')} ({item.get('id','')})": item.get("id", "")
                for item in results
                if item.get("id")
            }

            picked = st.sidebar.multiselect("Search results (add to catalog)", list(options.keys()))
            if st.sidebar.button("Add selected to catalog"):
                for label in picked:
                    st.session_state.dynamic_catalog[label] = options[label]
                st.sidebar.success(f"Added {len(picked)} series.")
                st.rerun()

    except FredSearchError as e:
        st.sidebar.error(str(e))
    except Exception as e:
        st.sidebar.error(f"Search failed: {e}")

st.sidebar.subheader("Select assets (min 3)")
default_sel = [x for x in ["EUR/USD (DEXUSEU)", "S&P 500 (SP500)", "US 10Y Treasury (DGS10)"] if x in CATALOG]
selected_labels = st.sidebar.multiselect(
    "Assets",
    options=list(CATALOG.keys()),
    default=default_sel,
)

if len(selected_labels) < 3:
    st.warning("Please select at least 3 assets for Quant B.")
    st.stop()

series_ids = [CATALOG[x] for x in selected_labels]

st.sidebar.header("Portfolio settings")

rebalance = st.sidebar.selectbox("Rebalancing", ["Monthly", "None"], index=0)

start_date = st.sidebar.date_input("Start date", value=date(2015, 1, 1))
end_date = st.sidebar.date_input("End date", value=date.today())
if start_date >= end_date:
    st.sidebar.error("Start date must be < end date.")
    st.stop()

st.sidebar.subheader("Weights (auto-normalized)")
raw_weights = []
for lab in selected_labels:
    raw_weights.append(
        st.sidebar.number_input(
            lab, min_value=0.0, max_value=1.0, value=1.0 / len(selected_labels), step=0.05
        )
    )
weights = normalize_weights(raw_weights)

# Data loading 
@st.cache_data(ttl=300)
def load_levels(ids_tuple, start_dt, end_dt):
    return fetch_multi(list(ids_tuple), start=start_dt, end=end_dt)

try:
    levels = load_levels(tuple(series_ids), start_date, end_date)
except DataFetchError as e:
    st.error(f"Data fetch failed (app did not crash):\n\n{e}")
    st.stop()

levels = levels.dropna()
levels.columns = selected_labels

st.subheader("Latest observations")
st.dataframe(levels.tail(30), use_container_width=True)

# Portfolio logic 
rets = compute_returns(levels)
port_ret = portfolio_returns(rets, weights, rebalance=rebalance)
port_val = portfolio_value(port_ret, start_value=1.0)

# Charts 
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

st.subheader("Correlation matrix")
st.dataframe(correlation_matrix(rets).style.format("{:.2f}"), use_container_width=True)

st.subheader("Cumulative comparison (assets vs portfolio)")
cum_assets = (1 + rets).cumprod()
cum_assets["Portfolio"] = port_val.reindex(cum_assets.index).ffill()
st.line_chart(cum_assets)
