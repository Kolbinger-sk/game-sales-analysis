
"""Platform analysis page for the Game Sales Analytics dashboard.

This page compares historical video game sales across platforms,
including recorded sales totals, entry counts, and average sales.

Each dataset row represents a game-platform entry. Sales figures
are expressed in millions of copies.
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


PAGE_TITLE = "Platforms | Game Sales Analytics"

TOP_N = 10

REQUIRED_COLUMNS = [
    "Platform",
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


def validate_platform_data(df: pd.DataFrame) -> None:
    """Validate the dataset required for platform comparisons."""
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

    if df["Platform"].isna().any():
        raise ValueError(
            "The dataset contains missing platform identifiers."
        )

    if df["Global_Sales"].isna().any():
        raise ValueError(
            "The dataset contains missing sales values."
        )


def calculate_platform_statistics(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Aggregate game entry counts and global sales by platform."""
    statistics = (
        df.groupby("Platform", as_index=False)
        .agg(
            Game_Count=("Global_Sales", "size"),
            Total_Sales=("Global_Sales", "sum"),
            Average_Sales=("Global_Sales", "mean"),
            Median_Sales=("Global_Sales", "median"),
        )
        .sort_values(
            ["Total_Sales", "Platform"],
            ascending=[False, True],
        )
        .reset_index(drop=True)
    )

    total_sales = statistics["Total_Sales"].sum()

    if total_sales > 0:
        statistics["Sales_Share_Percent"] = (
            statistics["Total_Sales"]
            / total_sales
            * 100
        )
    else:
        statistics["Sales_Share_Percent"] = 0.0

    return statistics


def sort_platform_statistics(
    statistics: pd.DataFrame,
    metric: str,
) -> pd.DataFrame:
    """Sort platforms by a supported statistical metric."""
    if metric not in METRIC_LABELS:
        raise ValueError(
            f"Unsupported platform metric: {metric}"
        )

    return (
        statistics
        .sort_values(
            [metric, "Platform"],
            ascending=[False, True],
        )
        .reset_index(drop=True)
    )


def select_platforms(
    statistics: pd.DataFrame,
    first_platform: str,
    second_platform: str,
) -> pd.DataFrame:
    """Return statistics for two selected gaming platforms."""
    selected = statistics.loc[
        statistics["Platform"].isin(
            [first_platform, second_platform]
        )
    ].copy()

    return selected.reset_index(drop=True)


def render_header() -> None:
    """Display the platform analysis title and description."""
    st.title("🕹️ Platform Analysis")

    st.write(
        "Compare gaming platforms using historical sales "
        "statistics, game entry counts, and interactive rankings."
    )

    st.caption(
        "Sales represent historical estimates recorded in the "
        "dataset, not complete platform lifetime sales."
    )

    st.divider()


def render_overview_metrics(
    statistics: pd.DataFrame,
) -> None:
    """Display the primary platform-level summary metrics."""
    total_entries = int(
        statistics["Game_Count"].sum()
    )

    total_sales = float(
        statistics["Total_Sales"].sum()
    )

    top_platform = statistics.iloc[0]["Platform"]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Gaming Platforms",
            f"{len(statistics):,}",
        )

    with col2:
        st.metric(
            "Game Entries",
            f"{total_entries:,}",
        )

    with col3:
        st.metric(
            "Recorded Global Sales",
            f"{total_sales:,.2f} M",
        )

    with col4:
        st.metric(
            "Top Platform by Sales",
            top_platform,
        )


def render_ranking_controls(
    platform_count: int,
) -> tuple[str, int]:
    """Render the ranking metric and number of displayed platforms."""
    col1, col2 = st.columns(2)

    with col1:
        selected_label = st.selectbox(
            "Rank Platforms By",
            options=list(METRIC_OPTIONS),
        )

    with col2:
        selected_limit = st.slider(
            "Number of Platforms",
            min_value=1,
            max_value=platform_count,
            value=min(TOP_N, platform_count),
        )

    return (
        METRIC_OPTIONS[selected_label],
        selected_limit,
    )


def render_platform_ranking(
    statistics: pd.DataFrame,
    metric: str,
    limit: int,
) -> None:
    """Display the top platforms for the selected metric."""
    ranked = (
        sort_platform_statistics(
            statistics,
            metric,
        )
        .head(limit)
    )

    fig = px.bar(
        ranked,
        x=metric,
        y="Platform",
        orientation="h",
        color=metric,
        title=f"Top Platforms by {METRIC_LABELS[metric]}",
        labels={
            metric: METRIC_LABELS[metric],
            "Platform": "Gaming Platform",
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
        height=max(450, len(ranked) * 35 + 150),
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


def render_platform_comparison(
    statistics: pd.DataFrame,
) -> None:
    """Compare sales metrics between two selected platforms."""
    st.subheader("⚖️ Platform Comparison")

    platforms = sorted(
        statistics["Platform"].tolist()
    )

    if len(platforms) < 2:
        st.info(
            "At least two platforms are required for comparison."
        )
        return

    col1, col2 = st.columns(2)

    with col1:
        first_platform = st.selectbox(
            "First Platform",
            options=platforms,
            index=0,
            key="platform_compare_first",
        )

    with col2:
        second_platform = st.selectbox(
            "Second Platform",
            options=platforms,
            index=1,
            key="platform_compare_second",
        )

    if first_platform == second_platform:
        st.info(
            "Select two different platforms to compare their statistics."
        )
        return

    comparison = select_platforms(
        statistics,
        first_platform,
        second_platform,
    )

    metric_columns = [
        "Total_Sales",
        "Average_Sales",
        "Median_Sales",
        "Game_Count",
    ]

    comparison_long = comparison.melt(
        id_vars="Platform",
        value_vars=metric_columns,
        var_name="Metric",
        value_name="Value",
    )

    # Faceting preserves independent scales for differently sized metrics.
    fig = px.bar(
        comparison_long,
        x="Platform",
        y="Value",
        color="Platform",
        facet_col="Metric",
        facet_col_wrap=2,
        title="Comparison of Selected Platforms",
        labels={
            "Value": "Value",
            "Platform": "Gaming Platform",
        },
    )

    fig.update_yaxes(
        matches=None,
        showticklabels=True,
    )

    fig.for_each_annotation(
        lambda annotation: annotation.update(
            text=annotation.text.split("=")[-1].replace("_", " ")
        )
    )

    fig.update_layout(
        height=650,
        showlegend=False,
        margin=dict(
            l=20,
            r=20,
            t=70,
            b=30,
        ),
    )

    st.plotly_chart(
        fig,
        width="stretch",
    )

    st.caption(
        "Sales metrics are expressed in millions of copies. "
        "Game Count refers to the number of game-platform entries."
    )


def prepare_platform_table(
    statistics: pd.DataFrame,
) -> pd.DataFrame:
    """Prepare platform statistics for presentation."""
    return (
        statistics
        .rename(
            columns={
                "Platform": "Platform",
                "Game_Count": "Game Entries",
                "Total_Sales": "Total Sales (Million Copies)",
                "Average_Sales": "Average Sales (Million Copies)",
                "Median_Sales": "Median Sales (Million Copies)",
                "Sales_Share_Percent": "Recorded Sales Share (%)",
            }
        )
        .round(3)
    )


def render_platform_table(
    statistics: pd.DataFrame,
    metric: str,
) -> None:
    """Display all platform statistics sorted by the selected metric."""
    st.subheader("📋 Detailed Platform Statistics")

    sorted_statistics = sort_platform_statistics(
        statistics,
        metric,
    )

    st.dataframe(
        prepare_platform_table(sorted_statistics),
        width="stretch",
        hide_index=True,
    )


def render_csv_download(
    statistics: pd.DataFrame,
) -> None:
    """Provide a CSV export of platform-level statistics."""
    st.subheader("📥 Download Platform Statistics")

    csv_data = (
        statistics
        .to_csv(index=False)
        .encode("utf-8-sig")
    )

    st.download_button(
        label="Download Platform Statistics (CSV)",
        data=csv_data,
        file_name="platform_statistics.csv",
        mime="text/csv",
    )


def render_footer() -> None:
    """Display dataset coverage and interpretation notes."""
    st.divider()

    st.caption(
        "Game Sales Analytics | Historical Video Game Sales Dataset"
    )

    st.caption(
        "Platform comparisons reflect the records available in "
        "the dataset. Missing historical records and differences "
        "in platform lifespans can affect comparisons."
    )


def main() -> None:
    """Render the interactive platform analysis dashboard page."""
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon="🕹️",
        layout="wide",
    )

    render_header()

    try:
        df = load_data()
        validate_platform_data(df)

    except (
        FileNotFoundError,
        sqlite3.Error,
        OSError,
        ValueError,
    ) as error:
        st.error(
            f"Unable to load platform data: {error}"
        )
        st.stop()

    statistics = calculate_platform_statistics(df)

    if statistics.empty:
        st.warning(
            "No platform statistics are available."
        )
        st.stop()

    render_overview_metrics(statistics)

    st.divider()

    st.subheader("🏆 Platform Rankings")

    selected_metric, selected_limit = render_ranking_controls(
        platform_count=len(statistics)
    )

    render_platform_ranking(
        statistics,
        metric=selected_metric,
        limit=selected_limit,
    )

    st.divider()

    render_platform_comparison(statistics)

    st.divider()

    render_platform_table(
        statistics,
        metric=selected_metric,
    )

    render_csv_download(statistics)

    render_footer()


if __name__ == "__main__":
    main()
