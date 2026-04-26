"""
Statistikaamet NH21 — PxWeb API.

Tagastab DataFrame'i, kus on vähemalt veerud `probability` ja `event_label`,
et seda saaks liita teiste allikatega ja plotida ühel skaalal.

API: https://andmed.stat.ee/api/v1/et/stat/NH21
"""

from __future__ import annotations

import requests
import pandas as pd
from pyjstat import pyjstat

NH21_URL = "https://andmed.stat.ee/api/v1/et/stat/NH21"

NÄITAJA_TÖÖTUSE_MÄÄR = "1"
VANUSERÜHM_15_74 = "4"
SUGU_NAISED = "3"


def _fetch_json_stat(year: str) -> dict:
    payload = {
        "query": [
            {"code": "Aasta", "selection": {"filter": "item", "values": [year]}},
            {"code": "Näitaja", "selection": {"filter": "item", "values": [NÄITAJA_TÖÖTUSE_MÄÄR]}},
            {"code": "Vanuserühm", "selection": {"filter": "item", "values": [VANUSERÜHM_15_74]}},
            {"code": "Sugu", "selection": {"filter": "item", "values": [SUGU_NAISED]}},
        ],
        "response": {"format": "json-stat2"},
    }
    response = requests.post(NH21_URL, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()


def _json_stat_to_dataframe(js: dict) -> pd.DataFrame:
    frames = pyjstat.from_json_stat(js)
    if not frames:
        raise ValueError("Tühi json-stat vastus")
    return frames[0]


def fetch_women_15_74_unemployment_row(year: str | None = None) -> pd.DataFrame:
    """
    Tõmba üks rida: tööjõus olevate tööealiste naiste (15–74) töötuse osakaal (%).

    Kui year on None, proovitakse 2025, siis 2024.
    Tagastatud DataFrame'il on täiendavalt `source` = 'NH21', et kompotis eristada.
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
        raise RuntimeError("NH21: ei saanud andmeid") from last_error

    raw = _json_stat_to_dataframe(js)
    if len(raw) != 1:
        raise ValueError(f"NH21: ootasin 1 rida, sain {len(raw)}")

    out = raw.copy()
    out["value"] = pd.to_numeric(out["value"], errors="coerce")
    if out["value"].isna().any():
        raise ValueError("NH21: puudub arvuline value")
    out["probability"] = (out["value"] / 100.0).round(4)
    out["event_label"] = (
        f"Tööealised naised (15–74): töötute osakaal tööjõus (NH21, {used_year}). "
        "Skaalal: hinnanguline tõenäosus / osakaal kümnendarvuna."
    )
    out["source"] = "NH21"
    return out
