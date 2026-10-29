# OncoTrace Random Survival Forest Report

## Model Performance (80/20 Split)
- **Training C-Index:** 0.7339
- **Testing C-Index:** 0.6816
- **Total Features Used:** 178

## Top 10 Predictive Features

| Feature | Mean Importance | Std Dev |
| --- | --- | --- |
| `age_at_diagnosis` | 0.05070 | 0.00840 |
| `lymph_nodes_examined_positive` | 0.04511 | 0.01015 |
| `tumor_size` | 0.03257 | 0.00706 |
| `tp53_mut` | 0.01708 | 0.00315 |
| `neoplasm_histologic_grade` | 0.00744 | 0.00005 |
| `cbfb_mut` | 0.00365 | 0.00086 |
| `er_status` | 0.00289 | 0.00062 |
| `ep300_mut` | 0.00175 | 0.00051 |
| `thsd7a_mut` | 0.00150 | 0.00061 |
| `gata3_mut` | 0.00149 | 0.00045 |

## Deliverables
- Feature Importance Plot: `results/figures/rsf_feature_importance.png`
