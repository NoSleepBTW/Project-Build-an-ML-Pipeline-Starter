# Short-Term Rental Price Estimation — NYC

An end-to-end, reproducible MLOps pipeline that predicts the typical nightly price of a
short-term rental in New York City from its listing attributes. A property-management company
receives fresh listing data in bulk every week, so the model has to be **retrained on a regular
cadence** — this project packages the whole train/validate/test/release cycle so a retrain is a
single command.

The pipeline is built with **MLflow** (orchestration + model packaging), **Hydra**
(configuration), and **Weights & Biases** (data/artifact versioning and experiment tracking).

## Links

- **W&B project:** https://wandb.ai/coreymlehman-western-governors-university/nyc_airbnb
- **GitHub repository:** https://github.com/NoSleepBTW/Project-Build-an-ML-Pipeline-Starter
- **Releases:** [`V1.0.0`](https://github.com/NoSleepBTW/Project-Build-an-ML-Pipeline-Starter/releases/tag/V1.0.0) — initial pipeline · [`V1.0.1`](https://github.com/NoSleepBTW/Project-Build-an-ML-Pipeline-Starter/releases/tag/V1.0.1) — adds the NYC geographic-bounds filter

> The W&B project is hosted under a Western Governors University organization account whose
> privacy policy caps project visibility at "Team", so a fully public link isn't available from
> this account. Reviewer access can be granted on request.

## Pipeline

```
download → basic_cleaning → data_check → data_split → train_random_forest → test_regression_model
```

| Step | What it does |
|------|--------------|
| `download` | Fetches the raw sample and logs it to W&B as `sample.csv`. |
| `basic_cleaning` | Drops price outliers, parses `last_review` dates, and removes listings outside the NYC bounding box; logs `clean_sample.csv`. |
| `data_check` | Pytest data-integrity tests (row count, price range, geographic bounds, column schema, and a KL-divergence check against a tagged `reference` dataset). |
| `data_split` | Stratified split into `trainval_data.csv` and `test_data.csv`. |
| `train_random_forest` | Builds an sklearn inference pipeline (preprocessing + Random Forest), fits it, logs MAE/R² and feature importance, and exports the model with MLflow. |
| `test_regression_model` | Scores the `prod` model on the held-out test set. Run explicitly, only after a model is promoted to `prod`. |

## What I built

- **`basic_cleaning` component** (`src/basic_cleaning/run.py`) — fully typed/documented data
  cleaning, including the NYC latitude/longitude filter that makes the pipeline robust to the
  out-of-area coordinates present in newer data batches.
- **Data-integrity tests** (`src/data_check/test_data.py`) — implemented `test_row_count` and
  `test_price_range` (price bounds pulled from config, never hardcoded).
- **Random Forest training** (`src/train_random_forest/run.py`) — assembled the preprocessing
  for ordinal/non-ordinal categoricals, numeric imputation, a date-delta feature, and TF-IDF on
  the listing name; combined preprocessing and the Random Forest into a single named
  `Pipeline`; fit it; logged metrics; and exported it as an MLflow sklearn model artifact.
- **Pipeline wiring** (`main.py`) — added the `data_split`, `train_random_forest`, and
  `test_regression_model` steps, with every argument sourced from `config.yaml`.

## Results

The model was tuned with a Hydra multirun sweep over `max_depth` (10/30/50) and `n_estimators`
(100/200). The configuration with the best validation MAE was promoted to `prod` in W&B.

| Dataset | MAE | R² |
|---------|-----|-----|
| Validation (`prod` model) | 34.13 | 0.55 |
| **Held-out test set** | **33.85** | **0.56** |
| Retrain on new batch (`sample2.csv`, `V1.0.1`) | 32.42 | 0.58 |

Test-set performance matching validation confirms the model generalizes rather than overfits.

## Handling a new data batch

`V1.0.0` was deliberately run against `sample2.csv` and **failed** the geographic-bounds data
check — newer data contains listings outside NYC. The fix (a latitude/longitude filter in
`basic_cleaning`) was released as `V1.0.1`, after which the released pipeline trains successfully
on the new batch. This demonstrates the data-check stage catching a real data-quality regression
before it reaches the model.

## Quickstart

Full setup and troubleshooting details are in [`docs/STARTER_README.md`](docs/STARTER_README.md).

```bash
# 1. Environment
conda env create -f environment.yml
conda activate nyc_airbnb_dev

# 2. Authenticate Weights & Biases
wandb login [your API key]

# 3. Run the whole pipeline
mlflow run .

# Run a subset of steps
mlflow run . -P steps=basic_cleaning,data_check

# Hyperparameter sweep (Hydra multirun)
mlflow run . -P steps=train_random_forest \
  -P hydra_options="modeling.random_forest.max_depth=10,30,50 modeling.random_forest.n_estimators=100,200 -m"

# Run the released pipeline on a new data batch
mlflow run https://github.com/NoSleepBTW/Project-Build-an-ML-Pipeline-Starter.git \
  -v V1.0.1 -P hydra_options="etl.sample='sample2.csv'"
```

`test_regression_model` is excluded from the default steps; run it explicitly after promoting a
model to `prod`:

```bash
mlflow run . -P steps=test_regression_model
```

## Project structure

```
main.py                      Pipeline orchestration (MLflow + Hydra)
config.yaml                  All pipeline/model parameters
src/
  basic_cleaning/            Data cleaning component
  data_check/                Pytest data-integrity tests
  train_random_forest/       Model training + MLflow export
components/                  Pre-built reusable components (get_data, split, test_model)
docs/STARTER_README.md       Original Udacity setup & troubleshooting reference
```

## License
[License](LICENSE.txt)
