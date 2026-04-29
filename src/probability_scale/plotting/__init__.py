"""
Plotly probability scale — chart appearance and layout.

Main helpers live in ``probability_scale.plotting.probability_scale``:

    from probability_scale.plotting import build_figure, write_html
"""

from .probability_scale import (
    FIGURE_TITLE,
    MARKER,
    TICK_LABELS,
    TICK_VALUES,
    X_AXIS_TITLE,
    build_figure,
    write_html,
    x_axis_config,
)

__all__ = [
    "FIGURE_TITLE",
    "MARKER",
    "TICK_LABELS",
    "TICK_VALUES",
    "X_AXIS_TITLE",
    "build_figure",
    "write_html",
    "x_axis_config",
]
