"""
RL21801: population by sex, age, nationality, dwelling type, place — PxWeb.

Reference date **31 December**; table title includes **2021** census-style grid.

API: https://andmed.stat.ee/api/v1/et/stat/RL21801
"""

from __future__ import annotations

import requests
import pandas as pd

RL21801_URL = "https://andmed.stat.ee/api/v1/et/stat/RL21801"

_DIM_AASTA = "Aasta"
_DIM_ELIKOHT = "Elukoht"
_DIM_VANUS = "Vanuserühm"
_DIM_ELURUUMI = "Eluruumi tüüp ja kasutamise alus"
_DIM_SUGU = "Sugu"
_DIM_RAHVUS = "Rahvus"

# Aggregates: whole Estonia, all ages, both sexes.
ELUKOHT_Kogu_Eesti = "1"
VANUSERÜHM_KOKKU = "1"
ELURUUMI_KOKKU = "1"
# PxWeb code for *Tavaeluruum* (child of total dwelling breakdown).
ELURUUMI_TAVAELURUUM = "2"
SUGU_MEHED_JA_NAISED = "0"

RAHVUS_KOKKU = "1"
RAHVUS_EESTLANE = "2"
RAHVUS_VENELANE = "3"
RAHVUS_MUU = "4"
RAHVUS_Teadmata = "5"

_RAHVUS_DETAIL = (RAHVUS_EESTLANE, RAHVUS_VENELANE, RAHVUS_MUU, RAHVUS_Teadmata)


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


def _fetch_nationality_dwelling_slice(*, year: str) -> dict:
    """One request: Eluruumi ∈ {Kokku, Tavaeluruum}, Rahvus ∈ {kokku + all detail}."""
    payload = {
        "query": [
            {"code": _DIM_AASTA, "selection": {"filter": "item", "values": [year]}},
            {"code": _DIM_ELIKOHT, "selection": {"filter": "item", "values": [ELUKOHT_Kogu_Eesti]}},
            {"code": _DIM_VANUS, "selection": {"filter": "item", "values": [VANUSERÜHM_KOKKU]}},
            {
                "code": _DIM_ELURUUMI,
                "selection": {"filter": "item", "values": [ELURUUMI_KOKKU, ELURUUMI_TAVAELURUUM]},
            },
            {"code": _DIM_SUGU, "selection": {"filter": "item", "values": [SUGU_MEHED_JA_NAISED]}},
            {
                "code": _DIM_RAHVUS,
                "selection": {
                    "filter": "item",
                    "values": list({RAHVUS_KOKKU, *_RAHVUS_DETAIL}),
                },
            },
        ],
        "response": {"format": "json-stat2"},
    }
    response = requests.post(RL21801_URL, json=payload, timeout=180)
    response.raise_for_status()
    return response.json()


def estimate_share_ethnic_estonian(js: dict, *, year: str) -> tuple[float, float, float]:
    """Return (count_estonian, total_population, share). Uses Eluruumi *Kokku*."""
    coords_base = {
        _DIM_AASTA: year,
        _DIM_ELIKOHT: ELUKOHT_Kogu_Eesti,
        _DIM_VANUS: VANUSERÜHM_KOKKU,
        _DIM_ELURUUMI: ELURUUMI_KOKKU,
        _DIM_SUGU: SUGU_MEHED_JA_NAISED,
    }

    total = _json_stat_cell(js, {**coords_base, _DIM_RAHVUS: RAHVUS_KOKKU})
    est = _json_stat_cell(js, {**coords_base, _DIM_RAHVUS: RAHVUS_EESTLANE})
    detail_sum = sum(_json_stat_cell(js, {**coords_base, _DIM_RAHVUS: r}) for r in _RAHVUS_DETAIL)
    if total <= 0:
        raise ValueError("RL21801: total population is zero or negative")
    if abs(detail_sum - total) > 0.5:
        raise ValueError(f"RL21801: nationality parts ({detail_sum}) != total ({total})")
    return est, total, est / total


def estimate_share_conventional_dwelling(js: dict, *, year: str) -> tuple[float, float, float]:
    """Return (count_tavaeluruum, total_with_dwelling_kokku, share). Uses Rahvus *Kokku*."""
    coords = {
        _DIM_AASTA: year,
        _DIM_ELIKOHT: ELUKOHT_Kogu_Eesti,
        _DIM_VANUS: VANUSERÜHM_KOKKU,
        _DIM_SUGU: SUGU_MEHED_JA_NAISED,
        _DIM_RAHVUS: RAHVUS_KOKKU,
    }
    koku = _json_stat_cell(js, {**coords, _DIM_ELURUUMI: ELURUUMI_KOKKU})
    tava = _json_stat_cell(js, {**coords, _DIM_ELURUUMI: ELURUUMI_TAVAELURUUM})
    if koku <= 0:
        raise ValueError("RL21801: total population (dwelling Kokku) is zero or negative")
    if tava > koku + 0.5:
        raise ValueError(f"RL21801: Tavaeluruum count ({tava}) exceeds dwelling total ({koku})")
    return tava, koku, tava / koku


def fetch_rl21801_scale_rows(year: str | None = None) -> pd.DataFrame:
    """
    Multiple scale rows from the same **2021** RL21801 slice (31 Dec definitions):

    1. Share with recorded nationality **Eestlane** (Eluruumi Kokku).
    2. Share in **Tavaeluruum** vs Eluruumi **Kokku** (Rahvused kokku; ~0.98 in 2021).
    """
    y = year or "2021"
    js = _fetch_nationality_dwelling_slice(year=y)

    est, total_nat, p_nat = estimate_share_ethnic_estonian(js, year=y)
    tava, total_dw, p_dw = estimate_share_conventional_dwelling(js, year=y)
    if abs(total_nat - total_dw) > 0.5:
        raise ValueError(
            f"RL21801: population total mismatch nationality ({total_nat}) vs dwelling ({total_dw})"
        )

    p_nat_r = round(p_nat, 4)
    p_dw_r = round(p_dw, 4)

    return pd.DataFrame(
        [
            {
                "Aasta": y,
                "value": p_nat_r * 100.0,
                "probability": p_nat_r,
                "population_estonian_ethnicity": int(est),
                "population_total": int(total_nat),
                "event_label": (
                    f"Census-style population ({y}, end of year): if you picked a person at random "
                    f"from the whole-country total (all ages, both sexes), this is roughly the chance "
                    f"they are counted as ethnic Estonian in the statistics—not the same as citizenship. "
                    f"About {int(est):,} out of {int(total_nat):,} people."
                ),
                "source": "RL21801",
                "rl21801_metric": "nationality_estonian",
            },
            {
                "Aasta": y,
                "value": p_dw_r * 100.0,
                "probability": p_dw_r,
                "population_tavaeluruum": int(tava),
                "population_dwelling_kokku": int(total_dw),
                "event_label": (
                    f"Same {y} population snapshot: most people live in ordinary housing (a standard "
                    f"house or flat in the stats, not dorms, homelessness, or odd edge categories). "
                    f"This point is that share—about {int(tava):,} in every {int(total_dw):,} counted people "
                    f"nationwide, all ages, both sexes."
                ),
                "source": "RL21801",
                "rl21801_metric": "dwelling_tavaeluruum",
            },
        ]
    )


# Backwards-compatible name (returns two rows).
fetch_ethnic_estonian_share_row = fetch_rl21801_scale_rows
