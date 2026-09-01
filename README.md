# Landing Page A/B Test

A reproducible analytics project for the Advanced Programming for Data Analysis course.

## Student

- **Name:** Haneen Mohammad Dahbour
- **Student ID:** 23038230

## Project question

Does the new landing page produce a statistically supported difference in
conversion rate compared with the old landing page?

The project cleans the experiment records, calculates conversion summaries,
tests the difference between the two conversion rates, and provides a final
recommendation based on statistical and practical evidence.

## Experiment definition

- **Experimental unit:** One user
- **Control group:** Users assigned to the old landing page
- **Treatment group:** Users assigned to the new landing page
- **Primary metric:** Proportion of users who converted
- **Null hypothesis (H0):** The treatment and control population conversion rates are equal
- **Alternative hypothesis (H1):** The treatment and control population conversion rates are different
- **Significance level:** alpha = 0.05

## Dataset

The project uses the public **A/B testing** dataset from Kaggle:

https://www.kaggle.com/datasets/zhangluyuan/ab-testing

Only `ab_data.csv` is used. The raw file is downloaded separately and placed at:

```text
data/raw/ab_data.csv
```

The raw CSV is excluded from Git and must not be edited or committed. Additional
source and download information is recorded in `data/raw/README.md`.

## Repository structure

```text
apda-ab-test-23038230/
|-- README.md
|-- requirements.txt
|-- .gitignore
|-- data/
|   |-- raw/
|   |   `-- README.md
|   `-- processed/
|-- src/
|   `-- pipeline.py
|-- scripts/
|   |-- run_pipeline.py
|   `-- run_sql.py
|-- sql/
|   |-- group_summary.sql
|   `-- daily_conversion.sql
|-- r/
|   |-- ab_test.R
|   `-- package-versions.txt
|-- tests/
|   `-- test_pipeline.py
|-- outputs/
|   |-- group_summary.csv
|   |-- daily_conversion.csv
|   `-- figures/
`-- .github/
    `-- workflows/
        `-- tests.yml
```

## Software requirements

### Python

The project was developed using Python 3.14.5. Required Python packages are
listed with exact versions in `requirements.txt`.

Main packages:

- pandas
- pyarrow
- duckdb
- pytest

### R

R is required for the statistical test and visualizations. The R script uses:

- readr
- dplyr
- ggplot2
- base R `stats`

## Environment setup

Run these commands from the repository root.

### Windows PowerShell

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
& ".\.venv\Scripts\Activate.ps1"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Reproduce the analysis

The following commands are run from the repository root.

### Run the Python cleaning pipeline

```powershell
python scripts/run_pipeline.py --input data/raw/ab_data.csv --output-dir data/processed
```

### Run the tests

```powershell
pytest -q
```

### Run the DuckDB analysis

```powershell
python scripts/run_sql.py
```

### Run the R analysis

`Rscript` must be available on PATH before running the command.

```powershell
Rscript r/ab_test.R
```

## Generated files

The Python pipeline creates:

```text
data/processed/clean_ab_data.csv
data/processed/clean_ab_data.parquet
```

The DuckDB analysis creates:

```text
outputs/group_summary.csv
outputs/daily_conversion.csv
```

The R statistical analysis creates:

```text
outputs/statistical_test.csv
outputs/figures/conversion_rates.png
outputs/figures/daily_conversion.png
```

The exact R and package versions used for Phase 5 are recorded in:

```text
r/package-versions.txt
```

The processed datasets are excluded from Git because they can be recreated from
the raw dataset using the documented pipeline command.

## DuckDB analytical layer

Phase 4 uses `scripts/run_sql.py` with an in-memory DuckDB engine to query
the cleaned Parquet dataset using the versioned SQL files in `sql/`.

The analytical layer produces overall and daily summaries and validates that
all aggregated user counts reconcile to the 290,584 cleaned experiment users.

| Group | Users | Conversions | Conversion rate |
|---|---:|---:|---:|
| Control | 145,274 | 17,489 | 12.0386% |
| Treatment | 145,310 | 17,264 | 11.8808% |

The observed treatment-minus-control difference is approximately -0.1578
percentage points. This is descriptive only; statistical inference is performed
in Phase 5.

Phase 4 reproducibility verification passed: rerunning the DuckDB analytical
pipeline from the same cleaned Parquet input reproduced both analytical CSV
outputs identically.

## Statistical inference

Phase 5 tests whether the descriptive control-versus-treatment conversion-rate
difference observed in Phase 4 is statistically supported.

The analysis uses a two-sided two-proportion test with:

```text
H0: treatment and control population conversion rates are equal
H1: treatment and control population conversion rates are different
alpha = 0.05
```

The R analysis produced a treatment-minus-control difference of approximately
-0.1578 percentage points, with a two-sided p-value of 0.189883 and a 95%
confidence interval from approximately -0.3938 to +0.0781 percentage points.

Because the p-value is greater than alpha = 0.05 and the confidence interval
contains zero, the analysis fails to reject H0. The experiment therefore does
not provide sufficient statistical evidence that the population conversion
rates of the old and new landing pages differ.

Statistical significance is interpreted separately from practical significance.

R 4.6.1 and the required `readr`, `dplyr`, and `ggplot2` packages were verified for the Phase 5 analysis.

Phase 5 reproducibility verification passed. The R statistical result was
independently reproduced with the equivalent two-proportion z-test equations
in Python, and rerunning the R analysis reproduced the result CSV and both
figures with identical SHA-256 hashes.

## Testing and continuous integration

The cleaning pipeline is covered by 13 focused pytest cases using small
synthetic DataFrames, so the tests do not require the downloaded Kaggle dataset.

The tests cover schema validation, missing and invalid values, timestamp
validation, experiment-assignment mismatches, deterministic duplicate handling,
conflicting duplicate detection, and final one-user-per-row invariants.

Run the tests locally with:

```powershell
python -m pytest -q
```

GitHub Actions is configured in `.github/workflows/tests.yml` to recreate the
Python environment and run the same test suite automatically on pushes and pull
requests. The Phase 3 CI verification completed successfully on a fresh Ubuntu runner.
The workflow uses `runs-on: ubuntu-latest`, so GitHub automatically creates a
temporary Linux machine, checks out the repository, installs Python and the
documented dependencies, and runs the same pytest suite used locally.

## Reproducibility

All code uses paths relative to the repository root. No personal absolute paths
are stored in the source code. The processed data, summaries, tests, and figures
can be recreated using the commands documented above.

## Project implementation guide

A detailed phase-by-phase explanation of the project, technical decisions,
validation results, and implementation progress is available in
[PROJECT_PHASES.md](PROJECT_PHASES.md).
