"""Validation and cleaning logic for the landing-page A/B test."""

from __future__ import annotations

from typing import Any

import pandas as pd


REQUIRED_COLUMNS = (
    "user_id",
    "timestamp",
    "group",
    "landing_page",
    "converted",
)

ALLOWED_GROUPS = {"control", "treatment"}
ALLOWED_PAGES = {"old_page", "new_page"}
ALLOWED_CONVERSIONS = {0, 1}


def validate_schema(df: pd.DataFrame) -> None:
    """Validate that the input contains exactly the expected columns."""

    actual = set(df.columns)
    required = set(REQUIRED_COLUMNS)

    missing = required - actual
    unexpected = actual - required

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    if unexpected:
        raise ValueError(
            f"Unexpected columns: {sorted(unexpected)}"
        )


def validate_raw_values(df: pd.DataFrame) -> None:
    """Validate missing values and allowed categorical domains."""

    null_counts = df[list(REQUIRED_COLUMNS)].isna().sum()
    columns_with_nulls = null_counts[null_counts > 0]

    if not columns_with_nulls.empty:
        details = columns_with_nulls.to_dict()
        raise ValueError(
            f"Missing values found in required columns: {details}"
        )

    bad_groups = set(df["group"].unique()) - ALLOWED_GROUPS
    if bad_groups:
        raise ValueError(
            f"Unexpected group values: {sorted(bad_groups)}"
        )

    bad_pages = (
        set(df["landing_page"].unique()) - ALLOWED_PAGES
    )
    if bad_pages:
        raise ValueError(
            f"Unexpected landing_page values: {sorted(bad_pages)}"
        )

    bad_converted = (
        set(df["converted"].unique()) - ALLOWED_CONVERSIONS
    )
    if bad_converted:
        raise ValueError(
            f"Unexpected converted values: {sorted(bad_converted)}"
        )


def parse_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with timestamp parsed as UTC datetime."""

    result = df.copy()

    parsed = pd.to_datetime(
        result["timestamp"],
        errors="coerce",
        utc=True,
    )

    invalid_count = int(parsed.isna().sum())

    if invalid_count:
        raise ValueError(
            f"Found {invalid_count} unparseable timestamp(s)."
        )

    result["timestamp"] = parsed

    return result


def valid_assignment_mask(df: pd.DataFrame) -> pd.Series:
    """Identify rows consistent with the experiment design."""

    control_valid = (
        (df["group"] == "control")
        & (df["landing_page"] == "old_page")
    )

    treatment_valid = (
        (df["group"] == "treatment")
        & (df["landing_page"] == "new_page")
    )

    return control_valid | treatment_valid


def validate_duplicate_users(df: pd.DataFrame) -> None:
    """Reject duplicated users whose valid records conflict."""

    duplicated = df[df.duplicated("user_id", keep=False)]

    if duplicated.empty:
        return

    consistency = (
        duplicated
        .groupby("user_id")
        .agg(
            group_values=("group", "nunique"),
            page_values=("landing_page", "nunique"),
            conversion_values=("converted", "nunique"),
        )
    )

    conflicting = consistency[
        (consistency["group_values"] > 1)
        | (consistency["page_values"] > 1)
        | (consistency["conversion_values"] > 1)
    ]

    if not conflicting.empty:
        user_ids = conflicting.index.tolist()

        raise ValueError(
            "Conflicting duplicate user records found for "
            f"user_id values: {user_ids}"
        )


def clean_ab_data(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Validate and clean raw A/B experiment records."""

    validate_schema(df)
    validate_raw_values(df)

    working = parse_timestamps(df)

    raw_rows = len(working)

    assignment_mask = valid_assignment_mask(working)

    mismatches_removed = int((~assignment_mask).sum())

    aligned = working.loc[assignment_mask].copy()

    duplicate_users_before = int(
        aligned.loc[
            aligned.duplicated("user_id", keep=False),
            "user_id",
        ].nunique()
    )

    validate_duplicate_users(aligned)

    before_deduplication = len(aligned)

    cleaned = (
        aligned
        .sort_values(["user_id", "timestamp"])
        .drop_duplicates(
            subset=["user_id"],
            keep="first",
        )
        .sort_values(["timestamp", "user_id"])
        .reset_index(drop=True)
    )

    duplicate_rows_removed = (
        before_deduplication - len(cleaned)
    )

    if cleaned["user_id"].duplicated().any():
        raise RuntimeError(
            "Cleaning invariant failed: duplicate users remain."
        )

    if not valid_assignment_mask(cleaned).all():
        raise RuntimeError(
            "Cleaning invariant failed: assignment mismatch remains."
        )

    report: dict[str, Any] = {
        "raw_rows": raw_rows,
        "assignment_mismatches_removed": mismatches_removed,
        "duplicate_users_after_assignment_cleaning": (
            duplicate_users_before
        ),
        "duplicate_rows_removed": duplicate_rows_removed,
        "clean_rows": len(cleaned),
        "unique_users": int(cleaned["user_id"].nunique()),
        "control_rows": int(
            (cleaned["group"] == "control").sum()
        ),
        "treatment_rows": int(
            (cleaned["group"] == "treatment").sum()
        ),
    }

    return cleaned, report
