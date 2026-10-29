from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from lifelines import CoxPHFitter
from lifelines.utils import k_fold_cross_validation


def train_cox_model(
    data_path: Path = Path("data/processed/metabric_cleaned.csv"),
    fig_dir: Path = Path("results/figures"),
    report_dir: Path = Path("results/reports"),
) -> dict:
    df = pd.read_csv(data_path, low_memory=False)

    # Core baseline clinical predictors
    clinical_candidates = {
        "age_at_diagnosis": "num",
        "tumor_size": "num",
        "lymph_nodes_examined_positive": "num",
        "er_status": "cat",
        "neoplasm_histologic_grade": "num",
    }

    selected_cols = [col for col in clinical_candidates if col in df.columns]
    model_df = df[selected_cols + ["duration", "event"]].copy()

    # Preprocessing: Impute numeric features, encode categoricals
    for col in selected_cols:
        if clinical_candidates[col] == "num":
            model_df[col] = pd.to_numeric(model_df[col], errors="coerce")
            model_df[col] = model_df[col].fillna(model_df[col].median())
        elif clinical_candidates[col] == "cat":
            model_df[col] = model_df[col].astype(str)
            model_df[col] = model_df[col].replace({"Positive": "Pos", "Negative": "Neg"})
            valid_mask = model_df[col].isin(["Pos", "Neg"])
            model_df.loc[~valid_mask, col] = "Pos"
            model_df[col] = (model_df[col] == "Pos").astype(int)

    # Evaluate model via 5-Fold Cross Validation
    cph = CoxPHFitter(penalizer=0.01)
    cv_scores = k_fold_cross_validation(
        cph,
        model_df,
        duration_col="duration",
        event_col="event",
        k=5,
        scoring_method="concordance_index",
    )
    mean_c_index = float(np.mean(cv_scores))
    std_c_index = float(np.std(cv_scores))

    # Fit final model on full cohort
    cph.fit(model_df, duration_col="duration", event_col="event")

    # Generate Forest Plot
    fig_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(9, 6))
    cph.plot()
    plt.title(
        "Cox Proportional Hazards Model — Hazard Ratios (Clinical Features)",
        fontsize=13,
        fontweight="bold",
    )
    plt.grid(True, linestyle="--", alpha=0.5)

    forest_path = fig_dir / "cox_hazard_ratios.png"
    plt.savefig(forest_path, dpi=300, bbox_inches="tight")
    plt.close()

    # Generate Markdown Report
    summary_df = cph.summary
    report_path = report_dir / "cox_model_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# OncoTrace Cox Proportional Hazards Model Report\n\n")
        f.write("## Model Performance\n")
        f.write(f"- **5-Fold Cross-Validated C-Index:** {mean_c_index:.4f} (+/- {std_c_index:.4f})\n")
        f.write(f"- **Sample Size:** {len(model_df)}\n")
        f.write(f"- **Event Count:** {model_df['event'].sum()}\n\n")

        f.write("## Parameter Estimates & Hazard Ratios\n\n")
        f.write("| Covariate | exp(coef) (HR) | exp(coef) lower 95% | exp(coef) upper 95% | p-value |\n")
        f.write("| --- | --- | --- | --- | --- |\n")
        for idx, row in summary_df.iterrows():
            f.write(
                f"| `{idx}` | {row['exp(coef)']:.4f} | {row['exp(coef) lower 95%']:.4f} | "
                f"{row['exp(coef) upper 95%']:.4f} | {row['p']:.4e} |\n"
            )

        f.write("\n## Deliverables\n")
        f.write(f"- Forest Plot: `{forest_path}`\n")

    return {
        "mean_c_index": mean_c_index,
        "std_c_index": std_c_index,
        "summary": summary_df,
    }


if __name__ == "__main__":
    res = train_cox_model()
    print("Cox Proportional Hazards Model Trained:")
    print(f"  - 5-Fold Cross-Validated C-Index: {res['mean_c_index']:.4f} +/- {res['std_c_index']:.4f}")