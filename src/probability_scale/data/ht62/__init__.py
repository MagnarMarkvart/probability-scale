"""
Statistics Estonia HT62 — vocational programme dropouts by mother tongue.

Use ``fetch_vocational_dropout_non_estonian_share_row`` for a scale-ready row.
"""

from .dropouts import (
    HT62_URL,
    estimate_share_non_estonian_mother_tongue,
    fetch_vocational_dropout_non_estonian_share_row,
)

__all__ = [
    "HT62_URL",
    "estimate_share_non_estonian_mother_tongue",
    "fetch_vocational_dropout_non_estonian_share_row",
]
