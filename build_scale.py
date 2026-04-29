"""
Run from the project root (after ``pip install -e .``):

    python build_scale.py

Pipeline: ``probability_scale.data`` (API → DataFrame) → ``compote`` (one table)
→ ``probability_scale.plotting`` (Plotly HTML).
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output"


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except OSError:
            pass

    from probability_scale.data.compote import build_scale_table
    from probability_scale.plotting import build_figure, write_html

    import pandas as pd

    table = build_scale_table()

    year_cols = [c for c in ("Aasta", "Vaatlusperiood") if c in table.columns]
    year = str(max(table[c].astype(str).max() for c in year_cols)) if year_cols else "output"

    for _, row in table.iterrows():
        src = row.get("source", "?")
        tag = (
            f" [{row['rl21801_metric']}]"
            if "rl21801_metric" in row.index and pd.notna(row["rl21801_metric"])
            else ""
        )
        prob = float(row["probability"])
        extra = f" value={row['value']}" if "value" in row and pd.notna(row["value"]) else ""
        print(f"{src}{tag}: probability={prob}{extra}")
    table_path = OUTPUT_DIR / f"scale_table_{year}.csv"
    table.to_csv(table_path, index=False, encoding="utf-8")
    print(f"Saved: {table_path}")

    fig = build_figure(table)
    html_path = OUTPUT_DIR / f"probability_scale_{year}.html"
    write_html(fig, html_path)
    print(f"Saved: {html_path}")
    print("Tip: change the Python sources to adjust the chart; avoid editing the generated HTML.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
