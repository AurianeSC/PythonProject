import plotly.graph_objects as go
import streamlit as st
from streamlit_autorefresh import st_autorefresh
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

# Auto-refresh every 5 minutes
st_autorefresh(interval=300000, key="refresh")


st.set_page_config(page_title="Quant B — Portfolio", layout="wide")
st.title("Quant B — Portfolio Analysis")
st.caption("Data Source: https://fred.stlouisfed.org")

# Session state init
if "dynamic_assets" not in st.session_state:
    st.session_state.dynamic_assets = {}

# Base Assets catalog 
ASSET_CATALOG = {
    "EUR/USD (DEXUSEU)": "DEXUSEU",
    "GBP/USD (DEXUSUK)": "DEXUSUK",
    "JPY/USD (DEXJPUS)": "DEXJPUS",
    "CHF/USD (DEXSZUS)": "DEXSZUS",
    "CAD/USD (DEXCAUS)": "DEXCAUS",
    "S&P 500 (SP500)": "SP500",
    "NASDAQ Composite (NASDAQCOM)": "NASDAQCOM",
    "Dow Jones (DJIA)": "DJIA",
    "VIX Volatility Index (VIXCLS)": "VIXCLS",
    "US 10Y Treasury (DGS10)": "DGS10",
    "US 2Y Treasury (DGS2)": "DGS2",
    "US 30Y Treasury (DGS30)": "DGS30",
    "WTI Crude Oil (DCOILWTICO)": "DCOILWTICO",
    "Brent Crude Oil (DCOILBRENTEU)": "DCOILBRENTEU"
}

def is_asset_like(item: dict) -> bool:
    
    title = (item.get("title") or "").lower()
    freq = (item.get("frequency_short") or "").upper()  # ex: 'D', 'W', 'M', 'Q'

    # 1) on garde plutôt les séries qui bougent souvent (marché)
    if freq not in {"D", "W"}:
        return False

    # 2) on garde les titres qui ressemblent à des prix/taux/indices
    keywords = [
        "price", "index", "rate", "exchange", "fx", "yield",
        "treasury", "interest", "spread", "oil", "gas", "gold",
        "brent", "wti", "vix", "s&p", "nasdaq", "dow", "etf"
    ]
    return any(k in title for k in keywords)


# Merge dynamic assets from search into the catalog
ASSET_CATALOG.update(st.session_state.dynamic_assets)

# Sidebar: Search + selection
st.sidebar.header("Assets")

selected_labels = st.sidebar.multiselect(
    "Select assets (min 3)",
    options=list(ASSET_CATALOG.keys()),
    default=["EUR/USD (DEXUSEU)", "S&P 500 (SP500)", "NASDAQ Composite (NASDAQCOM)"]
    if "NASDAQ Composite (NASDAQCOM)" in ASSET_CATALOG
    else ["EUR/USD (DEXUSEU)", "S&P 500 (SP500)", "US 10Y Treasury (DGS10)"],
)

if len(selected_labels) < 3:
    st.warning("Please select at least 3 assets for Quant B.")
    st.stop()

series_ids = [ASSET_CATALOG[x] for x in selected_labels]

st.sidebar.divider()

st.sidebar.subheader("Search an asset")
q = st.sidebar.text_input("Search keyword (e.g., gold, oil, vix, eur/usd, sp500)", value="")
limit = st.sidebar.slider("Max results", 5, 50, 15)

picked_labels = []
if q.strip():
    try:
        results = search_series(q.strip(), limit=limit)
        results = [it for it in results if is_asset_like(it)]
        options = {f"{item['title']} ({item['id']})": item["id"] for item in results}

        if len(options) == 0:
            st.sidebar.info("No results. Try a different keyword.")
        else:
            picked_labels = st.sidebar.multiselect(
                "Search results (select, then add to catalog)",
                options=list(options.keys()),
            )

            if st.sidebar.button("Add selected to catalog"):
                for lab in picked_labels:
                    st.session_state.dynamic_assets[lab] = options[lab]
                st.rerun()

    except FredSearchError as e:
        st.sidebar.error(str(e))
    except Exception as e:
        st.sidebar.error(f"Search failed: {e}")


# Portfolio settings
st.sidebar.header("Portfolio settings")
rebalance = st.sidebar.selectbox("Rebalancing", ["Weekly", "Monthly", "None"], index=1)

st.sidebar.subheader("Start date")
start_date = st.sidebar.date_input("Start date", value=None)

st.sidebar.subheader("Weights (auto-normalized)")
raw_weights = []
for lab in selected_labels:
    raw_weights.append(
        st.sidebar.number_input(
            lab,
            min_value=0.0,
            max_value=1.0,
            value=1.0 / len(selected_labels),
            step=0.01,
        )
    )
weights = normalize_weights(raw_weights)

# Load data
@st.cache_data(ttl=300)
def load_levels(ids_tuple):
    return fetch_multi(list(ids_tuple))

try:
    levels = load_levels(tuple(series_ids))
except DataFetchError as e:
    st.error(f"Data fetch failed (app did not crash):\n\n{e}")
    st.stop()

# Clean + rename columns
levels = levels.dropna()
levels.columns = selected_labels

# Filter by start_date if set
if start_date is not None:
    levels = levels[levels.index.date >= start_date]

if len(levels) < 5:
    st.warning("Not enough data after filtering. Try an earlier start date or different assets.")
    st.stop()

# Display latest observations
st.subheader("Latest observations")
st.dataframe(levels.tail(30), use_container_width=True)

# Compute returns & portfolio
rets = compute_returns(levels)
port_ret = portfolio_returns(rets, weights, rebalance=rebalance)
port_val = portfolio_value(port_ret, start_value=1.0)

# Main chart
st.subheader("asset levels and portfolio value")
fig = go.Figure()
for col in levels.columns:
    fig.add_trace(go.Scatter(x=levels.index, y=levels[col], mode="lines", name=col))

fig.add_trace(
    go.Scatter(
        x=port_val.index,
        y=port_val.values,
        mode="lines",
        name="Portfolio",
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

# Correlation matrix
st.subheader("Correlation matrix")
st.dataframe(correlation_matrix(rets).style.format("{:.2f}"), use_container_width=True)

# Cumulative comparison
st.subheader("Cumulative comparison (assets vs portfolio)")
cum_assets = (1 + rets).cumprod()
cum_assets["Portfolio"] = port_val.reindex(cum_assets.index).ffill()
st.line_chart(cum_assets)
