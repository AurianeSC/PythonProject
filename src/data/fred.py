import pandas as pd
import requests
from io import StringIO


class DataFetchError(Exception):
    pass


FRED_CSV_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv"


def fetch_series(series_id: str) -> pd.Series:
   
    try:
        r = requests.get(FRED_CSV_URL, params={"id": series_id}, timeout=20)
        if r.status_code == 404:
            raise DataFetchError(f"FRED series not found (404): {series_id}")
        r.raise_for_status()
    except DataFetchError:
        raise
    except Exception as e:
        raise DataFetchError(f"FRED request failed for {series_id}") from e

    df = pd.read_csv(StringIO(r.text))

    date_col = None
    for candidate in ("DATE", "observation_date"):
        if candidate in df.columns:
            date_col = candidate
            break

    if date_col is None:
        first_line = r.text.splitlines()[0] if r.text else ""
        raise DataFetchError(
            f"Unexpected FRED CSV (no date column) for {series_id}. First line: {first_line[:120]}"
        )

    value_col = None
    if series_id in df.columns:
        value_col = series_id
    else:
        for c in df.columns:
            if c != date_col:
                value_col = c
                break

    if value_col is None:
        raise DataFetchError(f"Unexpected FRED CSV (no value col) for {series_id}")

    df[date_col] = pd.to_datetime(df[date_col])
    s = pd.to_numeric(df[value_col], errors="coerce")
    s.index = df[date_col]
    s.name = series_id
    return s.dropna()


def fetch_multi(series_ids: list[str]) -> pd.DataFrame:
    """
    Fetch and align multiple FRED series into a DataFrame.
    """
    frames = [fetch_series(sid) for sid in series_ids]
    return pd.concat(frames, axis=1, join="inner").sort_index()
