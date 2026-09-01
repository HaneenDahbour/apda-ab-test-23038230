"""Run DuckDB SQL analysis against the cleaned A/B-test dataset."""

from pathlib import Path

import duckdb


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "clean_ab_data.parquet"
SQL_DIR = PROJECT_ROOT / "sql"
OUTPUT_DIR = PROJECT_ROOT / "outputs"


def load_sql(filename: str) -> str:
    """Read one SQL query from the sql directory."""

    path = SQL_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"SQL file not found: {path}")

    return path.read_text(encoding="utf-8")


def main() -> None:
    """Execute analytical SQL queries and write reproducible outputs."""

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            "Clean Parquet input not found. Run scripts/run_pipeline.py first."
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    connection = duckdb.connect(database=":memory:")

    try:
        relation = connection.read_parquet(str(INPUT_PATH))
        relation.create_view("clean_ab")

        total_rows = connection.execute(
            "SELECT COUNT(*) FROM clean_ab"
        ).fetchone()[0]

        unique_users = connection.execute(
            "SELECT COUNT(DISTINCT user_id) FROM clean_ab"
        ).fetchone()[0]

        if total_rows != unique_users:
            raise RuntimeError(
                "Clean input invariant failed: expected one row per user."
            )

        group_summary = connection.execute(
            load_sql("group_summary.sql")
        ).fetchdf()

        daily_conversion = connection.execute(
            load_sql("daily_conversion.sql")
        ).fetchdf()

        expected_group_columns = [
            "group",
            "users",
            "conversions",
            "conversion_rate",
        ]

        if list(group_summary.columns) != expected_group_columns:
            raise RuntimeError("Unexpected group-summary schema.")

        if set(group_summary["group"]) != {"control", "treatment"}:
            raise RuntimeError("Expected control and treatment groups.")

        if int(group_summary["users"].sum()) != total_rows:
            raise RuntimeError("Group-summary user counts do not match input.")

        if int(daily_conversion["users"].sum()) != total_rows:
            raise RuntimeError("Daily-summary user counts do not match input.")

        group_output = OUTPUT_DIR / "group_summary.csv"
        daily_output = OUTPUT_DIR / "daily_conversion.csv"

        group_summary.to_csv(group_output, index=False)
        daily_conversion.to_csv(daily_output, index=False)

        print("DuckDB analysis completed successfully.")
        print(f"Input rows: {total_rows:,}")
        print(f"Unique users: {unique_users:,}")
        print()
        print("Group summary:")
        print(group_summary.to_string(index=False))
        print()
        print(f"Daily summary rows: {len(daily_conversion):,}")
        print(f"Group output: {group_output}")
        print(f"Daily output: {daily_output}")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
