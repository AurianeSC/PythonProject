import numpy as np
import pandas as pd

def buy_and_hold_metrics(prices: pd.Series):
    returns = prices.pct_change().dropna()

    total_return = prices.iloc[-1] / prices.iloc[0] - 1
    annualized_return = (1 + total_return) ** (252 / len(returns)) - 1
    volatility = returns.std() * np.sqrt(252)
    sharpe = annualized_return / volatility if volatility != 0 else np.nan

    return {
        "Total Return": total_return,
        "Annualized Return": annualized_return,
        "Volatility": volatility,
        "Sharpe Ratio": sharpe
    }


def moving_average_strategy(prices: pd.Series, short_window=20, long_window=50):
    df = pd.DataFrame({"Price": prices})
    df["MA_Short"] = prices.rolling(short_window).mean()
    df["MA_Long"] = prices.rolling(long_window).mean()

    df["Signal"] = 0
    df.loc[df["MA_Short"] > df["MA_Long"], "Signal"] = 1
    df["Position"] = df["Signal"].diff()

    df["Returns"] = prices.pct_change()
    df["Strategy_Returns"] = df["Returns"] * df["Signal"].shift(1)

    returns = df["Strategy_Returns"].dropna()

    total_return = (1 + returns).prod() - 1
    annualized_return = (1 + total_return) ** (252 / len(returns)) - 1
    volatility = returns.std() * np.sqrt(252)
    sharpe = annualized_return / volatility if volatility != 0 else np.nan

    return {
        "Metrics": {
            "Total Return": total_return,
            "Annualized Return": annualized_return,
            "Volatility": volatility,
            "Sharpe Ratio": sharpe
        },
        "Data": df
    }
