"""
HT62: vocational programme leavers / dropouts by sex, level, mother tongue (PxWeb).

API: https://andmed.stat.ee/api/v1/et/stat/HT62
"""

from __future__ import annotations

import requests
import pandas as pd

HT62_URL = "https://andmed.stat.ee/api/v1/et/stat/HT62"

_DIM_SUGU = "Sugu"
_DIM_OPPETASE = "Õppetase"
_DIM_EMAKEEL = "Emakeel"
_DIM_NAITAJA = "Näitaja"
_DIM_PERIOD = "Vaatlusperiood"

# Filters: total sex, total vocational, indicator = curriculum leavers.
SUGU_KOKKU = "T"
OPPETASE_KUTSE_KOKKU = "FE_ED_VOC"
NAITAJA_KATKESTAJAD = "DISC"

EMAKEEL_KOKKU = "TOTAL"
EMAKEEL_EESTI = "EST"
EMAKEEL_NON_EST = ("RUS", "OTH", "UNK")  # Vene, Muu, Teadmata


def _json_stat_cell(js: dict, coords: dict[str, str]) -> float:
    dim_ids: list[str] = js["id"]
    sizes: list[int] = js["size"]
    linear = 0
    for i, dim_id in enumerate(dim_ids):
        code = coords[dim_id]
        pos = int(js["dimension"][dim_id]["category"]["index"][code])
        stride = 1
        for s in sizes[i + 1 :]:
            stride *= int(s)
        linear += pos * stride
    v = js["value"][linear]
    if v is None:
        return 0.0
    return float(v)


def _fetch_json_stat(*, period: str) -> dict:
    payload = {
        "query": [
            {"code": _DIM_SUGU, "selection": {"filter": "item", "values": [SUGU_KOKKU]}},
            {"code": _DIM_OPPETASE, "selection": {"filter": "item", "values": [OPPETASE_KUTSE_KOKKU]}},
            {
                "code": _DIM_EMAKEEL,
                "selection": {
                    "filter": "item",
                    "values": list({EMAKEEL_KOKKU, EMAKEEL_EESTI, *EMAKEEL_NON_EST}),
                },
            },
            {"code": _DIM_NAITAJA, "selection": {"filter": "item", "values": [NAITAJA_KATKESTAJAD]}},
            {"code": _DIM_PERIOD, "selection": {"filter": "item", "values": [period]}},
        ],
        "response": {"format": "json-stat2"},
    }
    response = requests.post(HT62_URL, json=payload, timeout=120)
    response.raise_for_status()
    return response.json()


def estimate_share_non_estonian_mother_tongue(js: dict, *, period: str) -> tuple[float, float, float, float]:
    """
    Return (count_non_est, count_est, total, probability).

    Non-Estonian mother tongue = RUS + OTH + UNK; total = Emakeel Kokku (TOTAL).
    """
    base = {
        _DIM_SUGU: SUGU_KOKKU,
        _DIM_OPPETASE: OPPETASE_KUTSE_KOKKU,
        _DIM_NAITAJA: NAITAJA_KATKESTAJAD,
        _DIM_PERIOD: period,
    }
    total = _json_stat_cell(js, {**base, _DIM_EMAKEEL: EMAKEEL_KOKKU})
    est = _json_stat_cell(js, {**base, _DIM_EMAKEEL: EMAKEEL_EESTI})
    non_est = sum(_json_stat_cell(js, {**base, _DIM_EMAKEEL: c}) for c in EMAKEEL_NON_EST)
    if total <= 0:
        raise ValueError("HT62: total dropouts is zero or negative")
    chk = est + non_est
    if abs(chk - total) > 0.5:  # allow tiny rounding
        raise ValueError(f"HT62: Estonian + non-Estonian ({chk}) != total ({total})")
    return non_est, est, total, non_est / total


def fetch_vocational_dropout_non_estonian_share_row(period: str | None = None) -> pd.DataFrame:
    """
    One scale row: among vocational **curriculum leavers** in period, share whose
    **mother tongue is not Estonian** (Russian, other, unknown).
    """
    periods = [period] if period else ["2025", "2024"]
    last_error: Exception | None = None
    used: str | None = None
    js: dict | None = None

    for p in periods:
        try:
            js = _fetch_json_stat(period=p)
            used = p
            break
        except requests.HTTPError as e:
            last_error = e

    if js is None or used is None:
        raise RuntimeError("HT62: could not retrieve data") from last_error

    non_est, est, total, prob = estimate_share_non_estonian_mother_tongue(js, period=used)
    prob_r = round(prob, 4)

    out = pd.DataFrame(
        [
            {
                "Aasta": used,
                "Vaatlusperiood": used,
                "value": prob_r * 100.0,
                "probability": prob_r,
                "dropouts_non_estonian_mt": int(non_est),
                "dropouts_estonian_mt": int(est),
                "dropouts_total": int(total),
                "event_label": (
                    f"HT62 ({used}, vocational total, sex total): share of curriculum leavers whose "
                    f"mother tongue is not Estonian (Russian + other + unknown; {int(non_est)} of "
                    f"{int(total)})."
                ),
                "source": "HT62",
            }
        ]
    )
    return out
