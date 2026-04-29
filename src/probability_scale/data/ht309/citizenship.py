"""
HT309: students in Estonia by country/territory of residence or citizenship (PxWeb).

This module uses **citizenship** (kodakondsus), not country of residence.

API: https://andmed.stat.ee/api/v1/et/stat/HT309
"""

from __future__ import annotations

import requests
import pandas as pd

HT309_URL = "https://andmed.stat.ee/api/v1/et/stat/HT309"

# PxWeb dimension ids (exact strings from JSON-stat).
_DIM_TERRITORY = "Riik/territoorium*"
_DIM_RES_CIT = "Elukohariik/kodakondsus"
_DIM_YEAR = "Aasta"

# Elukohariik/kodakondsus: Kodakondsus (not Elukohariik).
CITIZENSHIP = "2"

# Riik/territoorium*: official regional subtotals (kokku), excluding duplicate leaf countries.
# Europe total is a single row; do not add "Eesti" + "Euroopa v.a Eesti" separately.
CODE_AFRICA_TOTAL = "1"
CODE_ASIA_TOTAL = "36"
CODE_EUROPE_TOTAL = "81"
CODE_LATIN_AMERICA_CARIB_TOTAL = "123"
CODE_NORTH_AMERICA_TOTAL = "149"
CODE_OCEANIA_TOTAL = "153"
CODE_UNKNOWN = "158"

_CODES_OUTSIDE_EUROPE = [
    CODE_AFRICA_TOTAL,
    CODE_ASIA_TOTAL,
    CODE_LATIN_AMERICA_CARIB_TOTAL,
    CODE_NORTH_AMERICA_TOTAL,
    CODE_OCEANIA_TOTAL,
]


def _fetch_json_stat(*, year: str) -> dict:
    payload = {
        "query": [
            {"code": _DIM_YEAR, "selection": {"filter": "item", "values": [year]}},
            {"code": _DIM_RES_CIT, "selection": {"filter": "item", "values": [CITIZENSHIP]}},
        ],
        "response": {"format": "json-stat2"},
    }
    response = requests.post(HT309_URL, json=payload, timeout=120)
    response.raise_for_status()
    return response.json()


def _cell_by_territory_code(js: dict, territory_code: str) -> float:
    idx_map: dict[str, str | int] = js["dimension"][_DIM_TERRITORY]["category"]["index"]
    raw: list = js["value"]
    sizes: list[int] = js["size"]

    stride = 1
    for s in sizes[1:]:
        stride *= int(s)

    pos = int(idx_map[territory_code])
    linear = pos * stride
    cell = raw[linear]
    if cell is None:
        return 0.0
    return float(cell)


def estimate_share_non_european_citizenship(js: dict) -> tuple[float, float, float, float]:
    """
    Return (count_outside_europe, count_europe, count_unknown, total).

    Outside Europe = sum of continental ``kokku`` rows for Africa, Asia,
    Latin America & Caribbean, North America, and Oceania. Europe = ``Euroopa
    riigid kokku`` (includes Estonian citizens). ``Unknown`` = country
    missing; all three groups sum to ``total``.
    """
    outside = sum(_cell_by_territory_code(js, c) for c in _CODES_OUTSIDE_EUROPE)
    europe = _cell_by_territory_code(js, CODE_EUROPE_TOTAL)
    unknown = _cell_by_territory_code(js, CODE_UNKNOWN)
    total = outside + europe + unknown
    if total <= 0:
        raise ValueError("HT309: total student count is zero or negative")
    prob = outside / total
    return outside, europe, unknown, prob


def fetch_non_european_citizens_share_row(year: str | None = None) -> pd.DataFrame:
    """
    One scale row: ``probability`` = share of students in Estonia (by **citizenship**)
    whose citizenship region is **outside Europe**, for the given academic/reference year.

    Uses only regional ``kokku`` rows from HT309 so individual countries are not double-counted.
    Tries ``year`` if given; otherwise ``2025`` then ``2024``.
    """
    years = [year] if year else ["2025", "2024"]
    last_error: Exception | None = None
    used: str | None = None
    js: dict | None = None

    for y in years:
        try:
            js = _fetch_json_stat(year=y)
            used = y
            break
        except requests.HTTPError as e:
            last_error = e

    if js is None or used is None:
        raise RuntimeError("HT309: could not retrieve data") from last_error

    outside, europe, unknown, prob = estimate_share_non_european_citizenship(js)
    prob_r = round(prob, 4)

    out = pd.DataFrame(
        [
            {
                "Aasta": used,
                "value": prob_r * 100.0,
                "probability": prob_r,
                "students_outside_europe": int(outside),
                "students_europe_citizenship": int(europe),
                "students_citizenship_unknown": int(unknown),
                "students_total": int(outside + europe + unknown),
                "event_label": (
                    f"HT309 ({used}, citizenship / kodakondsus): estimated share of university students in Estonia "
                    f"with non-European citizenship (continental aggregates; {int(outside)} of "
                    f"{int(outside + europe + unknown)} including unknown region)."
                ),
                "source": "HT309",
            }
        ]
    )
    return out
