
"""Release-year-based sales analysis for Game Sales Analytics.

This module analyzes historical video game sales grouped by release year.
The dataset contains estimated lifetime sales, not annual transactions.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


# ---------------------------------------------------------------------
# Project configuration
# ---------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "vgsales_with_year.csv"
)

OUTPUT_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "yearly_sales.csv"
)

IMAGES_DIR = BASE_DIR / "images"

START_YEAR = 1980
END_YEAR = 2016

REGION_COLUMNS = [
    "NA_Sales",
    "EU_Sales",
    "JP_Sales",
    "Other_Sales",
]

REQUIRED_COLUMNS = [
    "Year",
    "Global_Sales",
    *REGION_COLUMNS,
]

REGION_LABELS = {
    "NA_Sales": "North America",
    "EU_Sales": "Europe",
    "JP_Sales": "Japan",
    "Other_Sales": "Other Regions",
}


# ---------------------------------------------------------------------
# Data loading and validation
# ---------------------------------------------------------------------

def load_sales_data(file_path: Path) -> pd.DataFrame:
    """Load and validate sales records with known release years."""
    if not file_path.is_file():
        raise FileNotFoundError(
            f"Release-year dataset not found: {file_path}"
        )

    df = pd.read_csv(file_path)

    if df.empty:
        raise ValueError("The release-year dataset is empty.")

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    validated = df.copy()

    for column in REQUIRED_COLUMNS:
        validated[column] = pd.to_numeric(
            validated[column],
            errors="coerce",
        )

    if validated[REQUIRED_COLUMNS].isna().any().any():
        raise ValueError(
            "The dataset contains missing or invalid numeric values."
        )

    sales_columns = [
        "Global_Sales",
        *REGION_COLUMNS,
    ]

    if validated[sales_columns].lt(0).any().any():
        raise ValueError(
            "The dataset contains negative sales values."
        )

    if not validated["Year"].between(
        START_YEAR,
        END_YEAR,
    ).all():
        raise ValueError(
            "Release years fall outside the configured analysis period."
        )

    if not validated["Year"].mod(1).eq(0).all():
        raise ValueError(
            "The dataset contains non-integer release years."
        )

    validated["Year"] = validated["Year"].astype(int)

    return validated


# ---------------------------------------------------------------------
# Sales aggregation
# ---------------------------------------------------------------------

def calculate_yearly_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate recorded global sales by game release year."""
    yearly_sales = (
        df.groupby("Year", as_index=False)["Global_Sales"]
        .sum()
        .sort_values("Year")
        .reset_index(drop=True)
    )

    return yearly_sales


def calculate_yearly_regional_sales(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Aggregate regional sales by game release year."""
    yearly_regions = (
        df.groupby("Year", as_index=False)[REGION_COLUMNS]
        .sum()
        .sort_values("Year")
        .reset_index(drop=True)
    )

    return yearly_regions


def calculate_yearly_changes(
    yearly_sales: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate relative changes between consecutive release-year groups.

    Undefined percentage changes are retained as missing values when
    the preceding release-year group's sales equal zero.
    """
    result = yearly_sales.copy()

    previous_sales = result["Global_Sales"].shift(1)

    valid_previous_sales = previous_sales.replace(
        0,
        float("nan"),
    )

    result["Growth_Percent"] = (
        (
            result["Global_Sales"] - previous_sales
        )
        / valid_previous_sales
        * 100
    )

    return result


# ---------------------------------------------------------------------
# Visualization
# ---------------------------------------------------------------------

def save_global_sales_chart(
    yearly_sales: pd.DataFrame,
) -> None:
    """Save global sales aggregated by game release year."""
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(
        yearly_sales["Year"],
        yearly_sales["Global_Sales"],
        marker="o",
        linewidth=2,
        color="royalblue",
    )

    ax.set(
        title="Recorded Global Sales by Game Release Year",
        xlabel="Game Release Year",
        ylabel="Recorded Sales (Million Copies)",
    )

    ax.grid(alpha=0.3)

    fig.tight_layout()

    fig.savefig(
        IMAGES_DIR / "yearly_global_sales.png",
        dpi=300,
    )

    plt.close(fig)


def save_regional_sales_chart(
    yearly_regions: pd.DataFrame,
) -> None:
    """Save regional sales aggregated by game release year."""
    fig, ax = plt.subplots(figsize=(12, 6))

    colors = {
        "NA_Sales": "royalblue",
        "EU_Sales": "seagreen",
        "JP_Sales": "darkorange",
        "Other_Sales": "mediumpurple",
    }

    for column in REGION_COLUMNS:
        ax.plot(
            yearly_regions["Year"],
            yearly_regions[column],
            label=REGION_LABELS[column],
            color=colors[column],
            linewidth=2,
        )

    ax.set(
        title="Recorded Regional Sales by Game Release Year",
        xlabel="Game Release Year",
        ylabel="Recorded Sales (Million Copies)",
    )

    ax.legend()
    ax.grid(alpha=0.3)

    fig.tight_layout()

    fig.savefig(
        IMAGES_DIR / "yearly_regional_sales.png",
        dpi=300,
    )

    plt.close(fig)


def save_growth_chart(
    yearly_sales: pd.DataFrame,
) -> None:
    """Save percentage changes between release-year sales groups."""
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.bar(
        yearly_sales["Year"],
        yearly_sales["Growth_Percent"],
        color="mediumpurple",
    )

    ax.axhline(
        y=0,
        color="black",
        linewidth=1,
    )

    ax.set(
        title="Change in Recorded Sales Between Release-Year Groups",
        xlabel="Game Release Year",
        ylabel="Change from Previous Release-Year Group (%)",
    )

    ax.grid(
        axis="y",
        alpha=0.3,
    )

    fig.tight_layout()

    fig.savefig(
        IMAGES_DIR / "yearly_sales_growth.png",
        dpi=300,
    )

    plt.close(fig)


# ---------------------------------------------------------------------
# Reporting and exports
# ---------------------------------------------------------------------

def print_analysis_summary(
    df: pd.DataFrame,
    yearly_sales: pd.DataFrame,
    yearly_regions: pd.DataFrame,
) -> None:
    """Print release-year sales statistics and regional comparisons."""
    print("\n" + "=" * 60)
    print("GAME SALES ANALYTICS - RELEASE YEAR ANALYSIS")
    print("=" * 60)

    print(f"\nAnalyzed records: {len(df):,}")

    print(
        "Release-year range: "
        f"{df['Year'].min()} - {df['Year'].max()}"
    )

    print("\nGlobal sales by release year:")
    print(
        yearly_sales[
            ["Year", "Global_Sales"]
        ].round(2).to_string(index=False)
    )

    print("\nTop 10 release-year groups by recorded sales:")

    top_years = (
        yearly_sales
        .nlargest(10, "Global_Sales")
    )

    print(
        top_years[
            ["Year", "Global_Sales"]
        ].round(2).to_string(index=False)
    )

    print("\nRegional sales by release year:")
    print(
        yearly_regions.round(2).to_string(index=False)
    )

    print("\nPercentage changes between release-year groups:")
    print(
        yearly_sales[
            ["Year", "Growth_Percent"]
        ].round(2).to_string(index=False)
    )


def export_yearly_sales(
    yearly_sales: pd.DataFrame,
    output_path: Path,
) -> None:
    """Export aggregated yearly sales and percentage changes."""
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    yearly_sales.to_csv(
        output_path,
        index=False,
    )


# ---------------------------------------------------------------------
# Application entry point
# ---------------------------------------------------------------------

def main() -> None:
    """Run release-year aggregation, reporting, and visualization."""
    df = load_sales_data(DATA_PATH)

    yearly_sales = calculate_yearly_sales(df)

    yearly_regions = calculate_yearly_regional_sales(df)

    yearly_sales = calculate_yearly_changes(
        yearly_sales
    )

    IMAGES_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    save_global_sales_chart(yearly_sales)

    save_regional_sales_chart(yearly_regions)

    save_growth_chart(yearly_sales)

    export_yearly_sales(
        yearly_sales,
        OUTPUT_PATH,
    )

    print_analysis_summary(
        df,
        yearly_sales,
        yearly_regions,
    )

    print("\nRelease-year analysis completed successfully.")
    print(f"Results exported to: {OUTPUT_PATH}")
    print(f"Charts saved to: {IMAGES_DIR}")

    print(
        "\nData limitation: Sales are grouped by game release year. "
        "They do not represent transactions occurring in that year."
    )


if __name__ == "__main__":
    main()
