import pandas as pd
import numpy as np

def compute_returns(price: pd.Series) -> pd.Series:
    return price.pct_change().dropna()

def buy_and_hold_metrics(price: pd.Series) -> dict:
    returns = compute_returns(price)

    total_return = price.iloc[-1] / price.iloc[0] - 1
    annualized_return = (1 + total_return) ** (252 / len(price)) - 1
    volatility = returns.std() * np.sqrt(252)
    sharpe_ratio = annualized_return / volatility if volatility != 0 else np.nan

    return {
        "Total Return": total_return,
        "Annualized Return": annualized_return,
        "Volatility": volatility,
        "Sharpe Ratio": sharpe_ratio
    }
