
"""Create and validate the SQLite database for Game Sales Analytics."""

import sqlite3
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "data" / "processed" / "vgsales_clean.csv"
DATABASE_PATH = BASE_DIR / "database" / "games.db"

TABLE_NAME = "games"

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


def load_cleaned_data(file_path: Path) -> pd.DataFrame:
    """Load the cleaned dataset and validate its structure."""
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

    return df


def validate_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    """Validate sales values and normalize numeric column types."""
    validated = df.copy()

    for column in SALES_COLUMNS:
        validated[column] = pd.to_numeric(
            validated[column],
            errors="coerce",
        )

    if validated[SALES_COLUMNS].isna().any().any():
        raise ValueError(
            "The dataset contains missing or invalid sales values."
        )

    if validated[SALES_COLUMNS].lt(0).any().any():
        raise ValueError(
            "The dataset contains negative sales values."
        )

    validated["Year"] = pd.to_numeric(
        validated["Year"],
        errors="coerce",
    )

    return validated


def create_database(
    df: pd.DataFrame,
    database_path: Path,
) -> None:
    """Replace the games table with the validated dataset."""
    database_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(database_path)

    try:
        df.to_sql(
            name=TABLE_NAME,
            con=connection,
            if_exists="replace",
            index=False,
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def verify_database(
    database_path: Path,
    expected_records: int,
) -> None:
    """Verify record counts and essential database statistics."""
    connection = sqlite3.connect(database_path)

    try:
        query = """
            SELECT
                COUNT(*) AS record_count,
                COUNT(DISTINCT Platform) AS platform_count,
                COUNT(DISTINCT Genre) AS genre_count,
                COUNT(Year) AS records_with_year,
                SUM(Global_Sales) AS total_global_sales
            FROM games;
        """

        result = pd.read_sql_query(
            query,
            connection,
        )

    finally:
        connection.close()

    actual_records = int(
        result.loc[0, "record_count"]
    )

    if actual_records != expected_records:
        raise ValueError(
            "Database verification failed: "
            f"expected {expected_records} records, "
            f"found {actual_records}."
        )

    print("\nDatabase verification")
    print("-" * 50)

    print(f"Records: {actual_records:,}")

    print(
        "Platforms:",
        int(result.loc[0, "platform_count"]),
    )

    print(
        "Genres:",
        int(result.loc[0, "genre_count"]),
    )

    print(
        "Records with release year:",
        int(result.loc[0, "records_with_year"]),
    )

    print(
        "Global sales (million copies):",
        f"{result.loc[0, 'total_global_sales']:,.2f}",
    )


def main() -> None:
    """Build and verify the SQLite database."""
    print("=" * 60)
    print("GAME SALES ANALYTICS - DATABASE SETUP")
    print("=" * 60)

    df = load_cleaned_data(DATA_PATH)

    validated_df = validate_sales_data(df)

    print(f"\nSource records: {len(validated_df):,}")

    create_database(
        df=validated_df,
        database_path=DATABASE_PATH,
    )

    verify_database(
        database_path=DATABASE_PATH,
        expected_records=len(validated_df),
    )

    print("\nDatabase setup completed successfully.")
    print(f"Database location: {DATABASE_PATH}")


if __name__ == "__main__":
    main()
