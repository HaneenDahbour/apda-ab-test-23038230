"""Command-line entry point for the A/B test cleaning pipeline."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.pipeline import clean_ab_data


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description="Validate and clean the landing-page A/B test dataset."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the raw A/B test CSV file.",
    )

    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory where cleaned datasets will be written.",
    )

    return parser.parse_args()


def resolve_path(value: str) -> Path:
    """Resolve a path relative to the repository root."""

    path = Path(value)

    if not path.is_absolute():
        path = PROJECT_ROOT / path

    return path.resolve()


def main() -> int:
    """Run the complete cleaning pipeline."""

    args = parse_args()

    input_path = resolve_path(args.input)
    output_dir = resolve_path(args.output_dir)

    if not input_path.exists():
        raise FileNotFoundError(
            f"Input dataset does not exist: {input_path}"
        )

    print(f"Input:      {input_path}")
    print(f"Output dir: {output_dir}")

    raw = pd.read_csv(input_path)

    cleaned, report = clean_ab_data(raw)

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    csv_path = output_dir / "clean_ab_data.csv"
    parquet_path = output_dir / "clean_ab_data.parquet"

    cleaned.to_csv(
        csv_path,
        index=False,
    )

    cleaned.to_parquet(
        parquet_path,
        index=False,
    )

    print("\nCleaning report:")

    for key, value in report.items():
        if isinstance(value, int):
            print(f"{key}: {value:,}")
        else:
            print(f"{key}: {value}")

    print("\nGenerated files:")
    print(csv_path)
    print(parquet_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
