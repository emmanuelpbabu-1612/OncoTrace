# OncoTrace Cox Proportional Hazards Model Report

## Model Performance
- **5-Fold Cross-Validated C-Index:** 0.6546 (+/- 0.0341)
- **Sample Size:** 1904
- **Event Count:** 1103

## Parameter Estimates & Hazard Ratios

| Covariate | exp(coef) (HR) | exp(coef) lower 95% | exp(coef) upper 95% | p-value |
| --- | --- | --- | --- | --- |
| `age_at_diagnosis` | 1.0382 | 1.0327 | 1.0437 | 9.8759e-44 |
| `tumor_size` | 1.0107 | 1.0075 | 1.0138 | 1.7339e-11 |
| `lymph_nodes_examined_positive` | 1.0585 | 1.0474 | 1.0697 | 3.6197e-26 |
| `er_status` | 0.7116 | 0.6104 | 0.8296 | 1.3882e-05 |
| `neoplasm_histologic_grade` | 1.1500 | 1.0399 | 1.2717 | 6.4660e-03 |

## Deliverables
- Forest Plot: `results/figures/cox_hazard_ratios.png`
