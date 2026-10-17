
"""Data preparation and exploratory analysis for Game Sales Analytics."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


# Project paths
BASE_DIR = Path(__file__).resolve().parent

RAW_DATA_PATH = BASE_DIR / "data" / "raw" / "vgsales.csv"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
IMAGES_DIR = BASE_DIR / "images"

CLEAN_DATA_PATH = PROCESSED_DIR / "vgsales_clean.csv"
YEAR_DATA_PATH = PROCESSED_DIR / "vgsales_with_year.csv"


# Expected dataset schema
REQUIRED_COLUMNS = [
    "Rank",
    "Name",
    "Platform",
    "Year",
    "Genre",
    "Publisher",
    "NA_Sales",
    "EU_Sales",
    "JP_Sales",
    "Other_Sales",
    "Global_Sales",
]

SALES_COLUMNS = [
    "NA_Sales",
    "EU_Sales",
    "JP_Sales",
    "Other_Sales",
    "Global_Sales",
]


def load_dataset(file_path: Path) -> pd.DataFrame:
    """Load the source dataset and validate its required columns."""
    if not file_path.is_file():
        raise FileNotFoundError(
            f"Source dataset not found: {file_path}"
        )

    df = pd.read_csv(file_path)

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required dataset columns: {missing_columns}"
        )

    if df.empty:
        raise ValueError("The source dataset is empty.")

    return df


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Clean game records while preserving missing release years."""
    cleaned = df.copy()

    # Normalize numeric values before validating the dataset.
    numeric_columns = ["Rank", "Year", *SALES_COLUMNS]

    for column in numeric_columns:
        cleaned[column] = pd.to_numeric(
            cleaned[column],
            errors="coerce",
        )

    # A valid record requires identifiable game information and sales.
    required_values = [
        "Name",
        "Platform",
        "Genre",
        *SALES_COLUMNS,
    ]

    cleaned = cleaned.dropna(subset=required_values)

    # Exclude records containing invalid negative sales figures.
    valid_sales = cleaned[SALES_COLUMNS].ge(0).all(axis=1)
    cleaned = cleaned.loc[valid_sales].copy()

    # Standardize text fields.
    text_columns = ["Name", "Platform", "Genre"]

    for column in text_columns:
        cleaned[column] = cleaned[column].astype(str).str.strip()

    cleaned = cleaned.loc[
        cleaned[text_columns].ne("").all(axis=1)
    ].copy()

    # Retain records whose publisher is not available.
    cleaned["Publisher"] = (
        cleaned["Publisher"]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
        .replace("", "Unknown")
    )

    # Keep release years nullable instead of dropping entire records.
    cleaned["Year"] = cleaned["Year"].astype("Int64")

    cleaned = cleaned.drop_duplicates()

    return cleaned.reset_index(drop=True)


def create_year_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Return records with valid release years for temporal analysis."""
    year_df = df.dropna(subset=["Year"]).copy()

    # The original dataset represents historical game releases.
    year_df = year_df.loc[
        year_df["Year"].between(1980, 2016)
    ].copy()

    year_df["Year"] = year_df["Year"].astype(int)

    return year_df.reset_index(drop=True)


def print_dataset_summary(
    original: pd.DataFrame,
    cleaned: pd.DataFrame,
    year_data: pd.DataFrame,
) -> None:
    """Print dataset quality indicators and basic sales statistics."""
    print("\n" + "=" * 60)
    print("GAME SALES ANALYTICS - DATA PREPARATION")
    print("=" * 60)

    print(f"\nOriginal records: {len(original):,}")
    print(f"Cleaned records: {len(cleaned):,}")
    print(f"Records with valid release years: {len(year_data):,}")

    print("\nMissing values in cleaned dataset:")
    print(cleaned.isna().sum().to_string())

    print("\nGenre distribution:")
    print(cleaned["Genre"].value_counts().to_string())

    print("\nGlobal sales by genre (million copies):")

    genre_sales = (
        cleaned.groupby("Genre")["Global_Sales"]
        .sum()
        .sort_values(ascending=False)
    )

    print(genre_sales.round(2).to_string())

    print("\nNumeric summary:")
    print(cleaned[SALES_COLUMNS].describe().round(2).to_string())


def save_genre_charts(df: pd.DataFrame) -> None:
    """Generate static genre distribution and sales charts."""
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    genre_counts = df["Genre"].value_counts()

    genre_sales = (
        df.groupby("Genre")["Global_Sales"]
        .sum()
        .sort_values(ascending=False)
    )

    # Game-platform entry counts by genre.
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.bar(
        genre_counts.index,
        genre_counts.values,
        color="steelblue",
    )

    ax.set(
        title="Game Entries by Genre",
        xlabel="Genre",
        ylabel="Number of Game Entries",
    )

    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()

    fig.savefig(
        IMAGES_DIR / "genre_counts.png",
        dpi=300,
    )

    plt.close(fig)

    # Historical global sales aggregated by genre.
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.bar(
        genre_sales.index,
        genre_sales.values,
        color="seagreen",
    )

    ax.set(
        title="Historical Global Sales by Genre",
        xlabel="Genre",
        ylabel="Sales (Million Copies)",
    )

    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()

    fig.savefig(
        IMAGES_DIR / "genre_sales.png",
        dpi=300,
    )

    plt.close(fig)


def save_processed_datasets(
    cleaned: pd.DataFrame,
    year_data: pd.DataFrame,
) -> None:
    """Persist the cleaned datasets for downstream processing."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    cleaned.to_csv(
        CLEAN_DATA_PATH,
        index=False,
    )

    year_data.to_csv(
        YEAR_DATA_PATH,
        index=False,
    )


def main() -> None:
    """Run the complete data preparation and exploratory analysis."""
    original = load_dataset(RAW_DATA_PATH)

    cleaned = clean_dataset(original)
    year_data = create_year_dataset(cleaned)

    print_dataset_summary(
        original=original,
        cleaned=cleaned,
        year_data=year_data,
    )

    save_processed_datasets(
        cleaned=cleaned,
        year_data=year_data,
    )

    save_genre_charts(cleaned)

    print("\nData preparation completed successfully.")
    print(f"Cleaned dataset: {CLEAN_DATA_PATH}")
    print(f"Release-year dataset: {YEAR_DATA_PATH}")
    print(f"Charts directory: {IMAGES_DIR}")


if __name__ == "__main__":
    main()
