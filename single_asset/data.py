import pandas as pd
from pandas_datareader import data as pdr
from datetime import timedelta


def load_price_data(ticker: str, period: str = "6mo") -> pd.DataFrame:
    """
    Load historical price data from Stooq and filter by period.
    """
    try:
        df = pdr.DataReader(ticker, "stooq").sort_index()

        if df.empty:
            return pd.DataFrame()

        end_date = df.index.max()

        if period == "6mo":
            start_date = end_date - timedelta(days=180)
        elif period == "1y":
            start_date = end_date - timedelta(days=365)
        elif period == "2y":
            start_date = end_date - timedelta(days=730)
        elif period == "5y":
            start_date = end_date - timedelta(days=1825)
        else:
            start_date = df.index.min()

        return df.loc[start_date:end_date]

    except Exception:
        return pd.DataFrame()
