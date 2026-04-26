"""
Käivita projekti juurest:

    python build_scale.py

Voog: datasrc (API → DataFrame) → compote (üks tabel) → plotting (Plotly HTML).
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

    from datasrc.compote import build_scale_table
    from plotting.probability_scale import build_figure, write_html

    table = build_scale_table()
    year = str(table["Aasta"].iloc[0])
    pct = float(table["value"].iloc[0])
    prob = float(table["probability"].iloc[0])
    print(f"Kompotis ({year}): {pct}% → tõenäosus: {prob}")
    table_path = OUTPUT_DIR / f"scale_table_{year}.csv"
    table.to_csv(table_path, index=False, encoding="utf-8")
    print(f"Salvestatud: {table_path}")

    fig = build_figure(table)
    html_path = OUTPUT_DIR / f"probability_scale_{year}.html"
    write_html(fig, html_path)
    print(f"Salvestatud: {html_path}")
    print("Juhend: docs/plotly_juhend.md (muuda Python faile, mitte HTML-i)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
