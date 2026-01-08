import numpy as np
import pandas as pd

"Calculates daily returns based on price levels"

def compute_returns(levels: pd.DataFrame) -> pd.DataFrame:
    return levels.pct_change().dropna()

"Normalizes the weights in the portfolio so that their sum equals 1"
def normalize_weights(raw_weights: list[float]) -> np.ndarray:
    w = np.array(raw_weights, dtype=float)
    w[w < 0] = 0.0
    s = float(w.sum())
    if s == 0.0:
        return np.repeat(1.0 / len(w), len(w))
    return w / s

"Calculates portfolio returns based on asset returns and weights"
def portfolio_returns(returns: pd.DataFrame, weights: np.ndarray, rebalance: str = "Monthly") -> pd.Series:

    # No rebalance: weights stay constant

    if rebalance == "None":
        pr = (returns * weights).sum(axis=1)
        pr.name = "Portfolio"
        return pr


    out = []
    last_month = None
    w = weights.copy()

    for dt, row in returns.iterrows():
        month = dt.to_period("M")
        if last_month is None:
            last_month = month
        if month != last_month:
            w = weights.copy()
            last_month = month

    if rebalance not in ("Monthly", "Weekly"):
        raise ValueError("rebalance must be one of: 'None', 'Weekly', 'Monthly'")

    out = []
    w = weights.copy()
    last_bucket = None

    for dt, row in returns.iterrows():
        bucket = dt.to_period("W") if rebalance == "Weekly" else dt.to_period("M")

        if last_bucket is None:
            last_bucket = bucket

        # when period changes, reset weights
        if bucket != last_bucket:
            w = weights.copy()
            last_bucket = bucket

        out.append(float(np.dot(w, row.values)))

    return pd.Series(out, index=returns.index, name="Portfolio")

"Converts returns into cumulative portfolio value"

def portfolio_value(port_ret: pd.Series, start_value: float = 1.0) -> pd.Series:
    return (1.0 + port_ret).cumprod() * float(start_value)
