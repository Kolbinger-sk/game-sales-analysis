
"""Overview dashboard for the Game Sales Analytics application.

The overview presents historical video game sales statistics,
genre and platform rankings, and sales grouped by release year.

Sales figures are expressed in millions of copies and reflect
the historical records available in the source dataset.
"""

import sqlite3

import pandas as pd
import plotly.express as px
import streamlit as st

from data_loader import load_data


# ---------------------------------------------------------------------
# Application configuration
# ---------------------------------------------------------------------

PAGE_TITLE = "Game Sales Analytics | Overview"

REQUIRED_COLUMNS = [
    "Name",
    "Platform",
    "Genre",
    "Year",
    "Global_Sales",
]

TOP_N = 10

START_YEAR = 1980
END_YEAR = 2016

NAVIGATION_PAGES = [
    {
        "path": "pages/1_Games.py",
        "label": "Games – Game Explorer",
        "icon": "🎮",
        "description": "Search and compare individual game entries.",
    },
    {
        "path": "pages/2_Genres.py",
        "label": "Genres – Genre Analysis",
        "icon": "📊",
        "description": "Explore sales performance across genres.",
    },
    {
        "path": "pages/3_Platforms.py",
        "label": "Platforms – Platform Analysis",
        "icon": "🕹️",
        "description": "Compare gaming platforms and sales metrics.",
    },
    {
        "path": "pages/4_Regions.py",
        "label": "Regions – Regional Analysis",
        "icon": "🌍",
        "description": "Analyze regional sales distributions.",
    },
    {
        "path": "pages/5_Predictions.py",
        "label": "Predictions – Machine Learning",
        "icon": "🤖",
        "description": "Explore experimental sales predictions.",
    },
]


# ---------------------------------------------------------------------
# Data validation
# ---------------------------------------------------------------------

def validate_dashboard_data(df: pd.DataFrame) -> None:
    """Validate the dataset required by the dashboard overview.

    Args:
        df: Game sales records loaded from SQLite.

    Raises:
        ValueError: If the dataset is empty or required columns
            are missing.
    """
    if df.empty:
        raise ValueError(
            "The database does not contain any game records."
        )

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Required dashboard columns are missing: "
            f"{missing_columns}"
        )


# ---------------------------------------------------------------------
# Overview metrics
# ---------------------------------------------------------------------

def calculate_overview_metrics(df: pd.DataFrame) -> dict:
    """Calculate the primary dataset-level overview metrics."""
    return {
        "game_entries": len(df),
        "platforms": df["Platform"].nunique(),
        "genres": df["Genre"].nunique(),
        "global_sales": df["Global_Sales"].sum(),
    }


def render_overview_metrics(df: pd.DataFrame) -> None:
    """Display the primary metrics in a four-column layout."""
    metrics = calculate_overview_metrics(df)

    st.subheader("📊 Dashboard Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Game Entries",
            value=f"{metrics['game_entries']:,}",
        )

    with col2:
        st.metric(
            label="Gaming Platforms",
            value=f"{metrics['platforms']:,}",
        )

    with col3:
        st.metric(
            label="Genres",
            value=f"{metrics['genres']:,}",
        )

    with col4:
        st.metric(
            label="Global Sales (Million Copies)",
            value=f"{metrics['global_sales']:,.2f}",
        )


# ---------------------------------------------------------------------
# Sales aggregation
# ---------------------------------------------------------------------

def calculate_top_sales(
    df: pd.DataFrame,
    group_column: str,
    limit: int = TOP_N,
) -> pd.DataFrame:
    """Aggregate and rank global sales by a categorical feature.

    Args:
        df: Validated game sales dataset.
        group_column: Column used to group the sales records.
        limit: Maximum number of categories returned.

    Returns:
        A DataFrame sorted by total recorded global sales.
    """
    if group_column not in {"Genre", "Platform"}:
        raise ValueError(
            f"Unsupported grouping column: {group_column}"
        )

    if limit < 1:
        raise ValueError(
            "The result limit must be greater than zero."
        )

    return (
        df.groupby(group_column, as_index=False)["Global_Sales"]
        .sum()
        .sort_values(
            "Global_Sales",
            ascending=False,
        )
        .head(limit)
        .reset_index(drop=True)
    )


def calculate_yearly_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate recorded sales by game release year.

    Missing release years and records outside the documented
    historical analysis period are excluded from this chart.
    """
    yearly_df = df[
        ["Year", "Global_Sales"]
    ].copy()

    yearly_df["Year"] = pd.to_numeric(
        yearly_df["Year"],
        errors="coerce",
    )

    yearly_df = yearly_df.dropna(
        subset=["Year"]
    )

    yearly_df = yearly_df.loc[
        yearly_df["Year"].between(
            START_YEAR,
            END_YEAR,
        )
    ].copy()

    if yearly_df.empty:
        return pd.DataFrame(
            columns=["Year", "Global_Sales"]
        )

    return (
        yearly_df.groupby("Year", as_index=False)["Global_Sales"]
        .sum()
        .sort_values("Year")
        .reset_index(drop=True)
    )


# ---------------------------------------------------------------------
# Sales visualizations
# ---------------------------------------------------------------------

def render_ranking_chart(
    data: pd.DataFrame,
    category_column: str,
    title: str,
) -> None:
    """Render a horizontal ranking of aggregated global sales."""
    if data.empty:
        st.info(
            "No records are available for this ranking."
        )
        return

    fig = px.bar(
        data,
        x="Global_Sales",
        y=category_column,
        orientation="h",
        title=title,
        labels={
            "Global_Sales": "Recorded Sales (Million Copies)",
            category_column: category_column,
        },
    )

    fig.update_yaxes(
        categoryorder="total ascending"
    )

    fig.update_layout(
        height=450,
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


def render_top_sales_charts(df: pd.DataFrame) -> None:
    """Display genre and platform rankings side by side."""
    st.subheader(
        "🏆 Top Genres and Gaming Platforms"
    )

    top_genres = calculate_top_sales(
        df,
        group_column="Genre",
    )

    top_platforms = calculate_top_sales(
        df,
        group_column="Platform",
    )

    col1, col2 = st.columns(2)

    with col1:
        render_ranking_chart(
            data=top_genres,
            category_column="Genre",
            title="Top 10 Genres by Global Sales",
        )

    with col2:
        render_ranking_chart(
            data=top_platforms,
            category_column="Platform",
            title="Top 10 Platforms by Global Sales",
        )


def render_yearly_sales_chart(df: pd.DataFrame) -> None:
    """Visualize recorded global sales grouped by release year."""
    st.subheader(
        "📈 Historical Sales by Game Release Year"
    )

    yearly_sales = calculate_yearly_sales(df)

    if yearly_sales.empty:
        st.info(
            "No valid release-year records are available "
            "for the selected historical period."
        )
        return

    fig = px.line(
        yearly_sales,
        x="Year",
        y="Global_Sales",
        markers=True,
        title="Recorded Global Sales by Game Release Year",
        labels={
            "Year": "Game Release Year",
            "Global_Sales": "Recorded Sales (Million Copies)",
        },
    )

    fig.update_layout(
        height=450,
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

    st.caption(
        f"The chart covers release years {START_YEAR}–{END_YEAR}. "
        "It groups the recorded sales of games by their release "
        "year and does not represent sales transactions occurring "
        "within each calendar year."
    )


# ---------------------------------------------------------------------
# Page navigation
# ---------------------------------------------------------------------

def render_navigation() -> None:
    """Display navigation links to the analytical dashboard pages."""
    st.subheader("🔎 Explore the Dashboard")

    st.write(
        "Select an analysis section to explore the historical "
        "dataset in more detail."
    )

    col1, col2 = st.columns(2)

    for index, page in enumerate(NAVIGATION_PAGES):
        target_column = (
            col1 if index % 2 == 0 else col2
        )

        with target_column:
            st.page_link(
                page["path"],
                label=page["label"],
                icon=page["icon"],
            )

            st.caption(
                page["description"]
            )


# ---------------------------------------------------------------------
# Application layout
# ---------------------------------------------------------------------

def render_header() -> None:
    """Display the dashboard title and project description."""
    st.title("🎮 Game Sales Analytics")

    st.write(
        "Interactive exploration of historical video game "
        "sales across genres, gaming platforms, and release years."
    )

    st.caption(
        "Python · Pandas · SQLite · Streamlit · Plotly"
    )

    st.divider()


def render_footer() -> None:
    """Display dataset scope and interpretation notes."""
    st.divider()

    st.caption(
        "Game Sales Analytics | Historical Video Game Sales Dataset "
        "| Sales expressed in millions of copies"
    )

    st.caption(
        "The dataset contains historical estimates with incomplete "
        "market coverage. Individual titles may appear on multiple "
        "platforms and are counted as separate game-platform entries."
    )


# ---------------------------------------------------------------------
# Application entry point
# ---------------------------------------------------------------------

def main() -> None:
    """Render the complete Game Sales Analytics overview page."""
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon="🎮",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    render_header()

    try:
        df = load_data()

        validate_dashboard_data(df)

    except (
        FileNotFoundError,
        sqlite3.Error,
        OSError,
        ValueError,
    ) as error:
        st.error(
            f"Unable to load dashboard data: {error}"
        )
        st.stop()

    render_overview_metrics(df)

    st.divider()

    render_top_sales_charts(df)

    st.divider()

    render_yearly_sales_chart(df)

    st.divider()

    render_navigation()

    render_footer()


if __name__ == "__main__":
    main()
