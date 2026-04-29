"""
Statistics Estonia RL21801 — population census grid (nationality + dwelling).

Use ``fetch_rl21801_scale_rows`` for two scale metrics from one API request.
"""

from .ethnicity import (
    RL21801_URL,
    estimate_share_conventional_dwelling,
    estimate_share_ethnic_estonian,
    fetch_ethnic_estonian_share_row,
    fetch_rl21801_scale_rows,
)

__all__ = [
    "RL21801_URL",
    "estimate_share_conventional_dwelling",
    "estimate_share_ethnic_estonian",
    "fetch_ethnic_estonian_share_row",
    "fetch_rl21801_scale_rows",
]
