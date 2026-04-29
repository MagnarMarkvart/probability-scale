# RL21801 data source (`probability_scale.data.rl21801`)

## Table

[RL21801 — population by sex, age group, nationality, dwelling type and tenure, place of residence, 31 December](https://andmed.stat.ee/api/v1/et/stat/RL21801) (Statistics Estonia). The published edition used here is centred on **2021**.

## Indicators (one HTTP request, two scale rows)

`fetch_rl21801_scale_rows()` pulls a **single PxWeb slice** (Eluruumi = *Kokku* + *Tavaeluruum*, Rahvus = kokku + detail) and builds **two** probabilities:

### 1. Nationality — ~0.69

**Share with recorded nationality “Eestlane”** among *Rahvused kokku*, holding:

- **Elukoht** — *Kogu Eesti*  
- **Vanuserühm** — *Vanuserühmad kokku*  
- **Eluruumi** — *Kokku*  
- **Sugu** — *Mehed ja naised*  

Checks: **Eestlane + Venelane + Muud + Teadmata** = **Rahvused kokku**.

### 2. Dwelling — ~0.98 (≥ 0.8)

**Share in *Tavaeluruum*** (conventional dwelling) among everyone counted under **Eluruumi *Kokku***, with **Rahvused kokku** and the same geography / age / sex aggregates. Uses official subtotal **Tavaeluruum** vs total **Kokku**; does **not** add finer subcategories (eramu / korter…) to avoid double-counting.

### Row metadata

Each output row has `source: RL21801` and `rl21801_metric`: `nationality_estonian` or `dwelling_tavaeluruum`.

## Code

- `probability_scale.data.rl21801.fetch_rl21801_scale_rows()` — default year `2021`.  
- `fetch_ethnic_estonian_share_row` is an alias for the same function (two rows).  
- Implementation: `src/probability_scale/data/rl21801/ethnicity.py`.

JSON-stat addressing uses the same linear-index pattern as HT62 / HT309.
