import os
import sys
from datetime import datetime

import numpy as np
import pandas as pd
from pandas_datareader import data as pdr

# PATH FIX 
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))
sys.path.insert(0, PROJECT_ROOT)

from src.metrics.single_asset_metrics import max_drawdown

# CONFIG 
TICKERS = ["AAPL.US", "MSFT.US", "GOOG.US"]
WEIGHTS = np.array([1/3, 1/3, 1/3])  # equal-weight portfolio

OUTPUT_DIR = os.path.join(CURRENT_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# MAIN LOGIC 
def main():
    prices = {}

    for ticker in TICKERS:
        df = pdr.DataReader(ticker, "stooq").sort_index()
        prices[ticker] = df["Close"]

    price_df = pd.DataFrame(prices).dropna()
    returns = price_df.pct_change().dropna()

    # Portfolio returns
    portfolio_returns = returns.dot(WEIGHTS)

    portfolio_equity = (1 + portfolio_returns).cumprod()

    report = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "assets": ",".join(TICKERS),
        "weights": ",".join([str(round(w, 2)) for w in WEIGHTS]),
        "portfolio_return": portfolio_returns.iloc[-1],
        "volatility": portfolio_returns.std() * np.sqrt(252),
        "max_drawdown": max_drawdown(portfolio_equity)
    }

    report_df = pd.DataFrame([report])

    filename = os.path.join(
        OUTPUT_DIR,
        f"daily_portfolio_report_{report['date']}.csv"
    )

    report_df.to_csv(filename, index=False)

    print(f"Portfolio daily report saved to {filename}")


# ENTRY POINT 
if __name__ == "__main__":
    main()
