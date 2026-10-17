
"""Platform-level sales analysis for Game Sales Analytics.

This module evaluates historical video game sales across gaming
platforms using the standardized cleaned dataset.
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
    / "vgsales_clean.csv"
)

IMAGES_DIR = BASE_DIR / "images"

OUTPUT_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "platform_statistics.csv"
)

REQUIRED_COLUMNS = [
    "Platform",
    "Global_Sales",
]

TOP_N = 10


# ---------------------------------------------------------------------
# Data loading and validation
# ---------------------------------------------------------------------

def load_platform_data(file_path: Path) -> pd.DataFrame:
    """Load and validate records required for platform analysis."""
    if not file_path.is_file():
        raise FileNotFoundError(
            f"Cleaned dataset not found: {file_path}"
        )

    df = pd.read_csv(file_path)

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    if df.empty:
        raise ValueError("The cleaned dataset is empty.")

    validated = df[REQUIRED_COLUMNS].copy()

    validated["Global_Sales"] = pd.to_numeric(
        validated["Global_Sales"],
        errors="coerce",
    )

    if validated["Platform"].isna().any():
        raise ValueError(
            "Platform identifiers contain missing values."
        )

    if validated["Global_Sales"].isna().any():
        raise ValueError(
            "Global sales contain missing or invalid values."
        )

    if validated["Global_Sales"].lt(0).any():
        raise ValueError(
            "Global sales cannot be negative."
        )

    validated["Platform"] = (
        validated["Platform"]
        .astype(str)
        .str.strip()
    )

    if validated["Platform"].eq("").any():
        raise ValueError(
            "Platform identifiers cannot be empty."
        )

    return validated


# ---------------------------------------------------------------------
# Platform statistics
# ---------------------------------------------------------------------

def calculate_platform_statistics(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Aggregate game counts and sales statistics by platform."""
    statistics = (
        df.groupby("Platform", as_index=False)
        .agg(
            Game_Count=("Global_Sales", "size"),
            Total_Sales=("Global_Sales", "sum"),
            Average_Sales=("Global_Sales", "mean"),
            Median_Sales=("Global_Sales", "median"),
        )
        .sort_values(
            "Total_Sales",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    return statistics


def get_top_platforms(
    statistics: pd.DataFrame,
    limit: int = TOP_N,
) -> pd.DataFrame:
    """Return the platforms with the highest recorded sales."""
    if limit < 1:
        raise ValueError(
            "The platform limit must be greater than zero."
        )

    return statistics.nlargest(
        limit,
        "Total_Sales",
    ).copy()


# ---------------------------------------------------------------------
# Visualizations
# ---------------------------------------------------------------------

def save_total_sales_chart(
    top_platforms: pd.DataFrame,
    output_dir: Path,
) -> None:
    """Save a ranking of platforms by total recorded global sales."""
    fig, ax = plt.subplots(figsize=(12, 7))

    chart_data = top_platforms.sort_values(
        "Total_Sales",
        ascending=True,
    )

    ax.barh(
        chart_data["Platform"],
        chart_data["Total_Sales"],
        color="royalblue",
    )

    ax.set(
        title="Top 10 Gaming Platforms by Recorded Global Sales",
        xlabel="Sales (Million Copies)",
        ylabel="Gaming Platform",
    )

    ax.grid(
        axis="x",
        alpha=0.2,
    )

    fig.tight_layout()

    fig.savefig(
        output_dir / "top_10_platforms.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


def save_average_sales_chart(
    statistics: pd.DataFrame,
    output_dir: Path,
) -> None:
    """Visualize average sales among platforms with sufficient records."""
    # A minimum sample size reduces misleading comparisons
    # driven by platforms with very few game entries.
    minimum_games = 30

    eligible_platforms = statistics.loc[
        statistics["Game_Count"] >= minimum_games
    ].copy()

    if eligible_platforms.empty:
        print(
            "Average sales chart skipped: "
            "no platform meets the minimum sample size."
        )
        return

    chart_data = (
        eligible_platforms
        .nlargest(TOP_N, "Average_Sales")
        .sort_values("Average_Sales")
    )

    fig, ax = plt.subplots(figsize=(12, 7))

    ax.barh(
        chart_data["Platform"],
        chart_data["Average_Sales"],
        color="seagreen",
    )

    ax.set(
        title="Average Sales per Game Entry by Platform",
        xlabel="Average Sales (Million Copies)",
        ylabel="Gaming Platform",
    )

    ax.grid(
        axis="x",
        alpha=0.2,
    )

    fig.tight_layout()

    fig.savefig(
        output_dir / "platform_average_sales.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


# ---------------------------------------------------------------------
# Reporting and export
# ---------------------------------------------------------------------

def print_platform_summary(
    df: pd.DataFrame,
    statistics: pd.DataFrame,
) -> None:
    """Print platform-level summary metrics and ranking tables."""
    print("\n" + "=" * 60)
    print("GAME SALES ANALYTICS - PLATFORM ANALYSIS")
    print("=" * 60)

    print(f"\nGame-platform entries: {len(df):,}")

    print(
        "Unique gaming platforms:",
        df["Platform"].nunique(),
    )

    print(
        "Total recorded global sales (million copies):",
        f"{df['Global_Sales'].sum():,.2f}",
    )

    print("\nTop 10 platforms by total sales:")

    print(
        statistics.head(TOP_N)
        .round(3)
        .to_string(index=False)
    )

    print("\nComplete platform statistics:")

    print(
        statistics.round(3).to_string(index=False)
    )


def export_platform_statistics(
    statistics: pd.DataFrame,
    output_path: Path,
) -> None:
    """Export platform-level statistics as a UTF-8 CSV file."""
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    statistics.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
    )


# ---------------------------------------------------------------------
# Application entry point
# ---------------------------------------------------------------------

def main() -> None:
    """Run platform sales aggregation, reporting, and visualization."""
    df = load_platform_data(DATA_PATH)

    statistics = calculate_platform_statistics(df)

    top_platforms = get_top_platforms(
        statistics,
        limit=TOP_N,
    )

    IMAGES_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    save_total_sales_chart(
        top_platforms,
        IMAGES_DIR,
    )

    save_average_sales_chart(
        statistics,
        IMAGES_DIR,
    )

    export_platform_statistics(
        statistics,
        OUTPUT_PATH,
    )

    print_platform_summary(
        df,
        statistics,
    )

    print("\nPlatform analysis completed successfully.")
    print(f"Statistics exported to: {OUTPUT_PATH}")
    print(f"Charts saved to: {IMAGES_DIR}")


if __name__ == "__main__":
    main()
