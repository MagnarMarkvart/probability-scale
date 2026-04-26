"""
Tõenäosusskaala — Plotly seadistus ja joonis.

MUUDA SIIN: telje sildid, värvid, pealkiri, markerite suurus.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# 1) X-telg: vahemik ja sildid
# ---------------------------------------------------------------------------

X_AXIS_TITLE = "Tõenäosus"

# tickvals = mis kohtadel joonisel „nööbid“; ticktext = mis teksti näidatakse
TICK_VALUES = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
TICK_LABELS = [
    "0",
    "0.1",
    "0.2",
    "0.3",
    "0.4",
    "0.5",
    "0.6",
    "0.7",
    "0.8",
    "0.9",
    "1",
]

FIGURE_TITLE = "Tõenäosusskaala"

MARKER = dict(size=22, color="#1f5f8b", line=dict(width=2, color="white"))

# ---------------------------------------------------------------------------
# 2) Abifunktsioonid
# ---------------------------------------------------------------------------


def _require_columns(df: pd.DataFrame) -> None:
    missing = {"probability", "event_label"} - set(df.columns)
    if missing:
        raise ValueError(f"DataFrame'il puuduvad veerud: {sorted(missing)}")


def x_axis_config() -> dict:
    """Tagastab Plotly xaxis sõnastiku — kasutatakse `update_layout(xaxis=...)` sees."""
    return dict(
        title=dict(text=X_AXIS_TITLE),
        range=[0, 1],
        tickmode="array",
        tickvals=list(TICK_VALUES),
        ticktext=list(TICK_LABELS),
        showgrid=True,
        zeroline=True,
        zerolinewidth=1,
    )


def build_figure(df: pd.DataFrame) -> go.Figure:
    """Üks või mitu punkti: iga rida = üks marker x = probability."""
    _require_columns(df)
    probs = df["probability"].astype(float)
    if ((probs < 0) | (probs > 1)).any():
        raise ValueError("Mõni `probability` jääb väljapoole [0, 1]")

    labels = df["event_label"].astype(str)
    xs = probs.tolist()
    ys = [0] * len(df)
    customdata = [[float(p), str(lab)] for p, lab in zip(probs, labels)]

    fig = go.Figure(
        data=[
            go.Scatter(
                x=xs,
                y=ys,
                mode="markers",
                marker=MARKER,
                customdata=customdata,
                hovertemplate=(
                    "<b>Tõenäosus</b> (kümnend): %{customdata[0]:.4f}<br>"
                    "%{customdata[1]}<extra></extra>"
                ),
            )
        ]
    )

    fig.update_layout(
        title=FIGURE_TITLE,
        xaxis=x_axis_config(),
        yaxis=dict(
            visible=False,
            showticklabels=False,
            showgrid=False,
            zeroline=False,
            range=[-0.35, 0.35],
            fixedrange=True,
        ),
        margin=dict(l=20, r=20, t=56, b=56),
        showlegend=False,
        hovermode="closest",
    )
    return fig


def write_html(fig: go.Figure, path: str | "Path", *, include_plotlyjs: str = "cdn") -> None:
    """Salvestab interaktiivse HTML-i. `include_plotlyjs='cdn'` = väiksem fail (vajab netti)."""
    from pathlib import Path

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(p, include_plotlyjs=include_plotlyjs, full_html=True)
