import pandas as pd
from pandas_datareader import data as pdr

def load_price_data(ticker: str, period: str = "6mo") -> pd.DataFrame:
    try:
        df = pdr.DataReader(ticker, "stooq")
        df = df.sort_index()

        if df.empty:
            return pd.DataFrame()

        return df[["Close"]]
    except Exception:
        return pd.DataFrame()
