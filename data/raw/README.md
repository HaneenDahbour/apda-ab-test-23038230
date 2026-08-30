# Raw Data

## Dataset source

- **Dataset title:** A/B testing
- **Source platform:** Kaggle
- **Dataset URL:** https://www.kaggle.com/datasets/zhangluyuan/ab-testing
- **Required filename:** ab_data.csv
- **Download date:** 2026-08-29

## Placement

Download b_data.csv separately from Kaggle and place it in this directory:

data/raw/ab_data.csv

## Data policy

The original CSV must remain unchanged. It is excluded from Git through the
project's .gitignore and must not be committed to GitHub.

The reproducible Python pipeline reads this raw file and creates cleaned CSV
and Parquet files inside data/processed/.
