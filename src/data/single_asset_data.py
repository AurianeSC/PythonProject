import pandas as pd


PERIOD_TO_DAYS = {
    "6mo": 183,
    "1y": 365,
    "2y": 730,
    "5y": 1825,
}


def load_price_data(ticker: str, period: str = "1y") -> pd.DataFrame:
    """
    Fetch daily OHLCV from Stooq (free) as CSV.
    ticker example: 'aapl.us', 'msft.us', 'tsla.us'
    """
    t = (ticker or "").strip().lower()
    if not t:
        return pd.DataFrame()

    url = f"https://stooq.com/q/d/l/?s={t}&i=d"
    try:
        df = pd.read_csv(url)
    except Exception:
        return pd.DataFrame()

    if df.empty or "Date" not in df.columns:
        return pd.DataFrame()

    df["Date"] = pd.to_datetime(df["Date"])
    df = df.set_index("Date").sort_index()

    # Keep standard columns if they exist
    keep = [c for c in ["Open", "High", "Low", "Close", "Volume"] if c in df.columns]
    df = df[keep].dropna()

    # Filter by period
    days = PERIOD_TO_DAYS.get(period, 365)
    if len(df) > 0:
        df = df[df.index >= (df.index.max() - pd.Timedelta(days=days))]

    return df
