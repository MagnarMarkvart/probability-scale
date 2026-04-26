# AI "dummy guide" of the entire task.

## Probability scale — step-by-step guide

This repository is for the **RMK data team internship challenge**: build a _probability scale_ — a curated list of real-world events with numeric probabilities, plus code and a chart so others can build intuition for numbers like `0.4` vs `0.004`.

Full official wording lives in [`test_challenge.md`](test_challenge.md). This README is a **learning roadmap**: what to do, in what order, and _why_ each step matters.

---

### 0. What you are actually building (in one paragraph)

**Input:** tables or statistics from a trustworthy source (the challenge suggests [Estonian Data Portal](https://andmed.eesti.ee/)).  
**Middle:** your code turns those numbers into **event + probability** pairs (e.g. “probability a randomly chosen person is X” = count / total).  
**Output:** a clear **figure** (and maybe a small table) that lines events up from rare to common so a reader can _feel_ the scale.

You do **not** need to finish everything perfectly. The challenge rewards clear thinking, reproducible steps, and honest documentation.

---

### 1. Install the minimum toolbox

Do these once on your computer.

1. **Python 3.11+** (or 3.10+) from [python.org](https://www.python.org/downloads/) or your package manager.
2. **Git** so you can commit work in small steps (the challenge asks for history, not one giant commit).
3. **Editor** you like (VS Code, Cursor, etc.).

Optional but very helpful:

- **venv** (Python virtual environment) — keeps project libraries separate.
- **Jupyter** — nice for experimenting; you can still move final code into `.py` files later.

**Check:** open a terminal and run:

```bash
python --version
git --version
```

---

### 2. Understand three words you will use constantly

| Term             | Plain meaning                                                                                                                                                            |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Probability**  | A number from 0 to 1 (or 0% to 100%) describing how often something happens _if the model matches reality_. Often estimated from data as “favourable cases ÷ all cases”. |
| **Event**        | A clear yes/no outcome, e.g. “this person is unemployed”, “this forest parcel was logged this year”.                                                                     |
| **Reproducible** | Someone else can run your script on a fresh machine and get the same numbers and figure, because data loading and all steps are in code (not hand-edited Excel).         |

If you are unsure whether something is a valid probability, ask: **what is the denominator?** (What is the full set you divided by?)

---

### 3. Pick a direction (scope)

The challenge lists many ways to shine. **Pick one narrow story** first; you can add extras later.

Examples of _good_ narrow goals:

- “10–20 events from Estonian open data, from very rare (~0.001) to common (~0.5).”
- “One topic (demographics, health, environment) with a short narrative.”

Examples of _risky_ goals for a beginner:

- Scraping every dataset on the portal.
- A large interactive website as the main deliverable (the brief says front-end should not be the core).

Write your chosen scope in a short **“Plan”** section at the bottom of this README or in `notes.md` as you go.

---

### 4. Find data (Estonian Data Portal)

1. Open [andmed.eesti.ee](https://andmed.eesti.ee/).
2. Use English if needed; search keywords related to your topic (population, employment, forestry, transport, etc.).
3. For each candidate dataset, read:
   - **What** each row represents (person? household? square km? year?).
   - **Whether** it has counts, rates, or both.
4. Download **CSV** or use an **API** if the portal offers one — APIs are “extra points” territory but optional.

**Rule:** If you cannot load it with code, still **cite the exact URL, dataset name, and access date** in your README (the challenge allows that fallback).

---

### 5. Set up the project folder (reproducible layout)

Suggested structure (adjust names if you like):

```text
probability-scale/
  README.md                 # this file — how to run, what you did
  requirements.txt        # pinned library versions
  data/
    raw/                    # files exactly as downloaded (do not edit by hand)
    processed/              # optional: cleaned tables written by code
  src/
    load_data.py            # download or read CSV
    clean_and_compute.py    # turn raw into event + probability table
    plot_scale.py           # make and save the figure
  output/
    probabilities.csv       # final table (written by code)
    probability_scale.png   # final figure (written by code)
  LICENSE                   # pick a license (e.g. MIT) when you publish
```

**Why:** separates “what we downloaded” from “what we derived”, and keeps scripts small.

Create a virtual environment and a `requirements.txt` with libraries you actually use, for example:

```text
pandas
matplotlib
# add: requests, pyarrow, etc. only if you need them
```

Install:

```bash
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

### 6. Load data in code (first real script)

In `src/load_data.py` (or a notebook first):

1. Read the CSV with **pandas** (`pd.read_csv`).
2. Print `df.head()`, `df.columns`, and `len(df)` so you see what you really have.
3. If the file is huge, filter early (year, region) so iteration is fast.

**Checkpoint:** running the script prints sensible shapes and no silent errors.

---

### 7. Turn raw numbers into “event + probability”

This is the **core analysis step**. Pattern:

1. **Define the event** in one sentence.
2. **Find numerator and denominator** in the table (or combine two columns).
3. **Compute** `p = numerator / denominator`.
4. **Sanity-check:** is `p` between 0 and 1? Does the denominator match the story?

Typical patterns:

- **Share of a category:** count in category ÷ total count (same grouping).
- **Rate given per 1000:** divide by 1000 if that is what the documentation says.
- **Two groups:** e.g. “share of group A among A∪B” — be explicit.

Put results in a small table:

| event_label | probability | source_note                |
| ----------- | ----------- | -------------------------- |
| …           | …           | dataset X, table Y, year Z |

Save it as `output/probabilities.csv` from code.

**Common beginner mistake:** mixing populations (e.g. dividing employment count by total population when the employment count only covers ages 15–74). Fix by **re-reading the dataset documentation** and aligning definitions.

---

### 8. Make the graphic (“probability scale”)

In `src/plot_scale.py`:

1. Sort events by probability (smallest to largest, or the reverse — pick one and state it).
2. Use **horizontal bar chart** or **dot plot** — easy to read many labels.
3. Put **log scale** on the probability axis if you span several orders of magnitude (e.g. 0.001 vs 0.5); otherwise a linear scale is fine.
4. Save to `output/` as PNG or SVG.

**Checkpoint:** the figure tells a story without reading your code — clear title, axis labels, and readable event names.

---

### 9. Document like a reviewer is tired

The challenge says: if they cannot understand your code in ~3 minutes, they may stop reading.

In this README, include:

1. **One paragraph** motivation: what question does your scale answer?
2. **How to run** (copy-paste commands): create venv, install, run each script or `python -m src.plot_scale` if you wire a small CLI.
3. **Data citation:** link + access date + any licence notes from the portal.
4. **Example output:** embed or link to your saved figure.
5. **Limitations:** what you assumed, what you did not have time to check.

In code:

- **Good file and variable names** (not `df2`, `x_final_final`).
- **Short docstrings** on functions: what goes in, what comes out.
- **Comments** only where the _why_ is non-obvious.

---

### 10. Git workflow (work history)

Aim for **many small commits** with clear messages, e.g.:

- `Add raw data for X`
- `Implement probability table for demographics events`
- `Add horizontal bar chart with log scale`
- `Document run instructions and data licence`

Avoid one commit that adds everything at once.

---

### 11. Optional “extra flavour” (only if time and energy)

Pick **at most one** so you do not sprawl:

- **Bayesian:** a tiny toy example (Beta-Binomial) _separate_ from your main table, with a plain-language explanation.
- **Effect size or correlation:** compare two groups with a second figure; explain in words what “larger effect” means.
- **API ingestion:** replace manual download with `requests` + documented endpoint.

The challenge explicitly rewards describing a **thought process** even when something is not fully built — a short “Future work” section is honest and can score points.

---

### 12. Final checklist before you submit

- [ ] Running your steps from a clean clone reproduces `output/`.
- [ ] Probabilities are between 0 and 1 (or you explain exceptions).
- [ ] Denominators match the plain-language event descriptions.
- [ ] README has run instructions + data citation + example figure.
- [ ] Repository has a **LICENSE**.
- [ ] Git history shows incremental work.
- [ ] You used AI if you want — but **you** can explain every line that matters.

---

### Where to learn more (friendly starting points)

- **pandas:** [pandas “10 minutes” tutorial](https://pandas.pydata.org/docs/user_guide/10min.html)
- **Thinking about probabilities:** any short intro to “law of total probability” and base rates (helps you sanity-check numbers).
- **Good charts:** focus on **labels**, **ordering**, and **scales** before fancy design.

Good luck — the goal is not perfection, but a **clear, reproducible story** backed by real data.
