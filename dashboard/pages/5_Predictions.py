
"""Experimental sales predictions for the Game Sales Analytics dashboard.

The page loads a trained regression pipeline and its evaluation metadata,
restricts inputs to observed historical combinations, and compares
model estimates with matching historical game-platform records.

Predictions are exploratory and are not reliable commercial forecasts.
"""

import json
import math
import sqlite3
import sys
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
import streamlit as st


DASHBOARD_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = DASHBOARD_DIR.parent

if str(DASHBOARD_DIR) not in sys.path:
    sys.path.insert(0, str(DASHBOARD_DIR))

from data_loader import load_data


PAGE_TITLE = "Predictions | Game Sales Analytics"

MODEL_PATH = BASE_DIR / "models" / "sales_model.joblib"
METRICS_PATH = BASE_DIR / "models" / "sales_model_metrics.json"

FEATURE_COLUMNS = ["Platform", "Genre", "Year"]
REQUIRED_COLUMNS = ["Name", *FEATURE_COLUMNS, "Global_Sales"]

START_YEAR = 1980
END_YEAR = 2016


def get_file_version(file_path: Path) -> tuple[str, int, int]:
    """Return an artifact path and metadata suitable for cache invalidation."""
    if not file_path.is_file():
        raise FileNotFoundError(
            f"Required artifact not found: {file_path}"
        )

    statistics = file_path.stat()

    return (
        str(file_path.resolve()),
        statistics.st_mtime_ns,
        statistics.st_size,
    )


@st.cache_resource(show_spinner=False)
def load_model(
    file_path: str,
    modified_ns: int,
    file_size: int,
) -> Any:
    """Load a trusted local model artifact with a versioned cache key."""
    model = joblib.load(file_path)

    if not hasattr(model, "predict"):
        raise TypeError(
            "The model artifact does not support predictions."
        )

    return model


@st.cache_data(show_spinner=False)
def load_model_metadata(
    file_path: str,
    modified_ns: int,
    file_size: int,
) -> dict[str, Any]:
    """Load and validate the model's persisted evaluation metadata."""
    with Path(file_path).open("r", encoding="utf-8") as file:
        metadata = json.load(file)

    if not isinstance(metadata, dict):
        raise ValueError(
            "Model metadata must contain a JSON object."
        )

    required_keys = {
        "model_name",
        "feature_columns",
        "evaluation",
        "split",
        "trained_at_utc",
    }

    missing_keys = required_keys - metadata.keys()

    if missing_keys:
        raise ValueError(
            "Model metadata is incomplete: "
            f"{sorted(missing_keys)}"
        )

    if metadata["feature_columns"] != FEATURE_COLUMNS:
        raise ValueError(
            "Model features do not match the dashboard input schema."
        )

    evaluation = metadata["evaluation"]

    for model_name in ["baseline", "random_forest"]:
        metrics = evaluation.get(model_name)

        if not isinstance(metrics, dict):
            raise ValueError(
                f"Missing evaluation metrics for {model_name}."
            )

        for metric_name in ["MAE", "RMSE", "R2"]:
            value = metrics.get(metric_name)

            if (
                not isinstance(value, (int, float))
                or not math.isfinite(value)
            ):
                raise ValueError(
                    f"Invalid {metric_name} for {model_name}."
                )

    return metadata


def prepare_historical_data(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare valid historical records for selection and comparison."""
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

    prepared = df[REQUIRED_COLUMNS].copy()

    prepared["Year"] = pd.to_numeric(
        prepared["Year"],
        errors="coerce",
    )

    prepared["Global_Sales"] = pd.to_numeric(
        prepared["Global_Sales"],
        errors="coerce",
    )

    prepared = prepared.dropna(
        subset=REQUIRED_COLUMNS
    ).copy()

    for column in ["Name", "Platform", "Genre"]:
        prepared[column] = (
            prepared[column]
            .astype(str)
            .str.strip()
        )

        prepared = prepared.loc[
            prepared[column].ne("")
        ].copy()

    valid_records = (
        prepared["Year"].between(START_YEAR, END_YEAR)
        & prepared["Year"].mod(1).eq(0)
        & prepared["Global_Sales"].ge(0)
        & prepared["Global_Sales"].map(math.isfinite)
    )

    prepared = prepared.loc[
        valid_records
    ].copy()

    if prepared.empty:
        raise ValueError(
            "No valid historical records remain."
        )

    prepared["Year"] = prepared["Year"].astype(int)

    return prepared.reset_index(drop=True)


def get_available_years(
    df: pd.DataFrame,
    platform: str,
) -> list[int]:
    """Return release years observed for the selected platform."""
    years = df.loc[
        df["Platform"].eq(platform),
        "Year",
    ]

    return sorted(years.unique().tolist())


def get_available_genres(
    df: pd.DataFrame,
    platform: str,
    year: int,
) -> list[str]:
    """Return genres observed for the selected platform and year."""
    matching = df.loc[
        df["Platform"].eq(platform)
        & df["Year"].eq(year)
    ]

    return sorted(
        matching["Genre"].unique().tolist()
    )


def create_prediction_features(
    platform: str,
    genre: str,
    year: int,
) -> pd.DataFrame:
    """Create an input record with the model's expected feature order."""
    return pd.DataFrame(
        [
            {
                "Platform": platform,
                "Genre": genre,
                "Year": year,
            }
        ],
        columns=FEATURE_COLUMNS,
    )


def predict_global_sales(
    model: Any,
    features: pd.DataFrame,
) -> float:
    """Generate and validate a single regression estimate."""
    predictions = model.predict(features)

    if len(predictions) != 1:
        raise ValueError(
            "The model must return exactly one prediction."
        )

    estimate = float(predictions[0])

    if not math.isfinite(estimate):
        raise ValueError(
            "The model returned a non-finite estimate."
        )

    if estimate < 0:
        raise ValueError(
            "The model returned a negative sales estimate."
        )

    return estimate


def calculate_historical_statistics(
    df: pd.DataFrame,
    platform: str,
    genre: str,
    year: int,
) -> dict[str, float | int]:
    """Summarize historical sales matching all selected features."""
    matching_sales = df.loc[
        df["Platform"].eq(platform)
        & df["Genre"].eq(genre)
        & df["Year"].eq(year),
        "Global_Sales",
    ]

    if matching_sales.empty:
        raise ValueError(
            "No historical records match the selected combination."
        )

    return {
        "count": int(len(matching_sales)),
        "mean": float(matching_sales.mean()),
        "median": float(matching_sales.median()),
        "minimum": float(matching_sales.min()),
        "maximum": float(matching_sales.max()),
    }


def render_header() -> None:
    """Display the page introduction and model reliability warning."""
    st.title("🤖 Experimental Sales Predictions")

    st.write(
        "Explore an experimental estimate of recorded historical "
        "video game sales using platform, genre, and release year."
    )

    st.warning(
        "The model is a demonstration of a machine-learning workflow, "
        "not a validated forecasting system. Its predictions should "
        "not be used for commercial or financial decisions."
    )

    st.caption(
        "All sales figures are measured in millions of copies."
    )

    st.divider()


def render_model_information(
    metadata: dict[str, Any],
) -> None:
    """Display training provenance and the current model configuration."""
    st.subheader("Trained Model")

    training_date = metadata["trained_at_utc"]

    model_name = metadata["model_name"]

    split_details = metadata["split"]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Model",
            model_name,
        )

    with col2:
        st.metric(
            "Training Records",
            f"{split_details['training_records']:,}",
        )

    with col3:
        st.metric(
            "Test Records",
            f"{split_details['test_records']:,}",
        )

    st.caption(
        f"Training timestamp (UTC): {training_date}"
    )

    st.caption(
        "Features: Platform, Genre, Year | "
        "Evaluation: Title-grouped holdout split"
    )


def render_prediction_controls(
    df: pd.DataFrame,
) -> tuple[str, str, int]:
    """Render historically observed platform, release-year, and genre options."""
    st.subheader("Prediction Inputs")

    platforms = sorted(
        df["Platform"].unique().tolist()
    )

    platform = st.selectbox(
        "Gaming Platform",
        options=platforms,
        key="prediction_platform",
    )

    years = get_available_years(
        df,
        platform,
    )

    year = st.selectbox(
        "Release Year",
        options=years,
        index=len(years) - 1,
        key="prediction_year",
    )

    genres = get_available_genres(
        df,
        platform,
        year,
    )

    genre = st.selectbox(
        "Game Genre",
        options=genres,
        key="prediction_genre",
    )

    st.caption(
        "The selectable combinations have been observed "
        "in the historical dataset. This does not establish "
        "that the model can predict them accurately."
    )

    return platform, genre, year


def render_prediction_result(
    estimate: float,
) -> None:
    """Display a point estimate without implying statistical confidence."""
    st.subheader("Model Estimate")

    st.metric(
        "Estimated Recorded Global Sales",
        f"{estimate:,.3f} M",
    )

    st.caption(
        "This is an uncalibrated point estimate, not "
        "a guaranteed sales figure or prediction interval."
    )


def render_historical_comparison(
    df: pd.DataFrame,
    platform: str,
    genre: str,
    year: int,
) -> None:
    """Display the distribution of matching historical sales values."""
    statistics = calculate_historical_statistics(
        df,
        platform,
        genre,
        year,
    )

    st.subheader("Historical Comparison")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Matching Entries",
            f"{statistics['count']:,}",
        )

    with col2:
        st.metric(
            "Historical Average",
            f"{statistics['mean']:,.3f} M",
        )

    with col3:
        st.metric(
            "Historical Median",
            f"{statistics['median']:,.3f} M",
        )

    st.write(
        "Recorded sales range: "
        f"**{statistics['minimum']:,.3f}–"
        f"{statistics['maximum']:,.3f} million copies**."
    )

    if statistics["count"] < 5:
        st.info(
            "Fewer than five matching game-platform entries "
            "are available. The historical comparison is "
            "particularly sensitive to individual records."
        )

    st.caption(
        "These are descriptive historical statistics, "
        "not independent model validation results."
    )


def render_model_evaluation(
    metadata: dict[str, Any],
) -> None:
    """Display regression metrics saved during the model training run."""
    st.subheader("Model Evaluation")

    evaluation = metadata["evaluation"]

    baseline = evaluation["baseline"]
    forest = evaluation["random_forest"]

    results = pd.DataFrame(
        [
            {
                "Model": "Dummy Baseline",
                "MAE": baseline["MAE"],
                "RMSE": baseline["RMSE"],
                "R²": baseline["R2"],
            },
            {
                "Model": "Random Forest",
                "MAE": forest["MAE"],
                "RMSE": forest["RMSE"],
                "R²": forest["R2"],
            },
        ]
    )

    st.dataframe(
        results.round(4),
        width="stretch",
        hide_index=True,
    )

    st.caption(
        "MAE and RMSE are expressed in millions of copies. "
        "Lower values are better. Higher R² values are better."
    )

    if (
        forest["MAE"] < baseline["MAE"]
        and forest["RMSE"] < baseline["RMSE"]
    ):
        st.success(
            "The Random Forest outperformed the dummy baseline "
            "on both error metrics in this holdout evaluation. "
            "Further validation is still required."
        )
    else:
        st.warning(
            "The Random Forest did not outperform the dummy "
            "baseline on both error metrics. Its usefulness "
            "for prediction remains unproven."
        )

    st.caption(
        "The metrics were loaded from the training metadata "
        "generated alongside the saved model. "
        "A single holdout split does not establish "
        "performance on future game releases."
    )


def render_limitations() -> None:
    """Explain the main limitations of the dataset and regression model."""
    st.subheader("Limitations")

    st.markdown(
        """
        - The model uses only platform, genre, and release year.
        - The target is recorded historical global sales, not
          revenue or sales within a particular calendar year.
        - The source dataset has incomplete market coverage.
        - The training evaluation uses one grouped holdout split.
        - Performance on future releases has not been established.
        - The point estimates do not include calibrated uncertainty.
        """
    )


def render_footer() -> None:
    """Display the experimental-use disclaimer."""
    st.divider()

    st.caption(
        "Game Sales Analytics | Experimental Machine Learning"
    )


def main() -> None:
    """Render model information, predictions, and evaluation results."""
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon="🤖",
        layout="wide",
    )

    render_header()

    try:
        historical_data = prepare_historical_data(
            load_data()
        )

        model_version = get_file_version(
            MODEL_PATH
        )

        metrics_version = get_file_version(
            METRICS_PATH
        )

        # Load model artifacts only from this trusted project.
        model = load_model(
            *model_version
        )

        metadata = load_model_metadata(
            *metrics_version
        )

    except Exception as error:
        st.error(
            f"Unable to initialize the prediction page: {error}"
        )

        st.info(
            "Run 'python src/train_model.py' to generate "
            "the model and its evaluation metadata."
        )

        st.stop()

    render_model_information(metadata)

    st.divider()

    platform, genre, year = render_prediction_controls(
        historical_data
    )

    if st.button(
        "Generate Prediction",
        type="primary",
    ):
        features = create_prediction_features(
            platform,
            genre,
            year,
        )

        try:
            estimate = predict_global_sales(
                model,
                features,
            )

        except (ValueError, TypeError, KeyError) as error:
            st.error(
                f"Prediction failed: {error}"
            )

        else:
            st.divider()

            render_prediction_result(estimate)

            st.divider()

            render_historical_comparison(
                historical_data,
                platform,
                genre,
                year,
            )

    st.divider()

    render_model_evaluation(metadata)

    st.divider()

    render_limitations()

    render_footer()


if __name__ == "__main__":
    main()
