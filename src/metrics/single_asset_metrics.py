import numpy as np
import pandas as pd
from scipy import stats


def max_drawdown(series: pd.Series) -> float:
    """
    Compute maximum drawdown of a cumulative series.
    """
    cum_max = series.cummax()
    drawdown = (series - cum_max) / cum_max
    return drawdown.min()


def compute_equity_curve(returns: pd.Series, base: float = 100) -> pd.Series:
    """
    Compute cumulative equity curve from returns.
    """
    return base * (1 + returns.fillna(0)).cumprod()


def buy_and_hold_metrics(prices: pd.Series) -> dict:
    returns = prices.pct_change().dropna()

    total_return = prices.iloc[-1] / prices.iloc[0] - 1
    annualized_return = (1 + total_return) ** (252 / len(returns)) - 1
    volatility = returns.std() * np.sqrt(252)
    sharpe = annualized_return / volatility if volatility != 0 else np.nan

    equity = compute_equity_curve(returns)
    mdd = max_drawdown(equity)

    return {
        "Total Return": total_return,
        "Annualized Return": annualized_return,
        "Volatility": volatility,
        "Sharpe Ratio": sharpe,
        "Max Drawdown": mdd
    }


def moving_average_strategy(
    prices: pd.Series,
    short_window: int = 20,
    long_window: int = 50
) -> dict:
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

    equity = compute_equity_curve(returns)
    mdd = max_drawdown(equity)

    df["Equity"] = compute_equity_curve(df["Strategy_Returns"])

    return {
        "Metrics": {
            "Total Return": total_return,
            "Annualized Return": annualized_return,
            "Volatility": volatility,
            "Sharpe Ratio": sharpe,
            "Max Drawdown": mdd
        },
        "Data": df
    }

def compute_rsi(prices: pd.Series, window: int = 14) -> pd.Series:
    delta = prices.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi

#linear regression

def linear_regression_forecast(
    prices: pd.Series,
    horizon: int = 10,
    confidence: float = 0.95
):
    """
    Linear regression on log-prices with confidence interval.
    """
    y = np.log(prices.values)
    x = np.arange(len(y))

    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

    # Future dates
    x_future = np.arange(len(y), len(y) + horizon)
    y_pred_log = intercept + slope * x_future
    y_pred = np.exp(y_pred_log)

    # Confidence interval
    t_value = stats.t.ppf((1 + confidence) / 2, len(y) - 2)
    residuals = y - (intercept + slope * x)
    sigma = np.sqrt(np.sum(residuals**2) / (len(y) - 2))

    delta = t_value * sigma * np.sqrt(
        1 + 1/len(y) + (x_future - x.mean())**2 / np.sum((x - x.mean())**2)
    )

    lower = np.exp(y_pred_log - delta)
    upper = np.exp(y_pred_log + delta)

    return y_pred, lower, upper
