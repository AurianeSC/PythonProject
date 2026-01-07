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
def moving_average_strategy(price: pd.Series, short_window: int = 20, long_window: int = 50) -> dict:
    df = pd.DataFrame(price)
    df.columns = ["Price"]

    df["MA_Short"] = df["Price"].rolling(short_window).mean()
    df["MA_Long"] = df["Price"].rolling(long_window).mean()

    df["Signal"] = 0
    df.loc[df["MA_Short"] > df["MA_Long"], "Signal"] = 1

    df["Returns"] = df["Price"].pct_change()
    df["Strategy_Returns"] = df["Signal"].shift(1) * df["Returns"]

    df = df.dropna()

    total_return = (1 + df["Strategy_Returns"]).prod() - 1
    annualized_return = (1 + total_return) ** (252 / len(df)) - 1
    volatility = df["Strategy_Returns"].std() * (252 ** 0.5)
    sharpe_ratio = annualized_return / volatility if volatility != 0 else np.nan

    return {
        "Total Return": total_return,
        "Annualized Return": annualized_return,
        "Volatility": volatility,
        "Sharpe Ratio": sharpe_ratio,
        "Data": df
    }
