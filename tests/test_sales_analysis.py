
"""Tests for platform, regional, and release-year sales aggregations."""

import pandas as pd
import pytest

from src.platform_analysis import calculate_platform_statistics
from src.regional_analysis import (
    calculate_genre_regional_statistics,
    calculate_regional_statistics,
)
from src.time_analysis import (
    calculate_yearly_changes,
    calculate_yearly_sales,
)


@pytest.fixture
def sample_sales_data() -> pd.DataFrame:
    """Provide a small dataset with known aggregation results."""
    return pd.DataFrame(
        [
            {
                "Name": "Game A",
                "Platform": "PS2",
                "Year": 2000,
                "Genre": "Action",
                "NA_Sales": 1.0,
                "EU_Sales": 0.5,
                "JP_Sales": 0.3,
                "Other_Sales": 0.2,
                "Global_Sales": 2.0,
            },
            {
                "Name": "Game B",
                "Platform": "PS2",
                "Year": 2000,
                "Genre": "Sports",
                "NA_Sales": 0.5,
                "EU_Sales": 0.3,
                "JP_Sales": 0.1,
                "Other_Sales": 0.1,
                "Global_Sales": 1.0,
            },
            {
                "Name": "Game C",
                "Platform": "Wii",
                "Year": 2001,
                "Genre": "Action",
                "NA_Sales": 1.0,
                "EU_Sales": 1.0,
                "JP_Sales": 0.5,
                "Other_Sales": 0.5,
                "Global_Sales": 3.0,
            },
        ]
    )


def test_platform_sales_totals(
    sample_sales_data: pd.DataFrame,
) -> None:
    """Platform totals equal the sum of their game entry sales."""
    statistics = calculate_platform_statistics(
        sample_sales_data
    )

    ps2 = statistics.loc[
        statistics["Platform"] == "PS2"
    ].iloc[0]

    assert ps2["Game_Count"] == 2
    assert ps2["Total_Sales"] == pytest.approx(3.0)
    assert ps2["Average_Sales"] == pytest.approx(1.5)


def test_platform_sales_preserve_global_total(
    sample_sales_data: pd.DataFrame,
) -> None:
    """Aggregated platform sales preserve the dataset's global total."""
    statistics = calculate_platform_statistics(
        sample_sales_data
    )

    assert statistics["Total_Sales"].sum() == pytest.approx(6.0)


def test_regional_sales_totals(
    sample_sales_data: pd.DataFrame,
) -> None:
    """Regional sales totals match the known sample values."""
    statistics = calculate_regional_statistics(
        sample_sales_data
    )

    north_america = statistics.loc[
        statistics["Region"] == "North America"
    ].iloc[0]

    assert north_america["Total_Sales"] == pytest.approx(2.5)


def test_regional_shares_sum_to_100_percent(
    sample_sales_data: pd.DataFrame,
) -> None:
    """Recorded regional sales shares form a complete distribution."""
    statistics = calculate_regional_statistics(
        sample_sales_data
    )

    assert statistics["Sales_Share_Percent"].sum() == pytest.approx(
        100.0
    )


def test_genre_regional_sales(
    sample_sales_data: pd.DataFrame,
) -> None:
    """Genre aggregations correctly sum sales from multiple platforms."""
    statistics = calculate_genre_regional_statistics(
        sample_sales_data
    )

    action = statistics.loc[
        statistics["Genre"] == "Action"
    ].iloc[0]

    assert action["Game_Count"] == 2
    assert action["Global_Sales"] == pytest.approx(5.0)
    assert action["NA_Sales"] == pytest.approx(2.0)


def test_yearly_sales_aggregation(
    sample_sales_data: pd.DataFrame,
) -> None:
    """Sales are grouped according to game release year."""
    yearly = calculate_yearly_sales(
        sample_sales_data
    )

    assert yearly["Year"].tolist() == [2000, 2001]
    assert yearly["Global_Sales"].tolist() == pytest.approx(
        [3.0, 3.0]
    )


def test_yearly_percentage_change(
    sample_sales_data: pd.DataFrame,
) -> None:
    """Percentage changes compare consecutive release-year groups."""
    yearly = calculate_yearly_sales(
        sample_sales_data
    )

    changes = calculate_yearly_changes(yearly)

    assert pd.isna(changes.iloc[0]["Growth_Percent"])
    assert changes.iloc[1]["Growth_Percent"] == pytest.approx(0.0)


def test_yearly_percentage_change_handles_zero() -> None:
    """A zero-valued previous year produces an undefined change."""
    yearly = pd.DataFrame(
        {
            "Year": [2000, 2001],
            "Global_Sales": [0.0, 5.0],
        }
    )

    changes = calculate_yearly_changes(yearly)

    assert pd.isna(changes.iloc[1]["Growth_Percent"])
