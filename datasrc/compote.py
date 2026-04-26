"""
Kõik skaala-andmed ühes tabelis.

Hiljem: lisa siia uusi `datasrc.*` importe ja pane need `frames` listi —
`pandas.concat` teeb ühe DataFrame'i (kompoti), mida Plotly korraga joonistab.
"""

from __future__ import annotations

import pandas as pd

from datasrc import nh21


def build_scale_table() -> pd.DataFrame:
    """
    Liidab kõik allikad üheks DataFrame'iks.

    Eeldus: iga osa sisaldab vähemalt veerge `probability` ja `event_label`
    (ja võib sisaldada lisa veerge, nt `source`, `value` — need jäävad CSV-sse).
    """
    frames: list[pd.DataFrame] = [
        nh21.fetch_women_15_74_unemployment_row(None),
    ]
    return pd.concat(frames, ignore_index=True)
