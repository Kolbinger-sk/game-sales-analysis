
"""Interactive game explorer for the Game Sales Analytics dashboard.

This page supports game title searches, platform filtering,
sales comparisons, and CSV exports of historical game sales data.

Each record represents a game-platform entry rather than
necessarily a unique game title.
"""

import sqlite3
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ---------------------------------------------------------------------
# Module configuration
# ---------------------------------------------------------------------

DASHBOARD_DIR = Path(__file__).resolve().parent.parent

if str(DASHBOARD_DIR) not in sys.path:
    sys.path.insert(0, str(DASHBOARD_DIR))

from data_loader import load_data


PAGE_TITLE = "Games | Game Sales Analytics"

TOP_N = 10

REQUIRED_COLUMNS = [
    "Name",
    "Platform",
    "Year",
    "Genre",
    "Publisher",
    "Global_Sales",
]

DISPLAY_COLUMNS = [
    "Name",
    "Platform",
    "Year",
    "Genre",
    "Publisher",
    "Global_Sales",
]


# ---------------------------------------------------------------------
# Data validation
# ---------------------------------------------------------------------

def validate_game_data(df: pd.DataFrame) -> None:
    """Validate the schema required by the game explorer."""
    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required game columns: "
            f"{missing_columns}"
        )


# ---------------------------------------------------------------------
# Search and filtering
# ---------------------------------------------------------------------

def get_platform_options(df: pd.DataFrame) -> list[str]:
    """Return available platform names in alphabetical order."""
    platforms = (
        df["Platform"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    return sorted(
        platform
        for platform in platforms.unique()
        if platform
    )


def filter_games(
    df: pd.DataFrame,
    search_query: str = "",
    platform: str = "All Platforms",
) -> pd.DataFrame:
    """Filter game entries by title and selected platform.

    Search terms are treated as literal text rather than regular
    expressions. Matching is case-insensitive.
    """
    filtered = df.copy()

    query = search_query.strip()

    if query:
        matching_titles = (
            filtered["Name"]
            .astype("string")
            .str.contains(
                query,
                case=False,
                regex=False,
                na=False,
            )
        )

        filtered = filtered.loc[
            matching_titles
        ].copy()

    if platform != "All Platforms":
        filtered = filtered.loc[
            filtered["Platform"] == platform
        ].copy()

    return (
        filtered
        .sort_values(
            "Global_Sales",
            ascending=False,
        )
        .reset_index(drop=True)
    )


# ---------------------------------------------------------------------
# Summary metrics
# ---------------------------------------------------------------------

def calculate_game_metrics(
    df: pd.DataFrame,
) -> dict[str, float | int]:
    """Calculate summary statistics for the filtered game records."""
    return {
        "game_entries": len(df),
        "total_sales": float(df["Global_Sales"].sum()),
        "platform_count": int(df["Platform"].nunique()),
    }


def render_game_metrics(df: pd.DataFrame) -> None:
    """Display metrics for the current search results."""
    metrics = calculate_game_metrics(df)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Matching Game Entries",
            f"{metrics['game_entries']:,}",
        )

    with col2:
        st.metric(
            "Recorded Global Sales (Million Copies)",
            f"{metrics['total_sales']:,.2f}",
        )

    with col3:
        st.metric(
            "Gaming Platforms",
            f"{metrics['platform_count']:,}",
        )


# ---------------------------------------------------------------------
# Chart preparation
# ---------------------------------------------------------------------

def calculate_top_games(
    df: pd.DataFrame,
    limit: int = TOP_N,
) -> pd.DataFrame:
    """Return the highest-selling game-platform entries."""
    if limit < 1:
        raise ValueError(
            "The result limit must be greater than zero."
        )

    top_games = (
        df.nlargest(
            limit,
            "Global_Sales",
        )
        .copy()
    )

    top_games["Game_Label"] = (
        top_games["Name"].astype(str)
        + " ("
        + top_games["Platform"].astype(str)
        + ")"
    )

    return top_games


def render_top_games_chart(df: pd.DataFrame) -> None:
    """Display a horizontal sales chart for the top game entries."""
    st.subheader("🏆 Top 10 Game Entries")

    top_games = calculate_top_games(df)

    if top_games.empty:
        st.info(
            "No game entries are available for visualization."
        )
        return

    # Unique labels prevent Plotly from merging equally named entries.
    top_games["Chart_Label"] = [
        f"{label} [{index + 1}]"
        for index, label in enumerate(top_games["Game_Label"])
    ]

    fig = px.bar(
        top_games,
        x="Global_Sales",
        y="Chart_Label",
        orientation="h",
        color="Global_Sales",
        title="Highest-Selling Game-Platform Entries",
        labels={
            "Global_Sales": "Recorded Sales (Million Copies)",
            "Chart_Label": "Game",
        },
        hover_data={
            "Name": True,
            "Platform": True,
            "Genre": True,
        },
    )

    fig.update_yaxes(
        categoryorder="total ascending"
    )

    fig.update_layout(
        height=550,
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20,
        ),
    )

    st.plotly_chart(
        fig,
        width="stretch",
    )


# ---------------------------------------------------------------------
# Results table and CSV export
# ---------------------------------------------------------------------

def prepare_results_table(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare the filtered results for tabular presentation."""
    results = df[DISPLAY_COLUMNS].copy()

    results = results.rename(
        columns={
            "Name": "Game",
            "Platform": "Platform",
            "Year": "Release Year",
            "Genre": "Genre",
            "Publisher": "Publisher",
            "Global_Sales": "Global Sales (Million Copies)",
        }
    )

    return results


def prepare_csv_export(df: pd.DataFrame) -> bytes:
    """Encode filtered game records as an Excel-compatible CSV."""
    return (
        df[DISPLAY_COLUMNS]
        .to_csv(
            index=False,
        )
        .encode("utf-8-sig")
    )


def render_results_table(df: pd.DataFrame) -> None:
    """Display the filtered game entries in an interactive table."""
    st.subheader("📋 Search Results")

    results = prepare_results_table(df)

    st.dataframe(
        results,
        width="stretch",
        hide_index=True,
    )

    st.caption(
        f"Showing {len(results):,} game-platform entries."
    )


def render_csv_download(df: pd.DataFrame) -> None:
    """Provide a download of the current filtered dataset."""
    st.subheader("📥 Download Search Results")

    csv_data = prepare_csv_export(df)

    st.download_button(
        label="Download Filtered Games (CSV)",
        data=csv_data,
        file_name="game_sales_filtered.csv",
        mime="text/csv",
    )


# ---------------------------------------------------------------------
# Page presentation
# ---------------------------------------------------------------------

def render_header() -> None:
    """Display the page heading and search description."""
    st.title("🎮 Game Explorer")

    st.write(
        "Search historical video game sales records, "
        "filter by platform, and compare recorded global sales."
    )

    st.caption(
        "Each entry represents a specific game-platform combination."
    )

    st.divider()


def render_filters(
    df: pd.DataFrame,
) -> tuple[str, str]:
    """Render the game title search and platform selection controls."""
    st.subheader("🔎 Search and Filters")

    col1, col2 = st.columns(
        [2, 1]
    )

    with col1:
        search_query = st.text_input(
            "Search by Game Title",
            placeholder="e.g. Mario, Zelda, Grand Theft Auto",
        )

    with col2:
        selected_platform = st.selectbox(
            "Gaming Platform",
            ["All Platforms", *get_platform_options(df)],
        )

    return search_query, selected_platform


def render_footer() -> None:
    """Display the dataset scope and interpretation notes."""
    st.divider()

    st.caption(
        "Game Sales Analytics | Historical Video Game Sales Dataset "
        "| Sales in Millions of Copies"
    )

    st.caption(
        "The dataset is historical and does not represent "
        "current market-wide sales statistics."
    )


# ---------------------------------------------------------------------
# Application entry point
# ---------------------------------------------------------------------

def main() -> None:
    """Render the complete game explorer dashboard page."""
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon="🎮",
        layout="wide",
    )

    render_header()

    try:
        df = load_data()

        validate_game_data(df)

    except (
        FileNotFoundError,
        sqlite3.Error,
        OSError,
        ValueError,
    ) as error:
        st.error(
            f"Unable to load game sales data: {error}"
        )
        st.stop()

    if df.empty:
        st.warning(
            "The database does not contain any game records."
        )
        st.stop()

    search_query, selected_platform = render_filters(df)

    filtered_df = filter_games(
        df,
        search_query=search_query,
        platform=selected_platform,
    )

    if filtered_df.empty:
        st.info(
            "No games match the selected search criteria. "
            "Try another title or platform."
        )
        return

    st.divider()

    render_game_metrics(filtered_df)

    st.divider()

    render_top_games_chart(filtered_df)

    st.divider()

    render_results_table(filtered_df)

    render_csv_download(filtered_df)

    render_footer()


if __name__ == "__main__":
    main()
