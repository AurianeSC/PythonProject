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
TICKER = "AAPL.US"
OUTPUT_DIR = os.path.join(CURRENT_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

#  MAIN LOGIC 
def main():
    # Load data
    df = pdr.DataReader(TICKER, "stooq").sort_index()

    close = df["Close"]
    returns = close.pct_change().dropna()

    report = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "ticker": TICKER,
        "open": df["Open"].iloc[-1],
        "close": df["Close"].iloc[-1],
        "volatility": returns.std() * np.sqrt(252),
        "max_drawdown": max_drawdown((1 + returns).cumprod())
    }

    report_df = pd.DataFrame([report])

    filename = os.path.join(
        OUTPUT_DIR,
        f"daily_report_{report['date']}.csv"
    )

    report_df.to_csv(filename, index=False)

    print(f"Daily report saved to {filename}")


# ENTRY POINT
if __name__ == "__main__":
    main()
