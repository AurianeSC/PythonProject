import pandas as pd
from pandas_datareader import data as pdr


def load_price_data(
    ticker: str,
    period: str = "6mo",
    short_ma: int = 20,
    long_ma: int = 50
) -> pd.DataFrame:

    try:
        df = pdr.DataReader(ticker, "stooq")
        df = df.sort_index()

        if df.empty:
            return pd.DataFrame()

        # Moving averages
        df["MA_Short"] = df["Close"].rolling(short_ma).mean()
        df["MA_Long"] = df["Close"].rolling(long_ma).mean()

        # Trading signals
        df["signal"] = 0
        df.loc[df["MA_Short"] > df["MA_Long"], "signal"] = 1
        df["position"] = df["signal"].diff()

        return df

    except Exception:
        return pd.DataFrame()
