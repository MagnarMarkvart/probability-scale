"""
Plotly tõenäosusskaala — ainult joonise välimus.

Põhiloogika on moodulis ``probability_scale``. Siit saab importida
peamised funktsioonid ja konstandid lühemalt:

    from plotting import build_figure, write_html
"""

from plotting.probability_scale import (
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
