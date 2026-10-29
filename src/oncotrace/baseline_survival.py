from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test


def run_baseline_survival_analysis(
    data_path: Path = Path("data/processed/metabric_cleaned.csv"),
    fig_dir: Path = Path("results/figures"),
    report_dir: Path = Path("results/reports"),
) -> dict:
    """Computes overall and stratified Kaplan-Meier baseline survival statistics,

    generates figures, and writes a Markdown report.
    """
    df = pd.read_csv(data_path, low_memory=False)

    durations = df["duration"]
    events = df["event"]

    fig_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    # 1. Fit overall cohort Kaplan-Meier estimator
    kmf = KaplanMeierFitter()
    kmf.fit(
        durations, event_observed=events, label=f"Overall Cohort (N={len(df)})"
    )

    median_survival = float(kmf.median_survival_time_)
    surv_5yr = float(kmf.predict(60.0))
    surv_10yr = float(kmf.predict(120.0))

    # Plot 1: Overall Kaplan-Meier Curve
    plt.figure(figsize=(9, 6))
    ax = kmf.plot_survival_function(ci_show=True, color="#1f77b4", lw=2)
    plt.title(
        "METABRIC Overall Survival (Kaplan-Meier Estimator)",
        fontsize=14,
        fontweight="bold",
    )
    plt.xlabel("Follow-up Time (Months)", fontsize=12)
    plt.ylabel("Overall Survival Probability", fontsize=12)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.ylim(0, 1.05)

    km_fig_path = fig_dir / "km_overall_survival.png"
    plt.savefig(km_fig_path, dpi=300, bbox_inches="tight")
    plt.close()

    # 2. Stratified analysis by ER Status
    er_col = None
    for candidate in [
        "er_status",
        "er_status_measured_by_ihc",
        "ER_status",
        "er_status_ihc",
    ]:
        if candidate in df.columns:
            er_col = candidate
            break

    logrank_res = None
    er_fig_path = None

    if er_col:
        plt.figure(figsize=(9, 6))
        ax = plt.gca()

        # Clean ER status values
        valid_mask = df[er_col].isin(["Pos", "Neg", "Positive", "Negative"])
        if valid_mask.sum() > 0:
            er_df = df[valid_mask].copy()
            er_df[er_col] = er_df[er_col].replace(
                {"Positive": "Pos", "Negative": "Neg"}
            )

            groups = er_df[er_col].unique()
            for group in groups:
                idx = er_df[er_col] == group
                kmf_g = KaplanMeierFitter()
                kmf_g.fit(
                    er_df.loc[idx, "duration"],
                    event_observed=er_df.loc[idx, "event"],
                    label=f"ER {group} (n={idx.sum()})",
                )
                kmf_g.plot_survival_function(ax=ax, ci_show=True, lw=2)

            if len(groups) == 2:
                g1 = er_df[er_df[er_col] == groups[0]]
                g2 = er_df[er_df[er_col] == groups[1]]
                logrank_res = logrank_test(
                    g1["duration"],
                    g2["duration"],
                    event_observed_A=g1["event"],
                    event_observed_B=g2["event"],
                )

            p_val_str = (
                f" (Log-Rank p = {logrank_res.p_value:.2e})"
                if logrank_res
                else ""
            )
            plt.title(
                f"Overall Survival Stratified by ER Status{p_val_str}",
                fontsize=14,
                fontweight="bold",
            )
            plt.xlabel("Follow-up Time (Months)", fontsize=12)
            plt.ylabel("Overall Survival Probability", fontsize=12)
            plt.grid(True, linestyle="--", alpha=0.5)
            plt.ylim(0, 1.05)

            er_fig_path = fig_dir / "km_by_er_status.png"
            plt.savefig(er_fig_path, dpi=300, bbox_inches="tight")
            plt.close()

    # 3. Export Baseline Report
    report_path = report_dir / "baseline_survival_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# OncoTrace Baseline Survival Analysis Report\n\n")
        f.write("## Cohort Summary\n")
        f.write(f"- **Total Patients:** {len(df)}\n")
        f.write(f"- **Observed Events (Deaths):** {events.sum()}\n")
        f.write(
            f"- **Right-Censored Patients:** {len(df) - events.sum()} "
            f"({(len(df) - events.sum()) / len(df) * 100:.2f}%)\n\n"
        )

        f.write("## Non-Parametric Survival Estimates\n")
        f.write(f"- **Median Survival Time:** {median_survival:.2f} months\n")
        f.write(
            f"- **5-Year Overall Survival Probability ($t=60$ mo):** "
            f"{surv_5yr:.4f} ({surv_5yr * 100:.2f}%)\n"
        )
        f.write(
            f"- **10-Year Overall Survival Probability ($t=120$ mo):** "
            f"{surv_10yr:.4f} ({surv_10yr * 100:.2f}%)\n\n"
        )

        if er_col and logrank_res:
            f.write("## Subgroup Comparison: ER Status\n")
            f.write(f"- **Column:** `{er_col}`\n")
            f.write(
                f"- **Log-Rank Statistic:** {logrank_res.test_statistic:.4f}\n"
            )
            f.write(f"- **Log-Rank p-value:** {logrank_res.p_value:.4e}\n\n")

        f.write("## Deliverables\n")
        f.write(f"- Cohort Kaplan-Meier Curve: `{km_fig_path}`\n")
        if er_fig_path:
            f.write(f"- ER Stratified Curve: `{er_fig_path}`\n")

    return {
        "median_survival": median_survival,
        "surv_5yr": surv_5yr,
        "surv_10yr": surv_10yr,
        "logrank_p_value": logrank_res.p_value if logrank_res else None,
    }


if __name__ == "__main__":
    res = run_baseline_survival_analysis()
    print("Baseline Survival Analysis Complete:")
    print(f"  - Median Survival: {res['median_survival']:.2f} months")
    print(f"  - 5-Year Survival Probability: {res['surv_5yr']*100:.2f}%")
    print(f"  - 10-Year Survival Probability: {res['surv_10yr']*100:.2f}%")
    if res["logrank_p_value"] is not None:
        print(f"  - ER Log-Rank Test p-value: {res['logrank_p_value']:.4e}")