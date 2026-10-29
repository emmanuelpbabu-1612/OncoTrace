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

1. Pre
