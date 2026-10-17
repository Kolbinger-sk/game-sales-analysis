
"""Regional sales analysis page for Game Sales Analytics.

The page compares recorded video game sales across geographic regions,
genres, and gaming platforms. Regional shares refer exclusively to
sales represented in the historical source dataset.
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


PAGE_TITLE = "Regions | Game Sales Analytics"

REGION_LABELS = {
    "NA_Sales": "North America",
    "EU_Sales": "Europe",
    "JP_Sales": "Japan",
    "Other_Sales": "Other Regions",
}

REGION_COLUMNS = list(REGION_LABELS)

REQUIRED_COLUMNS = [
    "Genre",
    "Platform",
    *REGION_COLUMNS,
]

TOP_N = 10


def validate_regional_data(df: pd.DataFrame) -> None:
    """Validate the columns and values required for regional analysis."""
    if df.empty:
        raise ValueError("The database does not contain any records.")

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    if df[REGION_COLUMNS].isna().any().any():
        raise ValueError(
            "Regional sales contain missing values."
        )

    if df[REGION_COLUMNS].lt(0).any().any():
        raise ValueError(
            "Regional sales cannot be negative."
        )


def calculate_regional_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate recorded sales and sales shares by region."""
    statistics = (
        df[REGION_COLUMNS]
        .sum()
        .rename("Total_Sales")
        .rename_axis("Region_Code")
        .reset_index()
    )

    statistics["Region"] = statistics["Region_Code"].map(
        REGION_LABELS
    )

    total_sales = statistics["Total_Sales"].sum()

    statistics["Sales_Share_Percent"] = (
        statistics["Total_Sales"] / total_sales * 100
        if total_sales > 0
        else 0.0
    )

    return (
        statistics[
            ["Region", "Total_Sales", "Sales_Share_Percent"]
        ]
        .sort_values("Total_Sales", ascending=False)
        .reset_index(drop=True)
    )


def calculate_category_sales(
    df: pd.DataFrame,
    category: str,
) -> pd.DataFrame:
    """Aggregate regional sales by genre or gaming platform."""
    if category not in {"Genre", "Platform"}:
        raise ValueError(
            f"Unsupported analysis category: {category}"
        )

    result = (
        df.groupby(category, as_index=False)[REGION_COLUMNS]
        .sum()
    )

    result["Total_Regional_Sales"] = result[
        REGION_COLUMNS
    ].sum(axis=1)

    return (
        result
        .sort_values(
            "Total_Regional_Sales",
            ascending=False,
        )
        .reset_index(drop=True)
    )


def prepare_long_format(
    df: pd.DataFrame,
    category: str,
) -> pd.DataFrame:
    """Convert regional category totals into chart-ready long format."""
    long_df = df.melt(
        id_vars=category,
        value_vars=REGION_COLUMNS,
        var_name="Region",
        value_name="Sales",
    )

    long_df["Region"] = long_df["Region"].map(
        REGION_LABELS
    )

    return long_df


def render_header() -> None:
    """Display the regional analysis title and dataset scope."""
    st.title("🌍 Regional Sales Analysis")

    st.write(
        "Explore recorded video game sales across North America, "
        "Europe, Japan, and other regions. Compare sales patterns "
        "across genres and gaming platforms."
    )

    st.caption(
        "All sales figures are historical estimates in millions "
        "of copies. Regional shares describe the available dataset."
    )

    st.divider()


def render_overview_metrics(
    statistics: pd.DataFrame,
) -> None:
    """Display total recorded regional sales and regional leaders."""
    total_sales = statistics["Total_Sales"].sum()

    leading_region = statistics.iloc[0]["Region"]
    leading_share = statistics.iloc[0]["Sales_Share_Percent"]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Sales Regions",
            len(statistics),
        )

    with col2:
        st.metric(
            "Total Recorded Regional Sales",
            f"{total_sales:,.2f} M",
        )

    with col3:
        st.metric(
            "Largest Recorded Region",
            leading_region,
        )

    st.caption(
        f"{leading_region} accounts for {leading_share:.1f}% "
        "of the regional sales recorded in this dataset."
    )


def render_regional_overview(
    statistics: pd.DataFrame,
) -> None:
    """Visualize regional sales totals and their distribution."""
    st.subheader("Regional Sales Overview")

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            statistics,
            x="Region",
            y="Total_Sales",
            color="Region",
            title="Recorded Sales by Region",
            labels={
                "Total_Sales": "Sales (Million Copies)",
            },
        )

        fig.update_layout(
            height=440,
            showlegend=False,
        )

        st.plotly_chart(fig, width="stretch")

    with col2:
        if statistics["Total_Sales"].sum() > 0:
            fig = px.pie(
                statistics,
                names="Region",
                values="Total_Sales",
                hole=0.45,
                title="Share of Recorded Regional Sales",
            )

            fig.update_layout(height=440)

            st.plotly_chart(fig, width="stretch")

        else:
            st.info(
                "Regional share visualization requires "
                "positive recorded sales."
            )

    st.caption(
        "These percentages are calculated from the sum of the "
        "four recorded regional sales columns. They are not "
        "estimates of the complete global gaming market."
    )


def render_genre_analysis(
    genre_statistics: pd.DataFrame,
) -> None:
    """Display regional sales comparisons across game genres."""
    st.subheader("Regional Sales by Genre")

    available_genres = len(genre_statistics)

    genre_limit = st.slider(
        "Number of Genres",
        min_value=1,
        max_value=available_genres,
        value=min(TOP_N, available_genres),
        key="regions_genre_limit",
    )

    selected_genres = genre_statistics.head(genre_limit)

    long_df = prepare_long_format(
        selected_genres,
        category="Genre",
    )

    fig = px.bar(
        long_df,
        x="Genre",
        y="Sales",
        color="Region",
        barmode="group",
        title="Genre Sales Across Geographic Regions",
        labels={
            "Sales": "Sales (Million Copies)",
        },
    )

    fig.update_layout(
        height=520,
        xaxis_tickangle=-45,
    )

    st.plotly_chart(fig, width="stretch")

    st.caption(
        "Genres are selected by their total recorded sales "
        "across the four regions."
    )


def render_regional_genre_ranking(
    genre_statistics: pd.DataFrame,
) -> None:
    """Rank game genres within a selected geographic region."""
    st.subheader("Top Genres in a Selected Region")

    selected_region = st.selectbox(
        "Select Region",
        options=list(REGION_LABELS),
        format_func=lambda value: REGION_LABELS[value],
        key="regions_genre_region",
    )

    ranking = (
        genre_statistics
        .nlargest(TOP_N, selected_region)
        .sort_values(selected_region)
    )

    fig = px.bar(
        ranking,
        x=selected_region,
        y="Genre",
        orientation="h",
        title=(
            f"Top Genres in {REGION_LABELS[selected_region]}"
        ),
        labels={
            selected_region: "Sales (Million Copies)",
            "Genre": "Genre",
        },
    )

    fig.update_layout(height=450)

    st.plotly_chart(fig, width="stretch")


def render_platform_analysis(
    platform_statistics: pd.DataFrame,
) -> None:
    """Compare regional sales for selected gaming platforms."""
    st.subheader("Regional Platform Comparison")

    available_platforms = sorted(
        platform_statistics["Platform"].tolist()
    )

    default_platforms = (
        platform_statistics["Platform"]
        .head(min(5, len(platform_statistics)))
        .tolist()
    )

    selected_platforms = st.multiselect(
        "Select Gaming Platforms",
        options=available_platforms,
        default=default_platforms,
        key="regions_platform_selection",
    )

    if not selected_platforms:
        st.info(
            "Select at least one platform to view "
            "its regional sales distribution."
        )
        return

    selected_data = platform_statistics.loc[
        platform_statistics["Platform"].isin(
            selected_platforms
        )
    ].copy()

    long_df = prepare_long_format(
        selected_data,
        category="Platform",
    )

    fig = px.bar(
        long_df,
        x="Platform",
        y="Sales",
        color="Region",
        barmode="stack",
        title="Recorded Regional Sales by Platform",
        labels={
            "Sales": "Sales (Million Copies)",
        },
    )

    fig.update_layout(
        height=510,
        xaxis_tickangle=-45,
    )

    st.plotly_chart(fig, width="stretch")

    st.caption(
        "The stacked bars show the regional composition "
        "of recorded sales for each selected platform."
    )


def render_statistics_tables(
    regional_statistics: pd.DataFrame,
    genre_statistics: pd.DataFrame,
    platform_statistics: pd.DataFrame,
) -> None:
    """Display downloadable regional, genre, and platform tables."""
    st.subheader("Detailed Regional Statistics")

    tab1, tab2, tab3 = st.tabs(
        [
            "Regions",
            "Genres",
            "Platforms",
        ]
    )

    with tab1:
        st.dataframe(
            regional_statistics.round(3),
            width="stretch",
            hide_index=True,
        )

    with tab2:
        st.dataframe(
            genre_statistics.round(3),
            width="stretch",
            hide_index=True,
        )

    with tab3:
        st.dataframe(
            platform_statistics.round(3),
            width="stretch",
            hide_index=True,
        )


def render_csv_downloads(
    regional_statistics: pd.DataFrame,
    genre_statistics: pd.DataFrame,
    platform_statistics: pd.DataFrame,
) -> None:
    """Provide CSV exports for all regional aggregations."""
    st.subheader("Download Regional Statistics")

    exports = [
        (
            "Regional Summary",
            regional_statistics,
            "regional_statistics.csv",
        ),
        (
            "Regional Genre Statistics",
            genre_statistics,
            "genre_regional_statistics.csv",
        ),
        (
            "Regional Platform Statistics",
            platform_statistics,
            "platform_regional_statistics.csv",
        ),
    ]

    columns = st.columns(3)

    for column, (label, data, filename) in zip(
        columns,
        exports,
    ):
        with column:
            st.download_button(
                label=label,
                data=data.to_csv(index=False).encode("utf-8-sig"),
                file_name=filename,
                mime="text/csv",
                use_container_width=True,
            )


def render_footer() -> None:
    """Display limitations of the underlying sales dataset."""
    st.divider()

    st.caption(
        "Game Sales Analytics | Historical Video Game Sales Dataset"
    )

    st.caption(
        "The dataset contains estimated sales with incomplete "
        "market coverage. Regional figures may differ slightly "
        "from reported global sales due to rounding."
    )


def main() -> None:
    """Render the interactive regional sales analysis page."""
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon="🌍",
        layout="wide",
    )

    render_header()

    try:
        df = load_data()
        validate_regional_data(df)

    except (
        FileNotFoundError,
        sqlite3.Error,
        OSError,
        ValueError,
    ) as error:
        st.error(
            f"Unable to load regional sales data: {error}"
        )
        st.stop()

    regional_statistics = calculate_regional_statistics(df)

    genre_statistics = calculate_category_sales(
        df,
        category="Genre",
    )

    platform_statistics = calculate_category_sales(
        df,
        category="Platform",
    )

    if genre_statistics.empty or platform_statistics.empty:
        st.warning(
            "Insufficient category data for regional analysis."
        )
        st.stop()

    render_overview_metrics(regional_statistics)

    st.divider()

    render_regional_overview(regional_statistics)

    st.divider()

    render_genre_analysis(genre_statistics)

    st.divider()

    render_regional_genre_ranking(genre_statistics)

    st.divider()

    render_platform_analysis(platform_statistics)

    st.divider()

    render_statistics_tables(
        regional_statistics,
        genre_statistics,
        platform_statistics,
    )

    render_csv_downloads(
        regional_statistics,
        genre_statistics,
        platform_statistics,
    )

    render_footer()


if __name__ == "__main__":
    main()
