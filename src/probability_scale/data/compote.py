"""
All scale observations in one combined table.

`pandas.concat` builds a single DataFrame that Plotly can draw in one pass.
"""

from __future__ import annotations

import pandas as pd

from probability_scale.data.ht62 import fetch_vocational_dropout_non_estonian_share_row
from probability_scale.data.ht309 import fetch_non_european_citizens_share_row
from probability_scale.data.nh21 import fetch_women_15_74_unemployment_row
from probability_scale.data.pa101 import fetch_share_above_mean_wage_row
from probability_scale.data.rl21801 import fetch_rl21801_scale_rows


def build_scale_table() -> pd.DataFrame:
    """
    Concatenate every source into one DataFrame.

    Each slice must include at least `probability` and `event_label`. Extra
    columns (e.g. `source`, `value`) are kept and written to the CSV.
    """
    frames: list[pd.DataFrame] = [
        fetch_women_15_74_unemployment_row(None),
        fetch_share_above_mean_wage_row(period=None),
        fetch_non_european_citizens_share_row(year=None),
        fetch_vocational_dropout_non_estonian_share_row(period=None),
        fetch_rl21801_scale_rows(year=None),
    ]
    return pd.concat(frames, ignore_index=True)
