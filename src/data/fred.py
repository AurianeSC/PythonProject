import os
from datetime import date
from typing import Optional

import pandas as pd
import requests


class DataFetchError(Exception):
    pass


FRED_API_BASE = "https://api.stlouisfed.org/fred"
FRED_OBS_URL = f"{FRED_API_BASE}/series/observations"


def _get_api_key() -> str:
    k = os.getenv("FRED_API_KEY")
    if not k:
        raise DataFetchError("Missing FRED_API_KEY environment variable.")
    return k


def fetch_series(series_id: str, start: Optional[date] = None, end: Optional[date] = None) -> pd.Series:
    """
    Fetch one FRED series using the official API.
    Returns a pandas Series indexed by date.
    """
    api_key = _get_api_key()

    params = {
        "api_key": api_key,
        "file_type": "json",
        "series_id": series_id,
    }
    if start:
        params["observation_start"] = start.isoformat()
    if end:
        params["observation_end"] = end.isoformat()

    try:
        r = requests.get(FRED_OBS_URL, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        raise DataFetchError(f"FRED request failed for {series_id}: {e}") from e

    obs = data.get("observations", [])
    if not obs:
        raise DataFetchError(f"No observations returned for {series_id}")

    df = pd.DataFrame(obs)
    # df has columns: date, value, realtime_start, realtime_end, ...
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")  # '.' -> NaN
    s = df.set_index("date")["value"].dropna()
    s.name = series_id
    return s


def fetch_multi(series_ids: list[str], start: Optional[date] = None, end: Optional[date] = None) -> pd.DataFrame:
    """
    Fetch and align multiple FRED series into a DataFrame (inner join on dates).
    """
    frames = [fetch_series(sid, start=start, end=end) for sid in series_ids]
    return pd.concat(frames, axis=1, join="inner").sort_index()
