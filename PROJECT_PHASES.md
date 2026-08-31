# Project Phases and Implementation Guide

## Project Goal

This project evaluates whether a **new landing page** changes the conversion rate compared with the **old landing page**.

Experiment design:

- `control` -> `old_page`
- `treatment` -> `new_page`
- `converted = 1` means the user converted
- `converted = 0` means the user did not convert
- Experimental unit: one user

This file is a living project record. It should be updated at the end of each phase.

---

## Project Roadmap

| Phase | Purpose | Main tools | Status |
|---|---|---|---|
| 1 | Build a reproducible project foundation | Git, GitHub, Python environment, Markdown | COMPLETE |
| 2 | Validate and clean the raw experiment data | Python, pandas, pyarrow | COMPLETE |
| 3 | Test the pipeline automatically | pytest, GitHub Actions | NOT STARTED |
| 4 | Perform analytical queries | DuckDB, SQL, Python | NOT STARTED |
| 5 | Perform statistical inference and visualization | R, stats, ggplot2 | NOT STARTED |
| 6 | Interpret results and finalize the project | Markdown, Git, GitHub | NOT STARTED |

---

# Phase 1 - Reproducible Workspace Foundation

## Purpose

Create a clean, reproducible project before writing analysis code.

A reproducible project should allow another person to obtain the same raw dataset,
install the documented environment, run the documented commands, and recreate
the analysis.

## What was done

- Created the project folder structure.
- Created and activated a Python virtual environment.
- Recorded exact Python package versions in `requirements.txt`.
- Created `.gitignore`.
- Protected `.venv/` from Git.
- Protected `data/raw/ab_data.csv` from Git.
- Added `data/raw/README.md` to document the raw dataset source and location.
- Added `.gitkeep` files so important empty folders remain trackable.
- Created the main `README.md`.
- Initialized Git.
- Created the first meaningful commit.
- Created a public GitHub repository.
- Connected local `main` to `origin/main`.
- Pushed the foundation commit successfully.

## Foundation commit

```text
7c9ddc7 chore: initialize reproducible A/B test workspace
```

## Why this phase matters

It separates raw data, code, dependencies, processed data, outputs, tests, and documentation.
It also ensures the analysis does not depend on a personal absolute Windows path.

## Status

**COMPLETE**

---

# Phase 2 - Python Validation and Cleaning Pipeline

## Purpose

Transform the raw A/B experiment dataset into a clean, validated dataset using deterministic Python code.
The original raw CSV remains unchanged.

## Block 2A - Raw Data Inspection

Raw file: `data/raw/ab_data.csv`

File size: `15,901,933 bytes`

SHA-256:

```text
d56e2accec25e99ac21cb3d76c5df516dd19cc7a77c14c9014f94e1ea1301beb
```

Raw shape:

```text
Rows: 294,478
Columns: 5
```

Columns: `user_id`, `timestamp`, `group`, `landing_page`, `converted`.

Findings:

- Missing values: 0
- Unparseable timestamps: 0
- Unique users: 290,584
- Rows belonging to duplicated user IDs: 7,788
- Duplicated user IDs: 3,894

Valid experiment assignments:

```text
control   + old_page
treatment + new_page
```

Invalid experiment assignments:

```text
control   + new_page
treatment + old_page
```

Observed mismatches:

```text
control + new_page      1,928
treatment + old_page    1,965
Total mismatches        3,893
```

## Block 2B - Cleaning Contract

Cleaning order:

1. Validate required schema.
2. Validate missing values.
3. Validate allowed `group` values.
4. Validate allowed `landing_page` values.
5. Validate `converted` contains only `0` and `1`.
6. Parse and validate timestamps.
7. Remove assignment mismatches.
8. Inspect duplicate users after assignment cleaning.
9. Reject conflicting duplicate records.
10. For equivalent duplicates, keep the earliest valid observation.
11. Verify one row remains per user.
12. Verify no assignment mismatches remain.

After assignment cleaning:

```text
Raw rows:                   294,478
Assignment mismatches:        3,893
Rows after removal:         290,585
Unique users:               290,584
Extra observations:               1
```

Only user `773192` remained duplicated. Both rows agreed on group, landing page, and conversion; only timestamp differed. The deterministic rule is to keep the earliest valid observation.

## Block 2C - Core Python Cleaning Pipeline

Created: `src/pipeline.py`

Main responsibilities:

- `validate_schema()`
- `validate_raw_values()`
- `parse_timestamps()`
- `valid_assignment_mask()`
- `validate_duplicate_users()`
- `clean_ab_data()`

Real-data smoke-test result:

```text
raw_rows: 294,478
assignment_mismatches_removed: 3,893
duplicate_users_after_assignment_cleaning: 1
duplicate_rows_removed: 1
clean_rows: 290,584
unique_users: 290,584
control_rows: 145,274
treatment_rows: 145,310
```

Final invariants:

```text
Duplicate users remaining:       0
Assignment mismatches remaining: 0
```

Clean descriptive conversion rates:

```text
control
count       145,274
converted    17,489
rate       0.120386

treatment
count       145,310
converted    17,264
rate       0.118808
```

These are descriptive results only. Statistical inference is deferred to Phase 5.

## Phase 2 remaining work

- Block 2D: create command-line pipeline runner
- Write clean CSV
- Write clean Parquet
- Validate generated files
- Confirm reproducible rerun
- Update documentation
- Create Commit 2
- Push Commit 2 to GitHub

## Status

**COMPLETE**

---

# Phase 3 - Pipeline Tests and Continuous Integration

## Purpose

Verify automatically that the pipeline behaves correctly and continues to do so after future code changes.

Planned tools: pytest and GitHub Actions.

Planned checks include valid input, schema failures, invalid values, malformed timestamps, assignment mismatches, equivalent duplicates, conflicting duplicates, and final uniqueness.

## Status

**NOT STARTED**

---

# Phase 4 - DuckDB Analytical Queries

## Purpose

Use SQL to create analytical summaries from the cleaned dataset.

Planned tools: DuckDB, SQL, Python.

Planned files:

```text
sql/analysis.sql
scripts/run_sql.py
```

Planned outputs:

```text
outputs/group_summary.csv
outputs/daily_conversion.csv
```

## Status

**NOT STARTED**

---

# Phase 5 - R Statistical Analysis

## Purpose

Determine whether the observed difference between control and treatment conversion rates is statistically supported.

Planned tools: R, readr, dplyr, ggplot2, base R stats.

Hypotheses:

```text
H0: control and treatment population conversion rates are equal
H1: control and treatment population conversion rates are different
alpha = 0.05
```

Planned work includes a hypothesis test, confidence interval, effect-size interpretation, visualizations, and a statistical decision.

## Status

**NOT STARTED**

---

# Phase 6 - Final Interpretation and Documentation

## Purpose

Combine all technical outputs into a clear final answer to the project question.

The final interpretation will distinguish between descriptive difference, statistical significance, and practical significance.
The README and this document will be updated with final results and exact reproduction commands.

## Status

**NOT STARTED**

---

# Reproducibility Goal

At completion, another person should be able to:

1. Clone the repository.
2. Obtain the documented raw dataset.
3. Place it at `data/raw/ab_data.csv`.
4. Create the Python virtual environment.
5. Install `requirements.txt`.
6. Run the cleaning pipeline.
7. Run automated tests.
8. Run DuckDB analysis.
9. Run the R statistical analysis.
10. Recreate the tables, figures, and final conclusion.

---

# Commit Roadmap

```text
Commit 1 - Workspace and reproducibility foundation        COMPLETE
Commit 2 - Python validation and cleaning pipeline         COMPLETE
Commit 3 - Pipeline tests and GitHub Actions               NOT STARTED
Commit 4 - DuckDB analytical queries                       NOT STARTED
Commit 5 - R analysis, figures, and statistical test       NOT STARTED
Commit 6 - Final report documentation and results          NOT STARTED
```

---

# Current Position

```text
Phase 1  Reproducible Foundation          COMPLETE
Phase 2  Python Data Pipeline             COMPLETE
Phase 3  Tests + Continuous Integration   NOT STARTED
Phase 4  DuckDB + SQL                     NOT STARTED
Phase 5  R Statistical Analysis           NOT STARTED
Phase 6  Final Interpretation             NOT STARTED
```

Next step: **Phase 2, Block 2D - Command-line pipeline runner and generated clean datasets.**

