import os
import requests


class FredSearchError(Exception):
    pass


FRED_API_BASE = "https://api.stlouisfed.org/fred"
FRED_SEARCH_URL = f"{FRED_API_BASE}/series/search"


def _get_api_key() -> str:
    k = os.getenv("FRED_API_KEY")
    if not k:
        raise FredSearchError("Missing FRED_API_KEY environment variable.")
    return k


def search_series(query: str, limit: int = 15) -> list[dict]:
    """
    Search FRED series by keyword.
    Returns a list of dicts with keys like: id, title, frequency, units, ...
    """
    api_key = _get_api_key()

    params = {
        "api_key": api_key,
        "file_type": "json",
        "search_text": query,
        "limit": int(limit),
        "order_by": "search_rank",
        "sort_order": "desc",
    }

    try:
        r = requests.get(FRED_SEARCH_URL, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        raise FredSearchError(f"Search request failed: {e}") from e

    return data.get("seriess", [])
