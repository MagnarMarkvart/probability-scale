"""
Statistics Estonia HT309 — students by residence country vs citizenship.

Use ``fetch_non_european_citizens_share_row`` for a scale-ready probability
(P(non-European citizenship | student in Estonia)).
"""

from .citizenship import (
    HT309_URL,
    estimate_share_non_european_citizenship,
    fetch_non_european_citizens_share_row,
)

__all__ = [
    "HT309_URL",
    "estimate_share_non_european_citizenship",
    "fetch_non_european_citizens_share_row",
]
