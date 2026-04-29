# NH21 data source (`probability_scale.data.nh21`)

## What the API call does

A **POST** to [NH21](https://andmed.stat.ee/api/v1/et/stat/NH21) with **JSON-stat2** returns a slice of Statistics Estonia **labour-force style** statistics. This project uses a fixed filter:

- **Näitaja** — unemployment rate (PxWeb category id `1`).
- **Vanuserühm** — 15–74 (`4`).
- **Sugu** — women (`3`).
- **Aasta** — e.g. `2025`, with fallback to `2024` if the year is not available.

The PxWeb table defines the exact population; see Statistikaamet methodology for NH21.

## What `probability` means on the scale

The published indicator is an **unemployment rate in percent** (share of unemployed in the labour force for that slice). On the scale we store:

`probability = rate / 100`

So the point answers: *“About what share (0–1) of this group is unemployed?”* — same number as the official **percentage**, expressed as a **decimal** for the 0–1 axis.

## Parsing

The response is read with **`pyjstat`** into a small `DataFrame`. This table is filtered to one indicator, so category labels and shape stay stable; there is no PA101-style code vs `valueTexts` issue for this slice.

## Code entry point

- `probability_scale.data.nh21.fetch_women_15_74_unemployment_row()` — HTTP fetch, parse, map **% → probability** → one row with `event_label`, `source='NH21'`.

Implementation: `src/probability_scale/data/nh21/labour.py`.
