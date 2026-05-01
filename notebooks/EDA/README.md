# Exploratory Data Analysis (EDA)

All EDA notebooks operate on the **train split only** (`data/processed/train.parquet`)
to prevent leaking test-set patterns into feature engineering decisions.

## Notebook sequence

| Notebook | Focus | Key questions answered |
|----------|-------|----------------------|
| `eda_00_data_profile` | Shape, dtypes, missing values, cardinality | What does the data look like? What's usable? |
| `eda_01_target_analysis` | `Results` distribution, class imbalance | Binary or ternary target? How imbalanced? |
| `eda_02_categorical_features` | Risk, Facility Type, Inspection Type, license fields, flags | Cardinality? Rare categories? Encoding strategy? |
| `eda_03_temporal_geospatial` | Inspection Date trends, lat/long, zip codes | Seasonality? Geographic clusters? |
| `eda_04_bivariate` | Each feature vs Results, correlations | Which features predict the target? |

## Running

Execute notebooks in order (`00` → `04`). Each is self-contained but findings
from earlier notebooks provide context for later ones.
