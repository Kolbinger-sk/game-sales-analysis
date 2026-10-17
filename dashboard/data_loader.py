
"""Centralized SQLite data access for the Game Sales Analytics dashboard.

The module provides validated, cached access to the historical video
game sales dataset. Database connections are opened in read-only mode.
"""

import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st


# ---------------------------------------------------------------------
# Project configuration
# ---------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_PATH = BASE_DIR / "database" / "games.db"

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

CACHE_TTL_SECONDS = 300


# ---------------------------------------------------------------------
# Database validation
# ---------------------------------------------------------------------

def validate_database_path(database_path: Path) -> None:
    """Verify that the configured SQLite database file exists."""
    if not database_path.is_file():
        raise FileNotFoundError(
            f"SQLite database not found: {database_path}. "
            "Run 'python src/database_setup.py' first."
        )


def validate_sales_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Validate the database schema and normalize sales data types.

    Args:
        df: Raw DataFrame loaded from the SQLite games table.

    Returns:
        DataFrame with validated numeric sales columns and nullable
        integer release years.

    Raises:
        sqlite3.DatabaseError: If required columns or values are invalid.
    """
    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise sqlite3.DatabaseError(
            "The games table is missing required columns: "
            f"{missing_columns}"
        )

    if df.empty:
        return df

    validated = df.copy()

    for column in SALES_COLUMNS:
        validated[column] = pd.to_numeric(
            validated[column],
            errors="coerce",
        )

    if validated[SALES_COLUMNS].isna().any().any():
        raise sqlite3.DatabaseError(
            "The database contains missing or invalid sales values."
        )

    if validated[SALES_COLUMNS].lt(0).any().any():
        raise sqlite3.DatabaseError(
            "The database contains negative sales values."
        )

    release_years = pd.to_numeric(
        validated["Year"],
        errors="coerce",
    )

    # Missing release years are valid for general sales analysis.
    # Non-integer years are rejected to preserve the expected schema.
    non_integer_years = (
        release_years.notna()
        & release_years.mod(1).ne(0)
    )

    if non_integer_years.any():
        raise sqlite3.DatabaseError(
            "The database contains non-integer release years."
        )

    validated["Year"] = release_years.astype("Int64")

    return validated


# ---------------------------------------------------------------------
# Cached database access
# ---------------------------------------------------------------------

@st.cache_data(
    ttl=CACHE_TTL_SECONDS,
    show_spinner=False,
)
def _load_data_cached(
    database_uri: str,
    modified_ns: int,
    file_size: int,
) -> pd.DataFrame:
    """Read and validate the games table using a versioned cache key.

    The modification timestamp and file size are included in the cache
    key so that database updates invalidate previously cached data.
    """
    connection = sqlite3.connect(
        database_uri,
        uri=True,
    )

    try:
        df = pd.read_sql_query(
            "SELECT * FROM games;",
            connection,
        )

    finally:
        connection.close()

    return validate_sales_dataframe(df)


# ---------------------------------------------------------------------
# Public data access interface
# ---------------------------------------------------------------------

def load_data() -> pd.DataFrame:
    """Load the current games dataset from the SQLite database.

    Returns:
        Validated video game sales records as a pandas DataFrame.

    Raises:
        FileNotFoundError: If the database file does not exist.
        sqlite3.Error: If the database cannot be queried or validated.
        OSError: If database file metadata cannot be accessed.
    """
    validate_database_path(DATABASE_PATH)

    database_path = DATABASE_PATH.resolve()

    file_stats = database_path.stat()

    # A read-only URI prevents accidental modifications and avoids
    # silently creating an empty database when a path is incorrect.
    database_uri = database_path.as_uri() + "?mode=ro"

    return _load_data_cached(
        database_uri=database_uri,
        modified_ns=file_stats.st_mtime_ns,
        file_size=file_stats.st_size,
    )
