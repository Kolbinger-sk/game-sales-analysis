# Game Sales Analytics

**An end-to-end Python data analytics project exploring historical video game sales through data preparation, exploratory analysis, SQL, interactive dashboards, and experimental machine learning.**

This project demonstrates a complete analytical workflow, from processing a raw dataset to building an interactive Streamlit application and evaluating a regression model.

## Project Overview

Game Sales Analytics explores historical video game sales across gaming platforms, genres, publishers, release years, and geographic regions.

The project combines:

- **Python and Pandas** for data preparation and exploratory analysis
- **SQLite and SQL** for structured data storage and analytical queries
- **Matplotlib and Plotly** for visualizations
- **Streamlit** for an interactive multipage dashboard
- **Scikit-learn** for experimental sales prediction
- **Pytest** for automated testing

The main objective is to demonstrate a reproducible data analysis workflow while clearly documenting dataset limitations and model performance.

## Dataset

**Source:** [Video Game Sales — Kaggle](https://www.kaggle.com/datasets/gregorut/videogamesales)

The dataset contains approximately 16,600 game-platform records and includes:

| Column | Description |
|---|---|
| `Rank` | Sales ranking in the source dataset |
| `Name` | Video game title |
| `Platform` | Gaming platform |
| `Year` | Game release year |
| `Genre` | Game genre |
| `Publisher` | Game publisher |
| `NA_Sales` | Recorded sales in North America |
| `EU_Sales` | Recorded sales in Europe |
| `JP_Sales` | Recorded sales in Japan |
| `Other_Sales` | Recorded sales in other regions |
| `Global_Sales` | Recorded global sales |

Sales figures are expressed in **millions of copies**.

### Dataset Limitations

Several limitations are important when interpreting the results:

- The dataset represents historical sales estimates and does not cover the entire video game market.
- A game released on multiple platforms may appear in multiple rows.
- Game counts therefore represent **game-platform entries**, not necessarily unique titles.
- Sales values represent recorded cumulative sales, not transactions occurring within a particular calendar year.
- Analyses grouped by `Year` describe games released in that year, rather than sales made during that year.
- Some records have missing release years or publishers.
- Regional totals may differ slightly from `Global_Sales` because of rounding.
- Recent games and modern digital distribution are not comprehensively represented.

These limitations are considered throughout the analysis and dashboard.

## Project Structure

```text
game-sales-analysis/
│
├── data/
│   ├── raw/
│   │   └── vgsales.csv
│   └── processed/
│       ├── vgsales_clean.csv
│       ├── vgsales_with_year.csv
│       ├── yearly_sales.csv
│       ├── platform_statistics.csv
│       ├── regional_statistics.csv
│       └── genre_regional_statistics.csv
│
├── database/
│   └── games.db
│
├── dashboard/
│   ├── app.py
│   ├── data_loader.py
│   └── pages/
│       ├── 1_Games.py
│       ├── 2_Genres.py
│       ├── 3_Platforms.py
│       ├── 4_Regions.py
│       └── 5_Predictions.py
│
├── images/
│
├── models/
│   ├── sales_model.joblib
│   └── sales_model_metrics.json
│
├── notebooks/
│
├── src/
│   ├── database_setup.py
│   ├── sql_analysis.py
│   ├── platform_analysis.py
│   ├── regional_analysis.py
│   ├── time_analysis.py
│   └── train_model.py
│
├── tests/
│   ├── test_data_cleaning.py
│   ├── test_sales_analysis.py
│   └── test_model_training.py
│
├── .gitignore
├── main.py
├── requirements.txt
└── README.md
```

**Note:** The raw and processed CSV files, SQLite database, and trained `.joblib` model are excluded from Git tracking. They must be downloaded or generated locally as described below. Some generated files and folders only appear after running the relevant scripts.

## Features

### 1. Data Preparation

The main data preparation script:

- Loads and validates the source CSV.
- Standardizes relevant data types.
- Checks for missing and invalid sales values.
- Removes duplicate records.
- Replaces missing publisher names with `Unknown`.
- Preserves missing release years for general sales analyses.
- Creates a separate dataset for release-year-based analyses.
- Generates initial genre visualizations.

**Output datasets:**

`data/processed/vgsales_clean.csv` — cleaned records for general analysis, including entries with missing release years.

`data/processed/vgsales_with_year.csv` — records with valid release years between 1980 and 2016.

### 2. Exploratory Data Analysis

The analysis scripts examine:

**Genre Analysis**
- Distribution of game-platform entries across genres
- Recorded global sales by genre
- Comparisons of genre performance

**Platform Analysis**
- Total sales by gaming platform
- Game entry counts
- Average and median sales
- Rankings of leading platforms

**Regional Analysis**
- Sales across North America, Europe, Japan, and other regions
- Regional sales shares within the dataset
- Genre performance by region
- Regional comparisons across platforms

**Release-Year Analysis**
- Recorded sales grouped by game release year
- Regional sales grouped by release year
- Percentage changes between consecutive release-year groups

Release-year comparisons are descriptive and **must not be interpreted as actual annual market growth**.

### 3. SQLite Database and SQL Analysis

Cleaned data is imported into a local SQLite database.

The database contains a `games` table used by the SQL analysis scripts and Streamlit dashboard.

The SQL analysis includes:

- Highest-selling game-platform entries
- Sales rankings for selected gaming platforms
- Total and average sales by genre
- Genres with a minimum number of game entries
- Filtered analyses by platform, genre, and release year
- Publisher rankings
- Regional sales totals

The SQL analysis module uses parameterized queries and read-only database access.

### 4. Interactive Streamlit Dashboard

The multipage dashboard provides five analysis sections:

| Page | Features |
|---|---|
| **Games** | Search game titles, filter by platform, inspect top-selling entries, export results |
| **Genres** | Compare total, average, and median sales across genres |
| **Platforms** | Explore rankings and compare two gaming platforms |
| **Regions** | Analyze regional sales, genre differences, and platform distributions |
| **Predictions** | Explore experimental machine-learning estimates and model evaluation |

The overview page displays headline metrics, top genres, top platforms, and historical sales grouped by release year.

All pages use a shared SQLite data loader with Streamlit caching.

### 5. Experimental Machine Learning

The project includes a regression pipeline designed to estimate recorded global sales using three features:

- `Platform`
- `Genre`
- `Year`

**Models:**
- Dummy Regressor using the training-set mean
- Random Forest Regressor

**Preprocessing:**
- One-hot encoding for categorical features
- Numeric processing for release year
- Scikit-learn pipelines to keep preprocessing and modeling together

**Evaluation:**
- Mean Absolute Error (MAE)
- Root Mean Squared Error (RMSE)
- Coefficient of Determination (R²)

A title-grouped train-test split reduces overlap between records of the same video game across platforms.

The trained model is saved to:

```text
models/sales_model.joblib
```

Its evaluation metadata is saved to:

```text
models/sales_model_metrics.json
```

The dashboard reads these evaluation results from the metadata file.

**Model limitations:** The initial Random Forest evaluation did not demonstrate convincing predictive performance relative to a simple baseline. The prediction functionality is therefore explicitly presented as an experimental demonstration rather than a reliable forecasting tool.

The current evaluation uses a single grouped holdout split, not a temporal forecast validation. Additional evaluation and stronger predictive features would be required before drawing substantive conclusions from its estimates.

## Installation

### Prerequisites

- Python 3.10 or newer
- Git
- An internet connection to download the dataset and Python dependencies

A Python virtual environment is recommended.

### 1. Clone the Repository

```bash
git clone https://github.com/Kolbinger-sk/game-sales-analysis.git
cd game-sales-analysis
```

### 2. Create a Virtual Environment

On Windows:

```powershell
python -m venv .venv
```

Activate it in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

The main dependencies include Pandas, NumPy, Matplotlib, Plotly, Streamlit, Scikit-learn, Joblib, and Pytest.

### 4. Download the Dataset

Download the dataset from:

[Video Game Sales — Kaggle](https://www.kaggle.com/datasets/gregorut/videogamesales)

Extract the archive and place `vgsales.csv` in:

```text
data/raw/vgsales.csv
```

The CSV is not included in the Git repository.

## Running the Project

Execute the following commands from the **project root directory**.

### Step 1: Prepare the Data

```bash
python main.py
```

This creates the cleaned datasets and initial charts.

### Step 2: Build the SQLite Database

```bash
python src/database_setup.py
```

This creates or replaces the `games` table in:

```text
database/games.db
```

### Step 3: Run the Analyses

Release-year analysis:

```bash
python src/time_analysis.py
```

Platform analysis:

```bash
python src/platform_analysis.py
```

Regional analysis:

```bash
python src/regional_analysis.py
```

SQL analysis:

```bash
python src/sql_analysis.py
```

These scripts generate reports, charts, and processed CSV files where applicable.

### Step 4: Train the Machine-Learning Model

```bash
python src/train_model.py
```

This trains the baseline and Random Forest models, evaluates them on a grouped holdout set, and saves the model and evaluation metadata.

**Note:** Running this script overwrites existing generated model artifacts.

### Step 5: Launch the Dashboard

```bash
python -m streamlit run dashboard/app.py
```

Streamlit displays a local browser address, typically:

```text
http://localhost:8501
```

Open the address to explore the dashboard.

The Predictions page requires both the saved `.joblib` model and its JSON metadata file.

## Automated Testing

The project uses **Pytest** to validate important data-processing and modeling functions.

Run the complete test suite from the project root:

```bash
python -m pytest -v
```

Tests cover:

- Handling of missing release years
- Removal of invalid sales records and duplicates
- Aggregation of platform, genre, regional, and release-year sales
- Percentage-change calculations
- Preparation of machine-learning training data
- Prevention of title overlap between training and test partitions
- Basic regression pipeline compatibility

The current test suite focuses on calculation logic. Dashboard integration tests, database integration tests, and comprehensive model validation remain potential improvements.

## Reproducibility

The project uses a documented workflow and a fixed random seed for its machine-learning split and Random Forest model.

Reproducibility is supported through:

- A shared cleaned dataset
- Separate processing and analytical scripts
- Parameterized SQL queries
- A fixed random state for model training
- Saved model evaluation metadata
- Declared Python dependencies
- Automated tests

Exact results may still depend on dataset and dependency versions.

## Technologies

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Pandas | Data cleaning and analysis |
| NumPy | Numerical operations |
| SQLite | Local relational database |
| SQL | Structured analytical queries |
| Matplotlib | Static data visualization |
| Plotly | Interactive charts |
| Streamlit | Multipage dashboard |
| Scikit-learn | Machine learning and evaluation |
| Joblib | Model serialization |
| Pytest | Automated testing |
| Git & GitHub | Version control and project documentation |

## Future Improvements

Potential extensions include:

- More comprehensive automated integration tests
- Stronger validation of the data preparation pipeline
- Cross-validation and time-based model evaluation
- Improved predictive features and model comparison
- Automated checks for model and metadata consistency
- Additional dashboard filters and visualizations
- More detailed analysis of dataset coverage and potential biases
- Reproducible dependency locking and CI-based test execution

## Author

**Kolbinger-sk**

GitHub: [Kolbinger-sk](https://github.com/Kolbinger-sk)

## Data Attribution

The analysis uses the publicly available [Video Game Sales dataset on Kaggle](https://www.kaggle.com/datasets/gregorut/videogamesales).

The dataset is not redistributed with this repository. Users should obtain the data from the original source and review its applicable terms before reuse.

---

*Game Sales Analytics is a portfolio project demonstrating Python data analysis, SQL, visualization, dashboard development, and experimental machine learning.*