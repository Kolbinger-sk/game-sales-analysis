
"""Tests for the project's data preparation and validation logic."""

import pandas as pd
import pytest

from main import clean_dataset, create_year_dataset


def create_sample_dataset() -> pd.DataFrame:
    """Create a representative dataset with common data quality issues."""
    return pd.DataFrame(
        [
            {
                "Rank": 1,
                "Name": "Game A",
                "Platform": "PS2",
                "Year": 2005,
                "Genre": "Action",
                "Publisher": "Publisher A",
                "NA_Sales": 1.0,
                "EU_Sales": 0.5,
                "JP_Sales": 0.2,
                "Other_Sales": 0.1,
                "Global_Sales": 1.8,
            },
            {
                "Rank": 2,
                "Name": "Game B",
                "Platform": "Wii",
                "Year": None,
                "Genre": "Sports",
                "Publisher": None,
                "NA_Sales": 0.5,
                "EU_Sales": 0.3,
                "JP_Sales": 0.1,
                "Other_Sales": 0.1,
                "Global_Sales": 1.0,
            },
            {
                "Rank": 3,
                "Name": "Game C",
                "Platform": "PS3",
                "Year": 2012,
                "Genre": "Action",
                "Publisher": "Publisher C",
                "NA_Sales": -1.0,
                "EU_Sales": 0.2,
                "JP_Sales": 0.1,
                "Other_Sales": 0.1,
                "Global_Sales": 0.4,
            },
        ]
    )


def test_clean_dataset_preserves_missing_years() -> None:
    """Records without a release year remain in the general dataset."""
    cleaned = clean_dataset(create_sample_dataset())

    assert len(cleaned) == 2
    assert cleaned["Year"].isna().sum() == 1


def test_clean_dataset_removes_negative_sales() -> None:
    """Records containing negative regional sales are excluded."""
    cleaned = clean_dataset(create_sample_dataset())

    assert "Game C" not in cleaned["Name"].tolist()


def test_clean_dataset_fills_missing_publishers() -> None:
    """Unknown publishers receive the project's standard placeholder."""
    cleaned = clean_dataset(create_sample_dataset())

    publisher = cleaned.loc[
        cleaned["Name"] == "Game B",
        "Publisher",
    ].iloc[0]

    assert publisher == "Unknown"


def test_clean_dataset_removes_exact_duplicates() -> None:
    """Duplicate records are removed during data preparation."""
    sample = create_sample_dataset()

    duplicated = pd.concat(
        [sample, sample.iloc[[0]]],
        ignore_index=True,
    )

    cleaned = clean_dataset(duplicated)

    assert len(cleaned) == 2


def test_year_dataset_excludes_missing_years() -> None:
    """Temporal analysis includes only records with known release years."""
    cleaned = clean_dataset(create_sample_dataset())

    yearly = create_year_dataset(cleaned)

    assert len(yearly) == 1
    assert yearly.iloc[0]["Year"] == 2005


def test_year_dataset_excludes_out_of_range_years() -> None:
    """Release years outside the configured period are excluded."""
    cleaned = clean_dataset(create_sample_dataset())

    future_record = cleaned.iloc[[0]].copy()
    future_record["Year"] = 2025

    combined = pd.concat(
        [cleaned, future_record],
        ignore_index=True,
    )

    yearly = create_year_dataset(combined)

    assert yearly["Year"].tolist() == [2005]


def test_year_dataset_uses_integer_years() -> None:
    """The temporal dataset stores release years as integers."""
    cleaned = clean_dataset(create_sample_dataset())

    yearly = create_year_dataset(cleaned)

    assert pd.api.types.is_integer_dtype(yearly["Year"])
