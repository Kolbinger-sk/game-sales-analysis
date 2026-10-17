
"""Train and evaluate the experimental game sales regression model.

The pipeline estimates recorded global sales using platform, genre,
and release year. Model quality is evaluated against a dummy baseline
using a holdout split grouped by game title.

The model is intended for exploratory analysis, not commercial
sales forecasting.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "data" / "processed" / "vgsales_clean.csv"

MODEL_DIR = BASE_DIR / "models"
MODEL_PATH = MODEL_DIR / "sales_model.joblib"
METRICS_PATH = MODEL_DIR / "sales_model_metrics.json"

FEATURE_COLUMNS = [
    "Platform",
    "Genre",
    "Year",
]

CATEGORICAL_COLUMNS = [
    "Platform",
    "Genre",
]

NUMERIC_COLUMNS = [
    "Year",
]

TARGET_COLUMN = "Global_Sales"
GROUP_COLUMN = "Name"

REQUIRED_COLUMNS = [
    GROUP_COLUMN,
    *FEATURE_COLUMNS,
    TARGET_COLUMN,
]

START_YEAR = 1980
END_YEAR = 2016

RANDOM_STATE = 42
TEST_SIZE = 0.2

FOREST_ESTIMATORS = 200
FOREST_MIN_SAMPLES_LEAF = 3


def load_training_data(file_path: Path) -> pd.DataFrame:
    """Load the cleaned dataset and validate its required columns."""
    if not file_path.is_file():
        raise FileNotFoundError(
            f"Cleaned dataset not found: {file_path}"
        )

    df = pd.read_csv(file_path)

    if df.empty:
        raise ValueError(
            "The cleaned dataset is empty."
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

    return df


def prepare_training_data(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare and validate features, targets, and title groups."""
    prepared = df[REQUIRED_COLUMNS].copy()

    prepared["Year"] = pd.to_numeric(
        prepared["Year"],
        errors="coerce",
    )

    prepared[TARGET_COLUMN] = pd.to_numeric(
        prepared[TARGET_COLUMN],
        errors="coerce",
    )

    prepared = prepared.dropna(
        subset=REQUIRED_COLUMNS
    ).copy()

    for column in [
        GROUP_COLUMN,
        *CATEGORICAL_COLUMNS,
    ]:
        prepared[column] = (
            prepared[column]
            .astype(str)
            .str.strip()
        )

        prepared = prepared.loc[
            prepared[column].ne("")
        ].copy()

    valid_years = (
        prepared["Year"].between(
            START_YEAR,
            END_YEAR,
        )
        & prepared["Year"].mod(1).eq(0)
    )

    valid_sales = (
        np.isfinite(prepared[TARGET_COLUMN])
        & prepared[TARGET_COLUMN].ge(0)
    )

    prepared = prepared.loc[
        valid_years & valid_sales
    ].copy()

    prepared["Year"] = prepared["Year"].astype(int)

    prepared = prepared.reset_index(drop=True)

    if prepared.empty:
        raise ValueError(
            "No valid records remain after training data preparation."
        )

    if prepared[GROUP_COLUMN].nunique() < 2:
        raise ValueError(
            "At least two distinct game titles are required "
            "for grouped train-test splitting."
        )

    return prepared


def split_training_data(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Create a holdout split without overlapping game title groups."""
    splitter = GroupShuffleSplit(
        n_splits=1,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
    )

    groups = (
        df[GROUP_COLUMN]
        .str.casefold()
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    train_indices, test_indices = next(
        splitter.split(
            df,
            groups=groups,
        )
    )

    train_df = df.iloc[train_indices].copy()
    test_df = df.iloc[test_indices].copy()

    train_titles = set(groups.iloc[train_indices])
    test_titles = set(groups.iloc[test_indices])

    if train_titles.intersection(test_titles):
        raise RuntimeError(
            "Game title groups overlap between "
            "training and test data."
        )

    if train_df.empty or test_df.empty:
        raise ValueError(
            "The train-test split produced an empty partition."
        )

    return train_df, test_df


def create_preprocessor() -> ColumnTransformer:
    """Configure categorical encoding and numeric feature processing."""
    return ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(
                    handle_unknown="ignore",
                ),
                CATEGORICAL_COLUMNS,
            ),
            (
                "numeric",
                "passthrough",
                NUMERIC_COLUMNS,
            ),
        ],
        remainder="drop",
    )


def create_baseline_pipeline() -> Pipeline:
    """Create a mean-based regression baseline."""
    return Pipeline(
        steps=[
            (
                "preprocessing",
                create_preprocessor(),
            ),
            (
                "regressor",
                DummyRegressor(
                    strategy="mean",
                ),
            ),
        ]
    )


def create_random_forest_pipeline() -> Pipeline:
    """Create the experimental Random Forest regression pipeline."""
    return Pipeline(
        steps=[
            (
                "preprocessing",
                create_preprocessor(),
            ),
            (
                "regressor",
                RandomForestRegressor(
                    n_estimators=FOREST_ESTIMATORS,
                    min_samples_leaf=FOREST_MIN_SAMPLES_LEAF,
                    random_state=RANDOM_STATE,
                    n_jobs=-1,
                ),
            ),
        ]
    )


def evaluate_model(
    model: Pipeline,
    features: pd.DataFrame,
    targets: pd.Series,
) -> dict[str, float]:
    """Evaluate regression performance on held-out data."""
    predictions = model.predict(features)

    mae = mean_absolute_error(
        targets,
        predictions,
    )

    rmse = np.sqrt(
        mean_squared_error(
            targets,
            predictions,
        )
    )

    r2 = r2_score(
        targets,
        predictions,
    )

    return {
        "MAE": float(mae),
        "RMSE": float(rmse),
        "R2": float(r2),
    }


def print_evaluation(
    model_name: str,
    metrics: dict[str, float],
) -> None:
    """Print regression metrics using consistent formatting."""
    print(f"\n{model_name}")
    print("-" * 50)

    print(
        f"MAE:  {metrics['MAE']:.4f} million copies"
    )

    print(
        f"RMSE: {metrics['RMSE']:.4f} million copies"
    )

    print(
        f"R²:   {metrics['R2']:.4f}"
    )


def create_training_metadata(
    full_df: pd.DataFrame,
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    baseline_metrics: dict[str, float],
    forest_metrics: dict[str, float],
) -> dict:
    """Create reproducible metadata for the trained model artifact."""
    training_groups = (
        train_df[GROUP_COLUMN]
        .str.casefold()
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    test_groups = (
        test_df[GROUP_COLUMN]
        .str.casefold()
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    return {
        "model_name": "RandomForestRegressor",
        "model_status": "experimental",
        "trained_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "data_source": str(
            DATA_PATH.relative_to(BASE_DIR)
        ),
        "feature_columns": FEATURE_COLUMNS,
        "target_column": TARGET_COLUMN,
        "target_unit": "million_copies",
        "year_range": {
            "start": START_YEAR,
            "end": END_YEAR,
        },
        "split": {
            "method": "GroupShuffleSplit",
            "group_column": GROUP_COLUMN,
            "test_size": TEST_SIZE,
            "random_state": RANDOM_STATE,
            "training_records": len(train_df),
            "test_records": len(test_df),
            "training_titles": training_groups.nunique(),
            "test_titles": test_groups.nunique(),
        },
        "total_valid_records": len(full_df),
        "model_parameters": {
            "n_estimators": FOREST_ESTIMATORS,
            "min_samples_leaf": FOREST_MIN_SAMPLES_LEAF,
            "random_state": RANDOM_STATE,
        },
        "evaluation": {
            "baseline": baseline_metrics,
            "random_forest": forest_metrics,
        },
        "sklearn_version": sklearn.__version__,
        "limitations": [
            "Single grouped holdout evaluation",
            "No temporal generalization test",
            "Historical dataset with incomplete market coverage",
            "Only platform, genre, and release year used as features",
            "Estimates are not calibrated prediction intervals",
        ],
    }


def save_training_artifacts(
    model: Pipeline,
    metadata: dict,
) -> None:
    """Save the trained regression pipeline and evaluation metadata."""
    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        model,
        MODEL_PATH,
    )

    with METRICS_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            metadata,
            file,
            indent=2,
            ensure_ascii=False,
        )


def main() -> None:
    """Train, evaluate, and persist the experimental regression model."""
    print("=" * 60)
    print("GAME SALES ANALYTICS - MODEL TRAINING")
    print("=" * 60)

    raw_df = load_training_data(
        DATA_PATH
    )

    prepared_df = prepare_training_data(
        raw_df
    )

    train_df, test_df = split_training_data(
        prepared_df
    )

    x_train = train_df[FEATURE_COLUMNS]
    y_train = train_df[TARGET_COLUMN]

    x_test = test_df[FEATURE_COLUMNS]
    y_test = test_df[TARGET_COLUMN]

    print(f"\nValid records: {len(prepared_df):,}")
    print(f"Training records: {len(train_df):,}")
    print(f"Test records: {len(test_df):,}")

    print(
        "Unique game titles:",
        f"{prepared_df[GROUP_COLUMN].nunique():,}",
    )

    print("\nTraining dummy baseline...")

    baseline = create_baseline_pipeline()

    baseline.fit(
        x_train,
        y_train,
    )

    baseline_metrics = evaluate_model(
        baseline,
        x_test,
        y_test,
    )

    print("\nTraining Random Forest...")

    forest = create_random_forest_pipeline()

    forest.fit(
        x_train,
        y_train,
    )

    forest_metrics = evaluate_model(
        forest,
        x_test,
        y_test,
    )

    print_evaluation(
        "Dummy Baseline",
        baseline_metrics,
    )

    print_evaluation(
        "Random Forest",
        forest_metrics,
    )

    metadata = create_training_metadata(
        full_df=prepared_df,
        train_df=train_df,
        test_df=test_df,
        baseline_metrics=baseline_metrics,
        forest_metrics=forest_metrics,
    )

    save_training_artifacts(
        model=forest,
        metadata=metadata,
    )

    print("\nModel artifacts saved successfully.")
    print(f"Model: {MODEL_PATH}")
    print(f"Metrics: {METRICS_PATH}")

    if (
        forest_metrics["MAE"] < baseline_metrics["MAE"]
        and forest_metrics["RMSE"] < baseline_metrics["RMSE"]
    ):
        print(
            "\nThe Random Forest improves both error metrics "
            "relative to the dummy baseline."
        )
    else:
        print(
            "\nThe Random Forest does not consistently outperform "
            "the dummy baseline on this test set."
        )

    print(
        "\nEvaluation limitation: This is a single grouped "
        "holdout test, not a time-based forecast evaluation."
    )


if __name__ == "__main__":
    main()
