
"""Regional video game sales analysis for Game Sales Analytics.

This module analyzes recorded sales across geographic regions and
compares genre performance using the standardized cleaned dataset.
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

PROCESSED_DIR = BASE_DIR / "data" / "processed"
IMAGES_DIR = BASE_DIR / "images"

REGIONAL_OUTPUT_PATH = (
    PROCESSED_DIR / "regional_statistics.csv"
)

GENRE_OUTPUT_PATH = (
    PROCESSED_DIR / "genre_regional_statistics.csv"
)

REGION_LABELS = {
    "NA_Sales": "North America",
    "EU_Sales": "Europe",
    "JP_Sales": "Japan",
    "Other_Sales": "Other Regions",
}

REGION_COLORS = {
    "NA_Sales": "royalblue",
    "EU_Sales": "seagreen",
    "JP_Sales": "darkorange",
    "Other_Sales": "mediumpurple",
}

REGION_COLUMNS = list(REGION_LABELS.keys())

REQUIRED_COLUMNS = [
    "Genre",
    "Global_Sales",
    *REGION_COLUMNS,
]


# ---------------------------------------------------------------------
# Data loading and validation
# ---------------------------------------------------------------------

def load_regional_data(file_path: Path) -> pd.DataFrame:
    """Load and validate sales records for regional analysis."""
    if not file_path.is_file():
        raise FileNotFoundError(
            f"Cleaned dataset not found: {file_path}"
        )

    df = pd.read_csv(file_path)

    if df.empty:
        raise ValueError("The cleaned dataset is empty.")

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    validated = df[REQUIRED_COLUMNS].copy()

    sales_columns = [
        "Global_Sales",
        *REGION_COLUMNS,
    ]

    for column in sales_columns:
        validated[column] = pd.to_numeric(
            validated[column],
            errors="coerce",
        )

    if validated[sales_columns].isna().any().any():
        raise ValueError(
            "Sales columns contain missing or invalid values."
        )

    if validated[sales_columns].lt(0).any().any():
        raise ValueError(
            "Sales figures cannot be negative."
        )

    if validated["Genre"].isna().any():
        raise ValueError(
            "Genre information contains missing values."
        )

    validated["Genre"] = (
        validated["Genre"]
        .astype(str)
        .str.strip()
    )

    if validated["Genre"].eq("").any():
        raise ValueError(
            "Genre information cannot be empty."
        )

    return validated


# ---------------------------------------------------------------------
# Regional sales statistics
# ---------------------------------------------------------------------

def calculate_regional_statistics(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate recorded sales and shares for each region."""
    regional_totals = df[REGION_COLUMNS].sum()

    statistics = (
        regional_totals
        .rename("Total_Sales")
        .rename_axis("Region_Code")
        .reset_index()
    )

    statistics["Region"] = (
        statistics["Region_Code"]
        .map(REGION_LABELS)
    )

    total_recorded_sales = statistics["Total_Sales"].sum()

    if total_recorded_sales > 0:
        statistics["Sales_Share_Percent"] = (
            statistics["Total_Sales"]
            / total_recorded_sales
            * 100
        )
    else:
        statistics["Sales_Share_Percent"] = 0.0

    statistics = (
        statistics[
            [
                "Region",
                "Total_Sales",
                "Sales_Share_Percent",
            ]
        ]
        .sort_values(
            "Total_Sales",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    return statistics


# ---------------------------------------------------------------------
# Genre-level regional analysis
# ---------------------------------------------------------------------

def calculate_genre_regional_statistics(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Aggregate regional sales and game counts by genre."""
    genre_statistics = (
        df.groupby("Genre", as_index=False)
        .agg(
            Game_Count=("Global_Sales", "size"),
            Global_Sales=("Global_Sales", "sum"),
            NA_Sales=("NA_Sales", "sum"),
            EU_Sales=("EU_Sales", "sum"),
            JP_Sales=("JP_Sales", "sum"),
            Other_Sales=("Other_Sales", "sum"),
        )
        .sort_values(
            "Global_Sales",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    return genre_statistics


def calculate_top_genres_by_region(
    genre_statistics: pd.DataFrame,
    top_n: int = 5,
) -> dict[str, pd.DataFrame]:
    """Identify the highest-selling genres within each region."""
    if top_n < 1:
        raise ValueError(
            "The number of genres must be greater than zero."
        )

    results = {}

    for region_column in REGION_COLUMNS:
        results[region_column] = (
            genre_statistics[
                [
                    "Genre",
                    region_column,
                ]
            ]
            .nlargest(
                top_n,
                region_column,
            )
            .reset_index(drop=True)
        )

    return results


# ---------------------------------------------------------------------
# Regional visualizations
# ---------------------------------------------------------------------

def save_regional_sales_chart(
    statistics: pd.DataFrame,
    output_dir: Path,
) -> None:
    """Save a bar chart of recorded sales across regions."""
    chart_data = statistics.sort_values(
        "Total_Sales",
        ascending=True,
    )

    fig, ax = plt.subplots(figsize=(11, 6))

    ax.barh(
        chart_data["Region"],
        chart_data["Total_Sales"],
        color="cornflowerblue",
    )

    ax.set(
        title="Recorded Video Game Sales by Region",
        xlabel="Sales (Million Copies)",
        ylabel="Region",
    )

    ax.grid(
        axis="x",
        alpha=0.2,
    )

    fig.tight_layout()

    fig.savefig(
        output_dir / "regional_sales.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


def save_regional_share_chart(
    statistics: pd.DataFrame,
    output_dir: Path,
) -> None:
    """Visualize the distribution of recorded regional sales."""
    total_sales = statistics["Total_Sales"].sum()

    if total_sales <= 0:
        print(
            "Regional share chart skipped: "
            "no positive sales figures available."
        )
        return

    fig, ax = plt.subplots(figsize=(9, 7))

    ax.pie(
        statistics["Total_Sales"],
        labels=statistics["Region"],
        autopct="%1.1f%%",
        startangle=90,
        wedgeprops={
            "width": 0.4,
        },
    )

    ax.set_title(
        "Distribution of Recorded Regional Sales"
    )

    fig.tight_layout()

    fig.savefig(
        output_dir / "regional_sales_share.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


def save_genre_region_comparison(
    genre_statistics: pd.DataFrame,
    output_dir: Path,
) -> None:
    """Compare regional sales across video game genres."""
    chart_data = (
        genre_statistics
        .sort_values(
            "Global_Sales",
            ascending=False,
        )
        .set_index("Genre")
    )

    # Use the same four regions throughout the project.
    fig, ax = plt.subplots(figsize=(14, 7))

    chart_data[REGION_COLUMNS].plot(
        kind="bar",
        ax=ax,
        color=[
            REGION_COLORS[column]
            for column in REGION_COLUMNS
        ],
        width=0.8,
    )

    ax.set(
        title="Recorded Genre Sales by Region",
        xlabel="Genre",
        ylabel="Sales (Million Copies)",
    )

    ax.legend(
        [
            REGION_LABELS[column]
            for column in REGION_COLUMNS
        ],
        title="Region",
    )

    ax.tick_params(
        axis="x",
        rotation=45,
    )

    ax.grid(
        axis="y",
        alpha=0.2,
    )

    fig.tight_layout()

    fig.savefig(
        output_dir / "genre_region_comparison.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


# ---------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------

def print_regional_summary(
    df: pd.DataFrame,
    regional_statistics: pd.DataFrame,
    genre_statistics: pd.DataFrame,
) -> None:
    """Print regional sales totals and genre comparisons."""
    print("\n" + "=" * 60)
    print("GAME SALES ANALYTICS - REGIONAL ANALYSIS")
    print("=" * 60)

    print(f"\nAnalyzed game entries: {len(df):,}")

    print("\nRegional sales statistics:")
    print(
        regional_statistics
        .round(2)
        .to_string(index=False)
    )

    print("\nGlobal sales recorded in the dataset:")

    print(
        f"{df['Global_Sales'].sum():,.2f} million copies"
    )

    print("\nSum of regional sales:")

    print(
        f"{df[REGION_COLUMNS].sum().sum():,.2f} million copies"
    )

    print("\nSales by genre and region:")

    print(
        genre_statistics
        .round(2)
        .to_string(index=False)
    )

    top_genres = calculate_top_genres_by_region(
        genre_statistics,
        top_n=5,
    )

    for region_column, results in top_genres.items():
        region_name = REGION_LABELS[region_column]

        print(f"\nTop 5 genres in {region_name}:")

        print(
            results
            .round(2)
            .to_string(index=False)
        )


# ---------------------------------------------------------------------
# Data export
# ---------------------------------------------------------------------

def export_statistics(
    regional_statistics: pd.DataFrame,
    genre_statistics: pd.DataFrame,
) -> None:
    """Export regional and genre-level statistics to CSV."""
    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    regional_statistics.to_csv(
        REGIONAL_OUTPUT_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    genre_statistics.to_csv(
        GENRE_OUTPUT_PATH,
        index=False,
        encoding="utf-8-sig",
    )


# ---------------------------------------------------------------------
# Application entry point
# ---------------------------------------------------------------------

def main() -> None:
    """Execute regional sales analysis and generate outputs."""
    df = load_regional_data(DATA_PATH)

    regional_statistics = calculate_regional_statistics(
        df
    )

    genre_statistics = calculate_genre_regional_statistics(
        df
    )

    IMAGES_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    save_regional_sales_chart(
        regional_statistics,
        IMAGES_DIR,
    )

    save_regional_share_chart(
        regional_statistics,
        IMAGES_DIR,
    )

    save_genre_region_comparison(
        genre_statistics,
        IMAGES_DIR,
    )

    export_statistics(
        regional_statistics,
        genre_statistics,
    )

    print_regional_summary(
        df,
        regional_statistics,
        genre_statistics,
    )

    print("\nRegional analysis completed successfully.")
    print(f"Statistics exported to: {PROCESSED_DIR}")
    print(f"Charts saved to: {IMAGES_DIR}")

    print(
        "\nData limitation: Regional sales shares describe "
        "the available dataset, not the entire gaming market."
    )


if __name__ == "__main__":
    main()
