import io
from typing import List, Dict

import pandas as pd
import requests


ECB_BASE_URL = "https://data-api.ecb.europa.eu/service/data/EXR"
ECB_SERIES_KEY = "D.USD.EUR.SP00.A"


def _detect_column(df: pd.DataFrame, candidates: List[str]) -> str:
    normalized = {col.strip().upper(): col for col in df.columns}

    for candidate in candidates:
        if candidate.upper() in normalized:
            return normalized[candidate.upper()]

    raise ValueError(
        f"Could not detect expected column. Available columns: {list(df.columns)}"
    )


def fetch_currency_rates(start_date: str, end_date: str) -> List[Dict]:
    """
    Fetch daily USD/EUR exchange rates from ECB API for the given period.

    Output format:
    [
        {"date": "2024-01-01", "euro": 0.91},
        {"date": "2024-01-02", "euro": 0.92},
    ]

    Explanation:
    - ECB EXR series D.USD.EUR.SP00.A returns USD against EUR.
    - Task requires final output with usd = 1 and euro = value relative to USD.
    - So we convert:
          1 USD = x EUR
      which is exactly:
          euro = observed USD/EUR rate
    """
    url = (
        f"{ECB_BASE_URL}/{ECB_SERIES_KEY}"
        f"?startPeriod={start_date}&endPeriod={end_date}&format=csvdata"
    )

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    df = pd.read_csv(io.StringIO(response.text))

    date_col = _detect_column(
        df,
        ["TIME_PERIOD", "TIME_PERIOD:OBS_VALUE", "DATE", "TIME_PERIOD "],
    )
    value_col = _detect_column(
        df,
        ["OBS_VALUE", "OBS VALUE", "VALUE", "OBS_VALUE "],
    )

    result_df = df[[date_col, value_col]].copy()
    result_df.columns = ["date", "euro"]

    result_df["date"] = pd.to_datetime(result_df["date"]).dt.strftime("%Y-%m-%d")
    result_df["euro"] = result_df["euro"].astype(float)

    result_df = result_df.sort_values("date").reset_index(drop=True)

    result = result_df.to_dict(orient="records")

    if not result:
        raise ValueError(
            f"No ECB data returned for period start_date={start_date}, end_date={end_date}"
        )

    return result