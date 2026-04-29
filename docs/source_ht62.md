# HT62 data source (`probability_scale.data.ht62`)

## Table

[HT62 — vocational education programme leavers, by sex, level, and mother tongue](https://andmed.stat.ee/api/v1/et/stat/HT62) (Statistics Estonia, PxWeb).

## Query used here

- **Sugu** `T` — Kokku (both sexes).
- **Õppetase** `FE_ED_VOC` — Kutseharidus kokku (all vocational levels aggregated).
- **Näitaja** `DISC` — Õppekava katkestajad (curriculum leavers / dropouts for this statistic).
- **Emakeel** — `TOTAL`, `EST`, `RUS`, `OTH`, `UNK` in one response.
- **Vaatlusperiood** — e.g. `2025` (fallback `2024` if the request fails).

## What `probability` means

Among counted **vocational dropouts** in that period:

> **Share whose mother tongue is not Estonian**, i.e. **Vene keel** + **Muu** + **Teadmata**, divided by **Emakeel Kokku** (`TOTAL`).

**Eesti keel** is excluded from the numerator; the published **Kokku** row is the denominator. The implementation checks that `EST + RUS + OTH + UNK` matches **Kokku** (within rounding).

## Code

- `probability_scale.data.ht62.fetch_vocational_dropout_non_estonian_share_row()` — HTTP, JSON-stat cell addressing, one `DataFrame` row.
- Implementation: `src/probability_scale/data/ht62/dropouts.py`.

Cell values are read with the JSON-stat linear index from dimension order (same pattern as PA101 / HT309).
