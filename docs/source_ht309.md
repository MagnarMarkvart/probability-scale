# HT309 data source (`probability_scale.data.ht309`)

## Table

[HT309 — students by country/territory; residence vs citizenship](https://andmed.stat.ee/api/v1/et/stat/HT309) (Statistics Estonia, PxWeb).

## Query used here

- **Aasta** — e.g. `2025` (fallback `2024` if needed).
- **Elukohariik/kodakondsus** = **`2`** = **Kodakondsus** (citizenship).  
  We **do not** use *Elukohariik* (`1`).

## What `probability` means

Given a randomly chosen student counted in HT309 under **citizenship** for that year:

> **Share whose citizenship is attributed to a world region *outside* Europe**, using only the published **continental subtotal** rows (`… riigid kokku`), so countries are **not** double-counted.

Europe is taken as **one** row: **Euroopa riigid kokku** (includes Estonian citizens).  
**Riik või territoorium teadmata** is included in the **denominator** only (added to Europe + non-Europe continental sums).

So:

`P ≈ (Aafrika kokku + Aasia kokku + L-Ameerika kokku + P-Ameerika kokku + Okeaania kokku) / (non-Europe + Euroopa kokku + teadmata)`

## Why not sum every country row?

The table mixes **regional totals** and **individual countries**. Summing both would **double-count**. The implementation sums **five non-European continental totals** plus **Euroopa riigid kokku** and **unknown**.

## Code

- `probability_scale.data.ht309.fetch_non_european_citizens_share_row()` — HTTP, parse, build one `DataFrame` row (`probability`, `event_label`, counts).
- Implementation: `src/probability_scale/data/ht309/citizenship.py` (territory codes `1`, `36`, `81`, …).

Parsing uses JSON-stat cell indexing (same idea as PA101), not label-based `pyjstat` rows for the aggregation step.
