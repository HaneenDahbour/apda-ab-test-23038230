"""Unit tests for the A/B test validation and cleaning pipeline."""

import pandas as pd
import pytest

from src.pipeline import clean_ab_data


def make_valid_data() -> pd.DataFrame:
    """Return a small valid A/B experiment dataset."""

    return pd.DataFrame(
        [
            {
                "user_id": 1,
                "timestamp": "2017-01-01 10:00:00",
                "group": "control",
                "landing_page": "old_page",
                "converted": 0,
            },
            {
                "user_id": 2,
                "timestamp": "2017-01-01 11:00:00",
                "group": "treatment",
                "landing_page": "new_page",
                "converted": 1,
            },
        ]
    )


def test_valid_data_passes():
    """Valid experiment records should remain in the clean dataset."""

    raw = make_valid_data()

    cleaned, report = clean_ab_data(raw)

    assert len(cleaned) == 2
    assert cleaned["user_id"].nunique() == 2
    assert report["raw_rows"] == 2
    assert report["clean_rows"] == 2
    assert report["assignment_mismatches_removed"] == 0
    assert report["duplicate_rows_removed"] == 0


def test_missing_required_column_fails():
    """A required column must not be silently accepted when missing."""

    raw = make_valid_data().drop(columns=["converted"])

    with pytest.raises(
        ValueError,
        match="Missing required columns",
    ):
        clean_ab_data(raw)


def test_unexpected_column_fails():
    """Unexpected schema changes should be detected."""

    raw = make_valid_data()
    raw["unexpected"] = "value"

    with pytest.raises(
        ValueError,
        match="Unexpected columns",
    ):
        clean_ab_data(raw)


def test_missing_required_value_fails():
    """Missing required data should stop the pipeline."""

    raw = make_valid_data()
    raw.loc[0, "group"] = None

    with pytest.raises(
        ValueError,
        match="Missing values found",
    ):
        clean_ab_data(raw)


@pytest.mark.parametrize(
    ("column", "bad_value", "message"),
    [
        ("group", "unknown_group", "Unexpected group values"),
        (
            "landing_page",
            "unknown_page",
            "Unexpected landing_page values",
        ),
        ("converted", 7, "Unexpected converted values"),
    ],
)
def test_invalid_domain_values_fail(
    column,
    bad_value,
    message,
):
    """Values outside the allowed experiment domains must fail."""

    raw = make_valid_data()
    raw.loc[0, column] = bad_value

    with pytest.raises(ValueError, match=message):
        clean_ab_data(raw)


def test_invalid_timestamp_fails():
    """Malformed timestamps must not enter the clean dataset."""

    raw = make_valid_data()
    raw.loc[0, "timestamp"] = "not-a-real-timestamp"

    with pytest.raises(
        ValueError,
        match="unparseable timestamp",
    ):
        clean_ab_data(raw)


def test_assignment_mismatch_is_removed():
    """Rows whose group and landing page disagree should be removed."""

    raw = make_valid_data()

    mismatch = pd.DataFrame(
        [
            {
                "user_id": 3,
                "timestamp": "2017-01-01 12:00:00",
                "group": "control",
                "landing_page": "new_page",
                "converted": 1,
            }
        ]
    )

    raw = pd.concat(
        [raw, mismatch],
        ignore_index=True,
    )

    cleaned, report = clean_ab_data(raw)

    assert len(cleaned) == 2
    assert 3 not in set(cleaned["user_id"])
    assert report["assignment_mismatches_removed"] == 1


def test_equivalent_duplicate_keeps_earliest():
    """Equivalent duplicates should keep the earliest observation."""

    raw = pd.DataFrame(
        [
            {
                "user_id": 10,
                "timestamp": "2017-01-05 12:00:00",
                "group": "treatment",
                "landing_page": "new_page",
                "converted": 0,
            },
            {
                "user_id": 10,
                "timestamp": "2017-01-03 12:00:00",
                "group": "treatment",
                "landing_page": "new_page",
                "converted": 0,
            },
        ]
    )

    cleaned, report = clean_ab_data(raw)

    assert len(cleaned) == 1
    assert report["duplicate_rows_removed"] == 1
    assert report["duplicate_users_after_assignment_cleaning"] == 1

    kept_timestamp = cleaned.iloc[0]["timestamp"]

    assert kept_timestamp == pd.Timestamp(
        "2017-01-03 12:00:00",
        tz="UTC",
    )


def test_conflicting_duplicate_conversion_fails():
    """Conflicting conversion outcomes for one valid user must fail."""

    raw = pd.DataFrame(
        [
            {
                "user_id": 20,
                "timestamp": "2017-01-01 10:00:00",
                "group": "control",
                "landing_page": "old_page",
                "converted": 0,
            },
            {
                "user_id": 20,
                "timestamp": "2017-01-02 10:00:00",
                "group": "control",
                "landing_page": "old_page",
                "converted": 1,
            },
        ]
    )

    with pytest.raises(
        ValueError,
        match="Conflicting duplicate user records",
    ):
        clean_ab_data(raw)


def test_conflicting_duplicate_assignment_fails():
    """A user appearing in two valid experiment arms must fail."""

    raw = pd.DataFrame(
        [
            {
                "user_id": 30,
                "timestamp": "2017-01-01 10:00:00",
                "group": "control",
                "landing_page": "old_page",
                "converted": 0,
            },
            {
                "user_id": 30,
                "timestamp": "2017-01-02 10:00:00",
                "group": "treatment",
                "landing_page": "new_page",
                "converted": 0,
            },
        ]
    )

    with pytest.raises(
        ValueError,
        match="Conflicting duplicate user records",
    ):
        clean_ab_data(raw)


def test_final_clean_data_has_one_row_per_user():
    """The final cleaning invariant is one row per experiment user."""

    raw = pd.DataFrame(
        [
            {
                "user_id": 100,
                "timestamp": "2017-01-01 10:00:00",
                "group": "control",
                "landing_page": "old_page",
                "converted": 0,
            },
            {
                "user_id": 101,
                "timestamp": "2017-01-01 11:00:00",
                "group": "treatment",
                "landing_page": "new_page",
                "converted": 1,
            },
            {
                "user_id": 101,
                "timestamp": "2017-01-02 11:00:00",
                "group": "treatment",
                "landing_page": "new_page",
                "converted": 1,
            },
        ]
    )

    cleaned, _ = clean_ab_data(raw)

    assert len(cleaned) == cleaned["user_id"].nunique()
    assert cleaned["user_id"].duplicated().sum() == 0
