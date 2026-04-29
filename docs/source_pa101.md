# PA101 data source (`probability_scale.data.pa101`)

## What the API call does

A **POST** to [PA101](https://andmed.stat.ee/api/v1/et/stat/PA101) with **JSON-stat2** asks Statistics Estonia for **annual wage statistics**:

- **Tegevusala** `TOTAL` — all activity sections combined.
- **Vaatlusperiood** — e.g. `2025`.

The response is **long format**: one row per **Näitaja** (indicator), including mean gross wage, employee count, decile thresholds **D1…D9**, and related fields.

## What `probability` means on the scale

The scale expects `probability` ∈ [0, 1]. For PA101 we set:

> **Estimated share of employees (same scope as the table) whose gross monthly wage is strictly greater than the published national mean wage.**

So it answers: *“If I pick a payroll employee at random from this PA101 population, about what fraction earn **more** than the **mean**?”*

It is **not** the chance that someone earns more than the **median** (that would be 0.5 by definition of the median in a continuous model).

## How the estimate is computed

Official tables give **D1…D9** (decile boundary wages) and the **arithmetic mean**. They do **not** publish “% above mean” directly.

We therefore approximate the cumulative share **at or below** the mean using **piecewise linear interpolation** between decile thresholds:

- **D1** is treated as the **10th** percentile point, …, **D9** as the **90th** (roughly 10% of employees between consecutive deciles).
- Below **D1**, linear ramp from 0% to 10%.
- Above **D9**, the top 10% is extrapolated using the span **D9 − D8** (capped so the CDF stays below 1).

Then:

`share_above_mean ≈ 1 − F(mean_wage)`

Rounded to 4 decimals. This is a **transparent approximation**, not a published official figure; wording in `event_label` states that.

## Naming / labelling

A short title you can use in reports:

**“Estimated share of employees above the national mean wage (PA101)”**

Longer (already used in `event_label`): includes year, “all NACE sectors”, mean wage in €, and “decile-based linear interpolation”.

## Code entry point

- `probability_scale.data.pa101.fetch_share_above_mean_wage_row()` — HTTP fetch + parsing + estimate → one `DataFrame` row with `probability`, `event_label`, `source`.

See `src/probability_scale/data/pa101/wages.py` for constants (`GR_W_AVG`, `GR_W_D1`, …) matching the API metadata.

Parsing uses the raw JSON-stat2 `value` array and `dimension.Näitaja.category.index` (not `pyjstat` for this table), because `pyjstat` substitutes Estonian `valueTexts` for category ids and breaks lookups by code like `GR_W_AVG`.
