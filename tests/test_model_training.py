
"""Tests for training data preparation and grouped holdout splitting."""

import pandas as pd
import pytest

from src.train_model import (
    FEATURE_COLUMNS,
    create_random_forest_pipeline,
    prepare_training_data,
    split_training_data,
)


@pytest.fixture
def training_dataset() -> pd.DataFrame:
    """Provide multiple titles with records on different platforms."""
    records = []

    for index in range(20):
        name = f"Game {index}"

        for platform in ["PS2", "Wii"]:
            records.append(
                {
                    "Name": name,
                    "Platform": platform,
                    "Genre": "Action" if index % 2 == 0 else "Sports",
                    "Year": 2000 + index % 10,
                    "Global_Sales": 0.5 + index * 0.1,
                }
            )

    return pd.DataFrame(records)


def test_training_data_preserves_valid_records(
    training_dataset: pd.DataFrame,
) -> None:
    """All valid historical records remain available for training."""
    prepared = prepare_training_data(training_dataset)

    assert len(prepared) == 40


def test_training_data_excludes_missing_years(
    training_dataset: pd.DataFrame,
) -> None:
    """Records without release years are excluded from model training."""
    training_dataset.loc[0, "Year"] = None

    prepared = prepare_training_data(training_dataset)

    assert len(prepared) == 39
    assert prepared["Year"].isna().sum() == 0


def test_training_data_excludes_negative_sales(
    training_dataset: pd.DataFrame,
) -> None:
    """Records with negative target values are excluded."""
    training_dataset.loc[0, "Global_Sales"] = -1.0

    prepared = prepare_training_data(training_dataset)

    assert len(prepared) == 39


def test_grouped_split_has_no_title_overlap(
    training_dataset: pd.DataFrame,
) -> None:
    """The same game title never appears in both holdout partitions."""
    prepared = prepare_training_data(training_dataset)

    train_df, test_df = split_training_data(prepared)

    training_titles = set(
        train_df["Name"].str.casefold()
    )

    test_titles = set(
        test_df["Name"].str.casefold()
    )

    assert training_titles.isdisjoint(test_titles)


def test_grouped_split_preserves_all_records(
    training_dataset: pd.DataFrame,
) -> None:
    """The holdout split preserves every prepared record exactly once."""
    prepared = prepare_training_data(training_dataset)

    train_df, test_df = split_training_data(prepared)

    assert len(train_df) + len(test_df) == len(prepared)


def test_random_forest_pipeline_uses_expected_features(
    training_dataset: pd.DataFrame,
) -> None:
    """The regression pipeline can train and predict with its feature schema."""
    prepared = prepare_training_data(training_dataset)

    model = create_random_forest_pipeline()

    model.fit(
        prepared[FEATURE_COLUMNS],
        prepared["Global_Sales"],
    )

    predictions = model.predict(
        prepared[FEATURE_COLUMNS].head(3)
    )

    assert len(predictions) == 3
    assert all(value >= 0 for value in predictions)
