
"""SQL-based sales analysis for Game Sales Analytics.

This module executes predefined analytical queries against the
SQLite database and presents results as structured reports.

All sales figures represent historical estimates in millions
of copies. Game records refer to game-platform entries rather
than necessarily unique game titles.
"""

import sqlite3
from pathlib import Path
from typing import Any

import pandas as pd


# ---------------------------------------------------------------------
# Project configuration
# ---------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_PATH = BASE_DIR / "database" / "games.db"

TABLE_NAME = "games"

DEFAULT_LIMIT = 10


# ---------------------------------------------------------------------
# Database access and validation
# ---------------------------------------------------------------------

def connect_database(database_path: Path) -> sqlite3.Connection:
    """Open an existing SQLite database in read-only mode.

    Args:
        database_path: Absolute path to the SQLite database.

    Returns:
        An active read-only SQLite connection.

    Raises:
        FileNotFoundError: If the database does not exist.
        sqlite3.Error: If the database cannot be opened.
    """
    if not database_path.is_file():
        raise FileNotFoundError(
            f"SQLite database not found: {database_path}"
        )

    # Read-only access prevents analysis queries from modifying
    # the database or creating a new database file.
    database_uri = database_path.resolve().as_uri() + "?mode=ro"

    return sqlite3.connect(
        database_uri,
        uri=True,
    )


def validate_database(connection: sqlite3.Connection) -> None:
    """Verify that the required games table and columns exist."""
    table_query = """
        SELECT COUNT(*)
        FROM sqlite_master
        WHERE type = 'table'
          AND name = ?;
    """

    cursor = connection.execute(
        table_query,
        (TABLE_NAME,),
    )

    table_exists = cursor.fetchone()[0] > 0

    if not table_exists:
        raise ValueError(
            f"Required table '{TABLE_NAME}' was not found."
        )

    required_columns = {
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
    }

    # PRAGMA table_info returns the column definitions
    # of the validated, fixed table name.
    cursor = connection.execute(
        "PRAGMA table_info(games);"
    )

    existing_columns = {
        row[1]
        for row in cursor.fetchall()
    }

    missing_columns = (
        required_columns - existing_columns
    )

    if missing_columns:
        raise ValueError(
            "Database schema is incomplete. "
            f"Missing columns: {sorted(missing_columns)}"
        )


def execute_query(
    connection: sqlite3.Connection,
    query: str,
    parameters: tuple[Any, ...] = (),
) -> pd.DataFrame:
    """Execute a parameterized SQL query and return a DataFrame.

    Args:
        connection: Active SQLite database connection.
        query: SQL SELECT statement to execute.
        parameters: Values bound to SQL placeholders.

    Returns:
        Query results as a pandas DataFrame.
    """
    return pd.read_sql_query(
        sql=query,
        con=connection,
        params=parameters,
    )


# ---------------------------------------------------------------------
# Game-level queries
# ---------------------------------------------------------------------

def get_first_games(
    connection: sqlite3.Connection,
    limit: int = DEFAULT_LIMIT,
) -> pd.DataFrame:
    """Return the first game entries ordered by dataset rank."""
    if limit < 1:
        raise ValueError("The result limit must be positive.")

    query = """
        SELECT *
        FROM games
        ORDER BY Rank ASC
        LIMIT ?;
    """

    return execute_query(
        connection,
        query,
        (limit,),
    )


def get_top_games_by_platform(
    connection: sqlite3.Connection,
    platform: str,
    limit: int = DEFAULT_LIMIT,
) -> pd.DataFrame:
    """Return the highest-selling game entries for a platform."""
    if limit < 1:
        raise ValueError("The result limit must be positive.")

    query = """
        SELECT
            Name,
            Platform,
            Year,
            Global_Sales
        FROM games
        WHERE Platform = ?
        ORDER BY Global_Sales DESC
        LIMIT ?;
    """

    return execute_query(
        connection,
        query,
        (platform, limit),
    )


def get_top_global_games(
    connection: sqlite3.Connection,
    limit: int = DEFAULT_LIMIT,
) -> pd.DataFrame:
    """Return the highest-selling game-platform entries globally."""
    if limit < 1:
        raise ValueError("The result limit must be positive.")

    query = """
        SELECT
            Name,
            Platform,
            Genre,
            Global_Sales
        FROM games
        ORDER BY Global_Sales DESC
        LIMIT ?;
    """

    return execute_query(
        connection,
        query,
        (limit,),
    )


def get_filtered_games(
    connection: sqlite3.Connection,
    platform: str,
    genre: str,
    start_year: int,
    limit: int = DEFAULT_LIMIT,
) -> pd.DataFrame:
    """Return top-selling games matching platform, genre and year."""
    if limit < 1:
        raise ValueError("The result limit must be positive.")

    query = """
        SELECT
            Name,
            Platform,
            Year,
            Genre,
            Global_Sales
        FROM games
        WHERE Platform = ?
          AND Genre = ?
          AND Year >= ?
        ORDER BY Global_Sales DESC
        LIMIT ?;
    """

    return execute_query(
        connection,
        query,
        (
            platform,
            genre,
            start_year,
            limit,
        ),
    )


# ---------------------------------------------------------------------
# Genre-level queries
# ---------------------------------------------------------------------

def get_genre_sales(
    connection: sqlite3.Connection,
) -> pd.DataFrame:
    """Calculate game counts and total global sales by genre."""
    query = """
        SELECT
            Genre,
            COUNT(*) AS Game_Count,
            ROUND(SUM(Global_Sales), 2) AS Total_Sales
        FROM games
        GROUP BY Genre
        ORDER BY Total_Sales DESC;
    """

    return execute_query(
        connection,
        query,
    )


def get_genre_average_sales(
    connection: sqlite3.Connection,
) -> pd.DataFrame:
    """Calculate average global sales per game entry by genre."""
    query = """
        SELECT
            Genre,
            COUNT(*) AS Game_Count,
            ROUND(AVG(Global_Sales), 2) AS Average_Sales
        FROM games
        GROUP BY Genre
        ORDER BY Average_Sales DESC;
    """

    return execute_query(
        connection,
        query,
    )


def get_genres_with_minimum_games(
    connection: sqlite3.Connection,
    minimum_games: int = 1000,
) -> pd.DataFrame:
    """Return genre sales statistics above a minimum record count."""
    if minimum_games < 1:
        raise ValueError(
            "The minimum number of games must be positive."
        )

    query = """
        SELECT
            Genre,
            COUNT(*) AS Game_Count,
            ROUND(SUM(Global_Sales), 2) AS Total_Sales
        FROM games
        GROUP BY Genre
        HAVING COUNT(*) >= ?
        ORDER BY Total_Sales DESC;
    """

    return execute_query(
        connection,
        query,
        (minimum_games,),
    )


# ---------------------------------------------------------------------
# Publisher and regional queries
# ---------------------------------------------------------------------

def get_top_publishers(
    connection: sqlite3.Connection,
    limit: int = DEFAULT_LIMIT,
) -> pd.DataFrame:
    """Return publishers ranked by recorded global sales."""
    if limit < 1:
        raise ValueError("The result limit must be positive.")

    query = """
        SELECT
            Publisher,
            COUNT(*) AS Game_Count,
            ROUND(SUM(Global_Sales), 2) AS Total_Sales
        FROM games
        WHERE Publisher IS NOT NULL
          AND TRIM(Publisher) != ''
          AND Publisher != 'Unknown'
        GROUP BY Publisher
        ORDER BY Total_Sales DESC
        LIMIT ?;
    """

    return execute_query(
        connection,
        query,
        (limit,),
    )


def get_regional_sales(
    connection: sqlite3.Connection,
) -> pd.DataFrame:
    """Calculate recorded sales totals for all four regions."""
    query = """
        SELECT
            ROUND(SUM(NA_Sales), 2) AS North_America,
            ROUND(SUM(EU_Sales), 2) AS Europe,
            ROUND(SUM(JP_Sales), 2) AS Japan,
            ROUND(SUM(Other_Sales), 2) AS Other_Regions
        FROM games;
    """

    return execute_query(
        connection,
        query,
    )


# ---------------------------------------------------------------------
# Report formatting
# ---------------------------------------------------------------------

def print_report(
    title: str,
    results: pd.DataFrame,
) -> None:
    """Print a consistently formatted SQL analysis report."""
    print("\n" + "-" * 60)
    print(title)
    print("-" * 60)

    if results.empty:
        print("No matching records found.")
        return

    print(
        results.to_string(
            index=False,
        )
    )


# ---------------------------------------------------------------------
# Analysis workflow
# ---------------------------------------------------------------------

def run_analysis(
    connection: sqlite3.Connection,
) -> None:
    """Execute and display the project's nine SQL analyses."""
    reports = [
        (
            "1. FIRST 10 GAME ENTRIES",
            get_first_games(
                connection,
                limit=10,
            ),
        ),
        (
            "2. TOP 10 PLAYSTATION 2 GAMES",
            get_top_games_by_platform(
                connection,
                platform="PS2",
                limit=10,
            ),
        ),
        (
            "3. GLOBAL SALES BY GENRE",
            get_genre_sales(
                connection,
            ),
        ),
        (
            "4. TOP 10 GLOBAL GAME ENTRIES",
            get_top_global_games(
                connection,
                limit=10,
            ),
        ),
        (
            "5. AVERAGE SALES BY GENRE",
            get_genre_average_sales(
                connection,
            ),
        ),
        (
            "6. GENRES WITH AT LEAST 1,000 GAME ENTRIES",
            get_genres_with_minimum_games(
                connection,
                minimum_games=1000,
            ),
        ),
        (
            "7. TOP PS3 ACTION GAMES RELEASED SINCE 2010",
            get_filtered_games(
                connection,
                platform="PS3",
                genre="Action",
                start_year=2010,
                limit=10,
            ),
        ),
        (
            "8. TOP 10 PUBLISHERS BY GLOBAL SALES",
            get_top_publishers(
                connection,
                limit=10,
            ),
        ),
        (
            "9. RECORDED SALES BY REGION",
            get_regional_sales(
                connection,
            ),
        ),
    ]

    for title, results in reports:
        print_report(
            title,
            results,
        )


# ---------------------------------------------------------------------
# Application entry point
# ---------------------------------------------------------------------

def main() -> None:
    """Validate the database and run the SQL analysis reports."""
    print("=" * 60)
    print("GAME SALES ANALYTICS - SQL ANALYSIS")
    print("=" * 60)

    connection = connect_database(
        DATABASE_PATH
    )

    try:
        validate_database(
            connection
        )

        run_analysis(
            connection
        )

    finally:
        connection.close()

    print("\n" + "=" * 60)
    print("SQL ANALYSIS COMPLETED SUCCESSFULLY")
    print("=" * 60)

    print(
        "\nData limitation: Results describe historical "
        "sales recorded in the dataset, not the complete "
        "video game market."
    )


if __name__ == "__main__":
    main()
