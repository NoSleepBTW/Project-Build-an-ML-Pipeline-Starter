# Starter Kit Reference (Udacity)

This file preserves the original setup, execution, and troubleshooting instructions that
shipped with the Udacity starter kit. The project-specific write-up lives in the top-level
[README](../README.md).

## Preliminary steps

### Supported operating systems
- **Ubuntu 22.04 / 24.04** (native or WSL)
- **macOS** (recent versions)

### Python requirement
This project requires **Python 3.13**.

### Create environment
With conda installed, create and activate the development environment:

```bash
conda env create -f environment.yml
conda activate nyc_airbnb_dev
```

### Get an API key for Weights & Biases
Grab your key from [https://wandb.ai/authorize](https://wandb.ai/authorize) and log in:

```bash
wandb login [your API key]
```

### The configuration
Pipeline parameters live in `config.yaml` and are managed with Hydra. `config.yaml` is read
only by `main.py`, where its contents are available through the `config` dictionary (e.g.
`config["main"]["project_name"]`). Do **not** hardcode parameters in the pipeline — read them
from the configuration file.

### Running the entire pipeline or a selection of steps
Run the whole pipeline from the repo root:

```bash
mlflow run .
```

Run a single step (or a comma-separated subset):

```bash
mlflow run . -P steps=download
mlflow run . -P steps=download,basic_cleaning
```

Override any config value with Hydra syntax via `hydra_options`:

```bash
mlflow run . \
  -P steps=download,basic_cleaning \
  -P hydra_options="modeling.random_forest.n_estimators=10 etl.min_price=50"
```

### Pre-existing components
Some reusable components are consumed directly from the upstream repository through
`config['main']['components_repository']`, e.g. `get_data` and `train_val_test_split`.
Check each component's `MLproject` file for its required parameters.

## In case of errors

### Environments
A bad `conda.yml` can leave a corrupted environment. List the mlflow-created environments:

```bash
conda info --envs | grep mlflow | cut -f1 -d" "
```

Remove **all** mlflow environments (use at your own risk):

```bash
for e in $(conda info --envs | grep mlflow | cut -f1 -d" "); do conda uninstall --name $e --all -y; done
```

### MLflow & W&B
If `mlflow run .` errors, make sure every step uses the **same** Python version, that conda is
installed, and that the `mlflow` and `wandb` package versions match across environments.

## License
[License](../LICENSE.txt)
