# OncoTrace Baseline Survival Analysis Report

## Cohort Summary
- **Total Patients:** 1904
- **Observed Events (Deaths):** 1103
- **Right-Censored Patients:** 801 (42.07%)

## Non-Parametric Survival Estimates
- **Median Survival Time:** 154.50 months
- **5-Year Overall Survival Probability ($t=60$ mo):** 0.7794 (77.94%)
- **10-Year Overall Survival Probability ($t=120$ mo):** 0.5886 (58.86%)

## Subgroup Comparison: ER Status
- **Column:** `er_status`
- **Log-Rank Statistic:** 5.2779
- **Log-Rank p-value:** 2.1597e-02

## Deliverables
- Cohort Kaplan-Meier Curve: `results/figures/km_overall_survival.png`
- ER Stratified Curve: `results/figures/km_by_er_status.png`
