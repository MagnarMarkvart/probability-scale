"""
Statistics Estonia NH21 — PxWeb API.

Returns a DataFrame with at least `probability` and `event_label` so rows can be
merged with other sources and plotted on one scale.

API: https://andmed.stat.ee/api/v1/et/stat/NH21
"""

from __future__ import annotations

import requests
import pandas as pd
from pyjstat import pyjstat

NH21_URL = "https://andmed.stat.ee/api/v1/et/stat/NH21"

# API uses Estonian dimension codes; values below are NH21 category ids.
INDICATOR_UNEMPLOYMENT_RATE = "1"
AGE_GROUP_15_74 = "4"
SEX_FEMALE = "3"


def _fetch_json_stat(year: str) -> dict:
    payload = {
        "query": [
            {"code": "Aasta", "selection": {"filter": "item", "values": [year]}},
            {"code": "Näitaja", "selection": {"filter": "item", "values": [INDICATOR_UNEMPLOYMENT_RATE]}},
            {"code": "Vanuserühm", "selection": {"filter": "item", "values": [AGE_GROUP_15_74]}},
            {"code": "Sugu", "selection": {"filter": "item", "values": [SEX_FEMALE]}},
        ],
        "response": {"format": "json-stat2"},
    }
    response = requests.post(NH21_URL, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()


def _json_stat_to_dataframe(js: dict) -> pd.DataFrame:
    frames = pyjstat.from_json_stat(js)
    if not frames:
        raise ValueError("Empty json-stat response")
    return frames[0]


def fetch_women_15_74_unemployment_row(year: str | None = None) -> pd.DataFrame:
    """
    Fetch one row: female working-age (15–74) unemployment share among the labour force (%).

    If ``year`` is None, try 2025 then 2024.
    Adds ``source`` = ``'NH21'`` so the merged table can tell rows apart.
    """
    years_to_try = [year] if year else ["2025", "2024"]
    last_error: Exception | None = None
    used_year: str | None = None
    js: dict | None = None

    for y in years_to_try:
        try:
            js = _fetch_json_stat(y)
            used_year = y
            break
        except requests.HTTPError as e:
            last_error = e

    if js is None or used_year is None:
        raise RuntimeError("NH21: could not retrieve data") from last_error

    raw = _json_stat_to_dataframe(js)
    if len(raw) != 1:
        raise ValueError(f"NH21: expected 1 row, got {len(raw)}")

    out = raw.copy()
    out["value"] = pd.to_numeric(out["value"], errors="coerce")
    if out["value"].isna().any():
        raise ValueError("NH21: missing numeric value")
    out["probability"] = (out["value"] / 100.0).round(4)
    out["event_label"] = (
        f"Women of working age (15–74) in the labour force: share unemployed (NH21, {used_year}). "
        "On the scale: approximate probability / share as a decimal."
    )
    out["source"] = "NH21"
    return out
