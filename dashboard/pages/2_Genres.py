
"""Genre analysis page for the Game Sales Analytics dashboard.

This page compares historical video game sales across genres using
aggregated game-platform records from the SQLite database.
"""

import sqlite3
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


DASHBOARD_DIR = Path(__file__).resolve().parent.parent

if str(DASHBOARD_DIR) not in sys.path:
    sys.path.insert(0, str(DASHBOARD_DIR))

from data_loader import load_data


PAGE_TITLE = "Genres | Game Sales Analytics"

REQUIRED_COLUMNS = [
    "Genre",
    "Global_Sales",
]

METRIC_OPTIONS = {
    "Total Sales": "Total_Sales",
    "Average Sales": "Average_Sales",
    "Median Sales": "Median_Sales",
    "Game Entries": "Game_Count",
}

METRIC_LABELS = {
    "Total_Sales": "Recorded Global Sales (Million Copies)",
    "Average_Sales": "Average Sales per Entry (Million Copies)",
    "Median_Sales": "Median Sales per Entry (Million Copies)",
    "Game_Count": "Number of Game-Platform Entries",
}


def validate_genre_data(df: pd.DataFrame) -> None:
    """Validate the columns required for genre-level analysis."""
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
            f"Missing required columns: {missing_columns}"
        )


def calculate_genre_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate game counts and historical sales metrics by genre."""
    statistics = (
        df.groupby("Genre", as_index=False)
        .agg(
            Game_Count=("Global_Sales", "size"),
            Total_Sales=("Global_Sales", "sum"),
            Average_Sales=("Global_Sales", "mean"),
            Median_Sales=("Global_Sales", "median"),
        )
        .sort_values(
            ["Total_Sales", "Genre"],
            ascending=[False, True],
        )
        .reset_index(drop=True)
    )

    total_sales = statistics["Total_Sales"].sum()
    total_entries = statistics["Game_Count"].sum()

    if total_sales > 0:
        statistics["Sales_Share_Percent"] = (
            statistics["Total_Sales"] / total_sales * 100
        )
    else:
        statistics["Sales_Share_Percent"] = 0.0

    if total_entries > 0:
        statistics["Entry_Share_Percent"] = (
            statistics["Game_Count"] / total_entries * 100
        )
    else:
        statistics["Entry_Share_Percent"] = 0.0

    return statistics


def sort_genre_statistics(
    statistics: pd.DataFrame,
    metric: str,
) -> pd.DataFrame:
    """Sort genre statistics by a supported metric."""
    if metric not in METRIC_LABELS:
        raise ValueError(
            f"Unsupported genre metric: {metric}"
        )

    return (
        statistics
        .sort_values(
            [metric, "Genre"],
            ascending=[False, True],
        )
        .reset_index(drop=True)
    )


def render_header() -> None:
    """Display the genre analysis title and dataset description."""
    st.title("📊 Genre Analysis")

    st.write(
        "Explore historical video game sales performance "
        "across genres, including total sales, average sales, "
        "median sales, and game entry counts."
    )

    st.caption(
        "Each record represents a game-platform entry. "
        "Sales figures are measured in millions of copies."
    )

    st.divider()


def render_overview_metrics(
    statistics: pd.DataFrame,
) -> None:
    """Display primary genre-level dataset metrics."""
    total_entries = int(
        statistics["Game_Count"].sum()
    )

    total_sales = float(
        statistics["Total_Sales"].sum()
    )

    top_genre = statistics.iloc[0]["Genre"]

    top_genre_sales = float(
        statistics.iloc[0]["Total_Sales"]
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Genres",
            f"{len(statistics):,}",
        )

    with col2:
        st.metric(
            "Game Entries",
            f"{total_entries:,}",
        )

    with col3:
        st.metric(
            "Global Sales (Million Copies)",
            f"{total_sales:,.2f}",
        )

    with col4:
        st.metric(
            "Top Genre by Total Sales",
            top_genre,
        )

    st.caption(
        f"The highest-selling genre accounts for "
        f"{top_genre_sales:,.2f} million recorded copies."
    )


def render_metric_controls() -> tuple[str, int]:
    """Render controls for metric selection and chart size."""
    col1, col2 = st.columns(2)

    with col1:
        selected_label = st.selectbox(
            "Compare Genres By",
            options=list(METRIC_OPTIONS),
            index=0,
        )

    with col2:
        selected_limit = st.slider(
            "Number of Genres",
            min_value=1,
            max_value=12,
            value=10,
        )

    return (
        METRIC_OPTIONS[selected_label],
        selected_limit,
    )


def render_genre_ranking(
    statistics: pd.DataFrame,
    metric: str,
    limit: int,
) -> None:
    """Render a horizontal ranking of genres by the chosen metric."""
    if limit < 1:
        raise ValueError(
            "The number of genres must be positive."
        )

    ranked = sort_genre_statistics(
        statistics,
        metric,
    ).head(limit)

    fig = px.bar(
        ranked,
        x=metric,
        y="Genre",
        orientation="h",
        color=metric,
        title=f"Genres Ranked by {METRIC_LABELS[metric]}",
        labels={
            metric: METRIC_LABELS[metric],
            "Genre": "Genre",
        },
        hover_data={
            "Game_Count": True,
            "Total_Sales": ":.2f",
            "Average_Sales": ":.3f",
            "Median_Sales": ":.3f",
        },
    )

    fig.update_yaxes(
        categoryorder="total ascending"
    )

    fig.update_layout(
        height=max(420, 42 * len(ranked) + 140),
        coloraxis_showscale=False,
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


def render_sales_comparison(
    statistics: pd.DataFrame,
) -> None:
    """Compare average and median sales across all genres."""
    st.subheader("Average vs. Median Sales")

    comparison = (
        statistics[
            [
                "Genre",
                "Average_Sales",
                "Median_Sales",
            ]
        ]
        .melt(
            id_vars="Genre",
            value_vars=[
                "Average_Sales",
                "Median_Sales",
            ],
            var_name="Metric",
            value_name="Sales",
        )
    )

    comparison["Metric"] = comparison["Metric"].map(
        {
            "Average_Sales": "Average Sales",
            "Median_Sales": "Median Sales",
        }
    )

    fig = px.bar(
        comparison,
        x="Genre",
        y="Sales",
        color="Metric",
        barmode="group",
        title="Average and Median Sales per Game Entry",
        labels={
            "Genre": "Genre",
            "Sales": "Sales (Million Copies)",
            "Metric": "Statistic",
        },
    )

    fig.update_layout(
        height=470,
        xaxis_tickangle=-45,
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=70,
        ),
    )

    st.plotly_chart(
        fig,
        width="stretch",
    )

    st.caption(
        "Large differences between average and median sales "
        "can indicate that a small number of exceptionally "
        "successful entries influence the mean."
    )


def render_genre_shares(
    statistics: pd.DataFrame,
) -> None:
    """Visualize the share of recorded global sales by genre."""
    st.subheader("Share of Recorded Global Sales")

    if statistics["Total_Sales"].sum() <= 0:
        st.info(
            "No positive sales values are available "
            "for the genre share chart."
        )
        return

    fig = px.pie(
        statistics,
        names="Genre",
        values="Total_Sales",
        hole=0.45,
        title="Genre Distribution of Recorded Global Sales",
    )

    fig.update_layout(
        height=480,
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
        "The percentages represent each genre's share "
        "of global sales recorded in this dataset, "
        "not its share of the complete video game market."
    )


def prepare_genre_table(
    statistics: pd.DataFrame,
) -> pd.DataFrame:
    """Prepare genre statistics with descriptive display labels."""
    return (
        statistics
        .rename(
            columns={
                "Genre": "Genre",
                "Game_Count": "Game Entries",
                "Total_Sales": "Total Sales (Million Copies)",
                "Average_Sales": "Average Sales (Million Copies)",
                "Median_Sales": "Median Sales (Million Copies)",
                "Sales_Share_Percent": "Sales Share (%)",
                "Entry_Share_Percent": "Entry Share (%)",
            }
        )
        .round(3)
    )


def render_genre_table(
    statistics: pd.DataFrame,
    metric: str,
) -> None:
    """Display all genre statistics sorted by the selected metric."""
    st.subheader("Detailed Genre Statistics")

    sorted_statistics = sort_genre_statistics(
        statistics,
        metric,
    )

    display_table = prepare_genre_table(
        sorted_statistics
    )

    st.dataframe(
        display_table,
        width="stretch",
        hide_index=True,
    )

    st.caption(
        f"Showing {len(display_table)} genres, "
        f"sorted by {METRIC_LABELS[metric].lower()}."
    )


def render_csv_download(
    statistics: pd.DataFrame,
) -> None:
    """Provide the full genre statistics as a CSV download."""
    st.subheader("Download Genre Statistics")

    csv_data = (
        statistics
        .to_csv(index=False)
        .encode("utf-8-sig")
    )

    st.download_button(
        label="Download Genre Statistics (CSV)",
        data=csv_data,
        file_name="genre_statistics.csv",
        mime="text/csv",
    )


def render_footer() -> None:
    """Display limitations of the historical sales dataset."""
    st.divider()

    st.caption(
        "Game Sales Analytics | Historical Video Game Sales Dataset"
    )

    st.caption(
        "Results are based on the available historical game-platform "
        "records and do not provide a complete view of the global market."
    )


def main() -> None:
    """Render the interactive genre analysis dashboard page."""
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon="📊",
        layout="wide",
    )

    render_header()

    try:
        df = load_data()
        validate_genre_data(df)

    except (
        FileNotFoundError,
        sqlite3.Error,
        OSError,
        ValueError,
    ) as error:
        st.error(
            f"Unable to load genre data: {error}"
        )
        st.stop()

    statistics = calculate_genre_statistics(df)

    if statistics.empty:
        st.warning(
            "No genre statistics are available."
        )
        st.stop()

    render_overview_metrics(statistics)

    st.divider()

    st.subheader("Genre Rankings")

    selected_metric, selected_limit = render_metric_controls()

    render_genre_ranking(
        statistics,
        metric=selected_metric,
        limit=selected_limit,
    )

    st.divider()

    render_sales_comparison(statistics)

    st.divider()

    render_genre_shares(statistics)

    st.divider()

    render_genre_table(
        statistics,
        metric=selected_metric,
    )

    render_csv_download(statistics)

    render_footer()


if __name__ == "__main__":
    main()
