# OncoTrace 🧬
### A Rust-Validated Bioinformatics Pipeline for Breast Cancer Survival Analysis

OncoTrace is a bioinformatics and machine learning project that explores how clinical characteristics and molecular features can be used to study survival outcomes in breast cancer patients.

The project uses the METABRIC breast cancer dataset to build a reproducible workflow covering data validation, quality checks, preprocessing, exploratory analysis, survival statistics, and machine learning. It combines **Rust for structured data validation** with **Python for statistical analysis, survival modelling, visualization, and evaluation**.

The goal is to make the process of working with complex cancer datasets more systematic, transparent, and reproducible—from checking the raw data to comparing survival models and examining their results.

> **Research status:** OncoTrace is an experimental computational research project. Its current results are preliminary and are not intended for clinical decision-making, individual prognosis, or treatment recommendations.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Why OncoTrace?](#why-oncotrace)
- [Research Objectives](#research-objectives)
- [Dataset](#dataset)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [Analysis Pipeline](#analysis-pipeline)
- [Survival Models](#survival-models)
- [Preliminary Results](#preliminary-results)
- [Visualizations and Reports](#visualizations-and-reports)
- [Project Structure](#project-structure)
- [Installation and Setup](#installation-and-setup)
- [Running OncoTrace](#running-oncotrace)
- [Testing](#testing)
- [Reproducibility](#reproducibility)
- [Current Limitations](#current-limitations)
- [Planned Improvements](#planned-improvements)
- [Ethical Considerations](#ethical-considerations)
- [License](#license)
- [Acknowledgements](#acknowledgements)

---

## Project Overview

Cancer survival analysis involves more than predicting whether an outcome will occur. Researchers must account for the time until an event, patients who have not experienced the event during follow-up, differences in clinical characteristics, and the statistical assumptions underlying their models.

OncoTrace approaches this problem through a structured computational pipeline.

The current implementation:

- Validates the structure and consistency of the raw dataset using a Rust-based CSV validation stage.
- Audits missing values, column types, and important survival-related fields.
- Prepares data for downstream statistical analysis.
- Estimates baseline survival patterns using Kaplan–Meier analysis.
- Examines survival differences between groups using the log-rank test.
- Fits a Cox proportional hazards model.
- Evaluates a Random Survival Forest model.
- Generates figures and reports to make the analysis easier to inspect.
- Includes automated tests to check core pipeline functionality.

Rather than treating model training as the entire project, OncoTrace emphasizes the full workflow surrounding a survival-analysis experiment: data quality, assumptions, evaluation, and reproducibility.

## Why OncoTrace?

Cancer-related datasets frequently combine clinical information, treatment characteristics, molecular measurements, and patient outcomes. These variables can have different data types, different levels of missingness, and different relationships with the outcome being studied.

A reliable analysis must address several questions:

1. Is the input data structurally valid?
2. Are the survival time and event indicator defined correctly?
3. Which variables are appropriate for use as predictors?
4. How do observed survival patterns differ between patient groups?
5. How well do statistical and machine learning models rank patient outcomes?
6. Are the evaluation results trustworthy, or could preprocessing and validation choices have inflated performance?

OncoTrace was developed to explore these questions in one reproducible project.

The Rust and Python components also provide an opportunity to combine systems-level data validation with the scientific computing ecosystem used in bioinformatics.

## Research Objectives

The project has five main objectives.

**1. Establish data quality before analysis**

Inspect the dataset's schema, record count, data types, missing values, and survival-related fields before using it for modelling.

**2. Characterize the survival outcomes**

Use descriptive statistics and non-parametric survival analysis to understand the observed distribution of survival times.

**3. Build statistical and machine learning baselines**

Compare a conventional survival regression model with a tree-based survival model.

**4. Make the workflow inspectable**

Produce reports, plots, processed data, and automated tests so that the analysis can be reviewed rather than treated as a black box.

**5. Identify what needs further validation**

Document the limitations of the current experiment and establish a path toward more rigorous evaluation.

## Dataset

OncoTrace currently uses the **METABRIC breast cancer dataset**, specifically the file:

`METABRIC_RNA_Mutation.csv`

The file is located in the project's `data/raw/` directory.

The inspected dataset contains:

| Property | Observed value |
|---|---:|
| Records | 1,904 |
| Columns | 693 |
| Overall survival time | `overall_survival_months` |
| Overall survival indicator | `overall_survival` |
| Cancer-specific outcome field | `death_from_cancer` |

The source file contains clinical and molecular-related variables. The exact variables used by each model depend on the preprocessing and feature-selection stages.

### Survival data

Survival analysis generally requires two distinct pieces of information:

- **Duration:** how long a patient was observed before the event or the end of follow-up.
- **Event indicator:** whether the event of interest was observed.

OncoTrace uses `overall_survival_months` as its survival-duration field and examines `overall_survival` as the event-related field. The exact event coding must be confirmed against the dataset's data dictionary and verified in the preprocessing code before interpreting final results.

The `death_from_cancer` field also requires careful treatment. It is not automatically a suitable predictor simply because it appears in the dataset. If it describes a cause of death or information determined after follow-up, using it as a feature could introduce target leakage or change the research question.

### Obtaining the data

The METABRIC data file should be obtained from the original dataset provider or the authorized dataset-hosting page. Place the downloaded CSV at:

`data/raw/METABRIC_RNA_Mutation.csv`

The dataset is not reproduced in this repository. Before redistributing it, check the source's licensing, attribution, and usage requirements.

## Technology Stack

| Technology | Role in OncoTrace |
|---|---|
| Rust | CSV and schema validation |
| Python | Analysis pipeline and orchestration |
| pandas / NumPy | Tabular data handling and numerical operations |
| SciPy / statistical libraries | Statistical calculations and hypothesis testing |
| scikit-learn ecosystem | Machine learning utilities and evaluation support |
| scikit-survival or equivalent survival tooling | Survival-model implementation, where configured |
| Matplotlib | Figures and visual reports |
| pytest | Automated testing |
| Jupyter Notebook | Exploratory analysis and interactive inspection |

The exact installed package versions should be recorded in the project's dependency files to support repeatable execution.

## System Architecture

OncoTrace separates input validation from scientific analysis.

```text
                 METABRIC CSV
                      |
                      v
            Rust Data Validation
                      |
                      v
             Python Orchestrator
                   main.py
                      |
          +-----------+-----------+
          |           |           |
          v           v           v
      Data Audit  Preprocessing  Target Audit
          |           |           |
          +-----------+-----------+
                      |
                      v
             Survival Analysis
                      |
          +-----------+-----------+
          |           |           |
          v           v           v
      Kaplan–Meier  Cox Model  Survival Forest
          |           |           |
          +-----------+-----------+
                      |
                      v
          Evaluation, Figures and Reports
```

This architecture gives each stage a defined responsibility and makes it easier to isolate failures or inspect intermediate outputs.

### Why use Rust and Python together?

Rust is used for the initial validation stage, where explicit checks on input structure and records can catch problems before the data reaches the analytical pipeline.

Python is used for the statistical and machine learning stages because of its extensive scientific computing and survival-analysis ecosystem.

The combination is intended to keep the data-ingestion boundary separate from the research logic.

## Analysis Pipeline

### 1. Raw data validation

The Rust component checks the input CSV and validates its records before the Python analysis proceeds.

The initial execution successfully validated **1,904 records**.

This stage is intended to catch structural problems early, rather than allowing malformed input to cause less obvious failures during model fitting.

### 2. Data audit

The Python audit examines the dataset's dimensions, data types, missing values, and key survival fields.

The initial inspection identified a missing value in `death_from_cancer` and mixed-type warnings in several columns near the end of the source file. These findings require explicit handling instead of silently coercing every value into a numeric format.

The audit helps distinguish expected missing data from potential schema or preprocessing problems.

### 3. Target and feature audit

Survival modelling requires a clear definition of the target variables.

OncoTrace separates survival duration and event status from candidate predictors. Features that reveal the outcome directly, encode post-outcome information, or would not have been available at the intended prediction time must be excluded or justified.

This is particularly important when clinical outcome fields appear alongside candidate predictors in the same dataset.

### 4. Preprocessing

The preprocessing stage prepares the raw data for downstream analysis. Depending on the variable, this may involve handling missing values, converting data types, encoding categorical features, and selecting suitable columns.

Preprocessing decisions must be learned from the training data only whenever they affect model fitting. Applying transformations using information from the full dataset before creating validation splits can introduce leakage.

This is one of the issues that must be resolved before the current performance figures can be considered final.

### 5. Kaplan–Meier survival analysis

The Kaplan–Meier estimator provides a non-parametric estimate of the survival function over time.

It accounts for right-censored observations, provided the duration and event variables have been correctly defined.

OncoTrace uses this analysis to establish a baseline view of survival patterns before relying on more complex models.

### 6. Group comparison with the log-rank test

The log-rank test compares survival distributions between groups.

The current analysis includes an exploratory comparison involving estrogen receptor (ER) status. The resulting p-value is a measure of evidence against the null hypothesis of equal survival distributions under the test's assumptions; it does not establish causation or prove that ER status alone determines survival.

The group definitions, sample sizes, censoring patterns, and any multiple-testing considerations should be reviewed when interpreting this result.

### 7. Cox proportional hazards model

The Cox proportional hazards model relates candidate predictors to the hazard of the event over time.

It is a useful statistical baseline because its coefficients can be interpreted in terms of hazard ratios, subject to the model specification and assumptions.

A Cox model should be checked for issues such as:

- Proportional hazards violations.
- Unstable or highly correlated predictors.
- Missing data and inappropriate feature encodings.
- Overfitting relative to the number of observed events.
- Leakage between training and validation data.

OncoTrace currently evaluates the Cox model using cross-validation, but the complete preprocessing and validation design requires further review.

### 8. Random Survival Forest

Random Survival Forest is a tree-based approach designed for time-to-event data. It can capture non-linear relationships and interactions that a conventional Cox model may not represent without additional modelling choices.

The current experiment uses a Random Survival Forest with 178 features in its reported evaluation.

Its performance is compared using the concordance index, which measures the model's ability to rank comparable patient pairs by their observed event times.

The model's feature count and reported score should be treated as experimental results, not evidence that all included features are clinically meaningful.

### 9. Reporting and visualization

The final stages produce figures and reports for inspecting the data and the modelling results.

These artifacts help make the workflow more transparent and provide a basis for checking whether the reported conclusions are supported by the underlying analysis.

## Survival Models

| Model | Purpose | Main evaluation |
|---|---|---|
| Kaplan–Meier estimator | Estimate baseline survival over time | Survival curve and summary estimates |
| Log-rank test | Compare survival distributions between groups | p-value |
| Cox proportional hazards | Model covariate relationships with the hazard | Concordance index and model diagnostics |
| Random Survival Forest | Capture potentially non-linear survival relationships | Concordance index |

The Cox model and Random Survival Forest address related but different modelling assumptions. Their results should be compared on the same properly defined evaluation data and with consistent outcome definitions.

## Preliminary Results

The following values are from the current end-to-end run. They are included to document the state of the experiment, not as final or clinically validated performance claims.

| Analysis | Preliminary result |
|---|---:|
| Records validated by Rust | 1,904 |
| Automated tests passing | 10/10 |
| Cox proportional hazards, 5-fold cross-validation C-index | 0.6573 ± 0.0138 |
| Random Survival Forest, reported 80/20 test C-index | 0.6816 |
| Median observed survival time | 154.50 months |
| Estimated 5-year survival | 77.94% |
| Estimated 10-year survival | 58.86% |
| Exploratory ER-group log-rank p-value | 0.021597 |
| Features used by the reported Random Survival Forest | 178 |

### Interpreting the results

**C-index:** A concordance index measures how often a model correctly ranks comparable pairs. A value of 0.5 is generally consistent with chance-level ranking under the usual interpretation, while higher values indicate better ranking. C-index values do not directly measure the accuracy of individual survival-time predictions.

**Cross-validation:** The Cox result reports the mean and standard deviation across five folds. Its reliability depends on how folds were created and whether all preprocessing steps were fitted independently within each training fold.

**Median and survival estimates:** The survival summaries are descriptive estimates from the current analysis. They are not individualized forecasts and should not be interpreted as the expected outcome for a particular patient.

**Log-rank p-value:** The reported p-value suggests a difference between the survival distributions being compared under the test assumptions. It does not establish a causal relationship or measure the clinical importance of that difference.

### Important evaluation qualification

Potential preprocessing and validation leakage has not yet been fully resolved. For this reason, the reported C-index values should be considered **provisional**.

Before treating them as reliable generalization estimates, the pipeline needs to be checked for:

1. Preprocessing or feature selection performed before splitting the data.
2. Any outcome-derived or post-outcome variables entering the predictors.
3. Inconsistent event coding or handling of censored observations.
4. Inappropriate reuse of the test set during model development.
5. Validation splits that do not reflect the intended use of the model.

The final results should be regenerated after these checks have been completed.

## Visualizations and Reports

The current run generates seven figures and four reports.

These artifacts are intended to document the data audit, survival analysis, and model evaluation. Their precise contents should be confirmed from the generated filenames and report headings in the repository.

Suggested artifacts to highlight here include:

- Dataset audit and missing-value summaries.
- Kaplan–Meier survival curves.
- Exploratory survival comparisons by clinical group.
- Cox model results and diagnostic plots.
- Random Survival Forest evaluation results.
- Model comparison summaries.

For GitHub, place final figures in `results/figures/` and reports in `reports/`. If the actual pipeline uses different output paths, update the README to match those paths.

## Project Structure

The following structure reflects the current core modules and outputs. Some generated filenames may differ depending on the latest run.

```text
OncoTrace/
├── data/
│   ├── raw/
│   │   └── METABRIC_RNA_Mutation.csv
│   └── processed/
│       └── processed_dataset.csv
├── rust/
│   └── src/
│       └── main.rs
├── src/
│   └── oncotrace/
│       ├── audit_target.py
│       ├── preprocess.py
│       ├── baseline_survival.py
│       ├── cox_model.py
│       ├── ml_survival.py
│       ├── advanced_visualizations.py
│       └── data_audit.py
├── notebooks/
│   └── exploratory_analysis.ipynb
├── tests/
│   └── ...
├── results/
│   ├── figures/
│   └── tables/
├── reports/
│   └── ...
├── main.py
├── README.md
└── ...
```

### Main components

| File or directory | Responsibility |
|---|---|
| `main.py` | Orchestrates the end-to-end workflow |
| `rust/src/main.rs` | Validates raw CSV input and records |
| `data_audit.py` | Inspects data quality and schema characteristics |
| `audit_target.py` | Checks survival-target and predictor definitions |
| `preprocess.py` | Prepares the data for analysis |
| `baseline_survival.py` | Performs baseline survival analysis |
| `cox_model.py` | Fits and evaluates the Cox model |
| `ml_survival.py` | Implements machine learning survival analysis |
| `advanced_visualizations.py` | Produces analytical figures |
| `tests/` | Contains automated checks for core functionality |
| `notebooks/` | Supports interactive exploration |
| `results/` | Stores generated figures and tabular outputs |
| `reports/` | Stores analysis summaries and reports |

## Installation and Setup

### Prerequisites

- Python 3.11 or another Python version compatible with the project's pinned dependencies.
- Rust and Cargo.
- Git.
- The METABRIC CSV file, obtained from an authorized source.
- A terminal and a code editor.

The exact supported Python version should be confirmed against the installed dependencies before publishing a definitive environment specification.

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd OncoTrace
```

Replace the placeholder with the actual repository URL.

### 2. Create a Python virtual environment

On Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install Python dependencies

If the repository contains a `requirements.txt`:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If it uses another dependency manager, follow the committed lockfile or project configuration instead. The dependency file should reflect the versions that were actually tested.

### 4. Verify Rust

```bash
rustc --version
cargo --version
```

Both commands should return version information.

### 5. Place the dataset

Ensure the raw CSV is available at:

```text
data/raw/METABRIC_RNA_Mutation.csv
```

Do not commit the dataset to Git unless its distribution terms explicitly permit it.

## Running OncoTrace

From the repository root, activate the Python virtual environment and run:

```bash
python main.py
```

The entry point coordinates the validation and analysis stages. On successful execution, the pipeline should produce its configured processed data, figures, and reports.

The Rust component can also be built and checked independently:

```bash
cd rust
cargo check
cargo run --release
```

**Note:** The Rust command assumes the validator's input path and configuration support execution from the `rust/` directory. If the executable expects to be launched from the repository root, use the path and working directory specified in the actual implementation.

Run the Python pipeline from the repository root unless the project configuration explicitly specifies otherwise.

## Testing

OncoTrace currently has **10 passing automated tests** in its latest recorded run.

Run the test suite using:

```bash
pytest
```

The test suite is intended to help detect regressions in core behaviour. The exact coverage depends on the test cases present in the repository; passing tests do not, by themselves, establish the scientific validity of the model or its evaluation results.

Useful additional tests include:

- Malformed CSV files and inconsistent column counts.
- Missing or invalid survival times.
- Invalid event-indicator values.
- Missing-value handling and categorical encoding.
- Exclusion of outcome leakage from model features.
- Correct fitting of preprocessing steps within validation folds.
- Reproducible model evaluation and output generation.

## Reproducibility

Reproducibility is an important part of OncoTrace's design.

To improve reproducibility, the project should maintain:

- A dependency file with pinned or otherwise documented package versions.
- The Rust `Cargo.toml` and `Cargo.lock` files.
- Documented dataset provenance and permitted usage.
- Fixed random seeds wherever applicable.
- A clear definition of survival duration and event coding.
- A record of the features used by each model.
- A consistent train/validation/test strategy.
- Saved evaluation metrics and model configuration.
- Automated tests for critical data-processing steps.

The current pipeline has been executed end to end, but a fully reproducible research release also requires documenting the environment, data source, and final validated evaluation procedure.

## Current Limitations

OncoTrace is an active research and learning project, and several limitations matter when interpreting its output.

### 1. Preliminary validation results

The current evaluation may be affected by leakage in preprocessing or validation. The reported scores should not be treated as definitive until the pipeline has been audited and the models have been reevaluated.

### 2. Dataset scope

The current experiment uses one breast cancer dataset. Performance on this dataset does not demonstrate generalization to other hospitals, populations, datasets, or clinical settings.

### 3. Observational data

Associations found in observational data do not establish causation. A feature associated with survival is not automatically a causal risk factor or a useful treatment target.

### 4. Survival-model assumptions

Cox proportional hazards models require careful assessment of their assumptions. Tree-based survival models have different limitations and may still overfit, particularly when the sample size is limited relative to the number of candidate features.

### 5. Missing data and mixed types

The raw dataset contains missing values and mixed-type columns. Decisions about exclusion, imputation, and encoding can affect model behaviour and must be documented.

### 6. No clinical validation

OncoTrace has not been established as a clinically validated prognostic system. Its results should not be used to diagnose cancer, estimate an individual's prognosis, select treatment, or replace professional medical judgement.

## Planned Improvements

The next stages of development should focus on scientific reliability before adding complexity.

- [ ] Resolve preprocessing and validation leakage.
- [ ] Verify the exact event coding and censoring conventions.
- [ ] Review all predictors for target leakage and post-outcome information.
- [ ] Fit imputers, encoders, and feature selectors within each training fold.
- [ ] Define a consistent and documented evaluation protocol.
- [ ] Add checks for proportional hazards and other model assumptions.
- [ ] Report uncertainty and confidence intervals where appropriate.
- [ ] Compare models on comparable evaluation data.
- [ ] Record the provenance and version of the dataset.
- [ ] Pin dependencies and document the tested environment.
- [ ] Expand tests for edge cases and leakage prevention.
- [ ] Improve the report documentation so each figure and metric is explained.
- [ ] Consider external validation on a compatible, independently sourced dataset where permitted.

## Ethical Considerations

Cancer-related data requires careful interpretation and responsible communication.

OncoTrace is intended for computational research and education. The presence of a machine learning model does not imply that its predictions are sufficiently reliable for clinical use.

Any future evaluation should consider dataset representativeness, potential biases, missingness, uncertainty, data-use permissions, and the consequences of incorrect predictions. Results should be communicated with enough context that exploratory associations are not mistaken for medical conclusions.

## License

The repository's software license should be chosen and added explicitly before public release. The license governing the code may differ from the terms governing the METABRIC dataset.

A repository license does not automatically grant permission to redistribute the dataset or its derived contents. Check the source's terms before publishing raw data or outputs that may be restricted.

## Acknowledgements

This project builds on publicly documented work in cancer research, survival analysis, statistical computing, and machine learning.

The METABRIC dataset is the data foundation for the current experiment. Please cite its original publication and dataset source according to their recommended citation instructions once the exact source used for this copy has been verified.

---

**OncoTrace — validating the data, studying survival patterns, and making computational cancer research more reproducible.**
