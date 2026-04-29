"""
Statistics Estonia PA101 — wages (mean, deciles, headcount).

Use ``fetch_share_above_mean_wage_row`` for a scale-ready row with ``probability``.
"""

from .wages import (
    PA101_URL,
    estimate_share_above_mean_wage,
    fetch_share_above_mean_wage_row,
)

__all__ = [
    "PA101_URL",
    "estimate_share_above_mean_wage",
    "fetch_share_above_mean_wage_row",
]
