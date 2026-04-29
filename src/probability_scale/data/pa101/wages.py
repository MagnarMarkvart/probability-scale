"""
PA101: gross wage mean, median, deciles, employee count — PxWeb API.

Statistics Estonia; same JSON-stat2 POST shape as NH21.
"""

from __future__ import annotations

import requests
import pandas as pd

PA101_URL = "https://andmed.stat.ee/api/v1/et/stat/PA101"

# JSON-stat dimension id for indicators (PxWeb metadata).
_DIM_INDICATOR = "Näitaja"

# PxWeb dimension values (API metadata).
ACTIVITY_TOTAL = "TOTAL"

# Näitaja codes (see API variable list).
CODE_MEAN_WAGE = "GR_W_AVG"
CODE_EMPLOYEES = "NR_EMPL"
CODE_DECILES = [f"GR_W_D{i}" for i in range(1, 10)]


def _fetch_json_stat(*, period: str, activity: str = ACTIVITY_TOTAL) -> dict:
    payload = {
        "query": [
            {"code": "Tegevusala", "selection": {"filter": "item", "values": [activity]}},
            {"code": "Vaatlusperiood", "selection": {"filter": "item", "values": [period]}},
        ],
        "response": {"format": "json-stat2"},
    }
    response = requests.post(PA101_URL, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()


def _indicators_from_json_stat(js: dict) -> dict[str, float]:
    """
    Read indicator codes (GR_W_AVG, …) from raw JSON-stat2.

    ``pyjstat`` replaces category ids with Estonian ``valueTexts`` labels; we need
    the machine codes to match PxWeb metadata.
    """
    try:
        idx_map = js["dimension"][_DIM_INDICATOR]["category"]["index"]
        raw = js["value"]
        sizes = js["size"]
    except KeyError as e:
        raise ValueError(f"PA101: unexpected json-stat shape ({e})") from e

    if len(sizes) < 1:
        raise ValueError("PA101: empty json-stat size")

    stride_other = 1
    for s in sizes[1:]:
        stride_other *= int(s)

    out: dict[str, float] = {}
    for code, pos_indicator in idx_map.items():
        linear = int(pos_indicator) * stride_other
        if linear < 0 or linear >= len(raw):
            raise ValueError(f"PA101: index out of range for {code}")
        cell = raw[linear]
        if cell is None:
            raise ValueError(f"PA101: null value for {code}")
        out[str(code)] = float(cell)
    return out


def _cdf_share_at_or_below_wage(wage: float, deciles_d1_to_d9: list[float]) -> float:
    """
    Approximate F(w) = P(W <= wage) using published decile thresholds D1..D9.

    Convention: Dk is treated as the (10*k)-th percentile point, i.e. between
    Dk and D{k+1} lies roughly 10% of employees. Below D1, linear from 0 to 10%;
    above D9, extrapolate the top 10% using the (D8, D9) span (capped below 1).
    """
    d = deciles_d1_to_d9
    if len(d) != 9:
        raise ValueError("PA101: expected nine decile thresholds (D1..D9)")
    if any(x <= 0 for x in d):
        raise ValueError("PA101: decile thresholds must be positive")
    if not all(d[i] < d[i + 1] for i in range(8)):
        raise ValueError("PA101: decile thresholds must be strictly increasing")

    w = float(wage)
    if w <= 0:
        return 0.0
    if w <= d[0]:
        return 0.1 * (w / d[0])

    for k in range(1, 9):
        if w <= d[k]:
            low, high = d[k - 1], d[k]
            return k * 0.1 + (w - low) / (high - low) * 0.1

    span = max(d[8] - d[7], 1.0)
    return float(min(0.999, 0.9 + (w - d[8]) / span * 0.1))


def estimate_share_above_mean_wage(mean_wage: float, deciles_d1_to_d9: list[float]) -> float:
    """Approximate P(W > mean) for the same population as PA101 mean & deciles."""
    cdf_at_mean = _cdf_share_at_or_below_wage(mean_wage, deciles_d1_to_d9)
    return float(round(max(0.0, min(1.0, 1.0 - cdf_at_mean)), 4))


def fetch_share_above_mean_wage_row(
    *,
    period: str | None = None,
    activity: str = ACTIVITY_TOTAL,
) -> pd.DataFrame:
    """
    One table row for the scale: ``probability`` ≈ share of employees with gross
    wage strictly above the national mean (all sectors if ``activity=TOTAL``).

    Tries ``period`` if given; otherwise 2025 then 2024.
    """
    periods = [period] if period else ["2025", "2024"]
    last_error: Exception | None = None
    used: str | None = None
    js: dict | None = None

    for p in periods:
        try:
            js = _fetch_json_stat(period=p, activity=activity)
            used = p
            break
        except requests.HTTPError as e:
            last_error = e

    if js is None or used is None:
        raise RuntimeError("PA101: could not retrieve data") from last_error

    idx = _indicators_from_json_stat(js)
    mean_w = idx[CODE_MEAN_WAGE]
    n_emp = int(idx[CODE_EMPLOYEES])
    deciles = [idx[c] for c in CODE_DECILES]
    prob = estimate_share_above_mean_wage(mean_w, deciles)

    out = pd.DataFrame(
        [
            {
                "Aasta": used,
                "Vaatlusperiood": used,
                "Tegevusala": activity,
                "mean_gross_wage_eur": mean_w,
                "employees": n_emp,
                "value": prob * 100.0,
                "probability": prob,
                "event_label": (
                    f"PA101 ({used}, all NACE sectors): estimated share of employees earning "
                    f"above the national mean gross monthly wage ({mean_w:.0f} €). "
                    "Decile-based linear interpolation (approximate)."
                ),
                "source": "PA101",
            }
        ]
    )
    return out
