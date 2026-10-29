from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from lifelines import KaplanMeierFitter, NelsonAalenFitter
from lifelines.statistics import logrank_test


def generate_advanced_visualizations(
    data_path: Path = Path("data/processed/metabric_cleaned.csv"),
    fig_dir: Path = Path("results/figures"),
) -> None:
    fig_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(data_path, low_memory=False)

    sns.set_theme(style="whitegrid", font="sans-serif")
    plt.rcParams.update({"font.size": 11, "axes.labelsize": 12, "axes.titlesize": 13})

    # FIGURE 1: 4-Panel Comprehensive Survival & Hazard Dashboard
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    kmf = KaplanMeierFitter()
    kmf.fit(df["duration"], event_observed=df["event"], label="METABRIC Cohort")
    kmf.plot_survival_function(ax=axes[0, 0], ci_show=True, color="#1f77b4", lw=2.5)
    
    med_time = kmf.median_survival_time_
    axes[0, 0].axvline(med_time, color="red", linestyle="--", alpha=0.7, label=f"Median OS ({med_time:.1f} mo)")
    axes[0, 0].axhline(0.5, color="red", linestyle="--", alpha=0.3)
    axes[0, 0].set_title("A. Cohort Overall Survival Curve (KM Estimator)", fontweight="bold")
    axes[0, 0].set_xlabel("Follow-up Time (Months)")
    axes[0, 0].set_ylabel("Survival Probability")
    axes[0, 0].set_ylim(0, 1.05)
    axes[0, 0].legend(loc="lower left")

    naf = NelsonAalenFitter()
    naf.fit(df["duration"], event_observed=df["event"], label="Cumulative Hazard")
    naf.plot_cumulative_hazard(ax=axes[0, 1], color="#d62728", lw=2.5)
    axes[0, 1].set_title("B. Cumulative Hazard Rate (Nelson-Aalen)", fontweight="bold")
    axes[0, 1].set_xlabel("Follow-up Time (Months)")
    axes[0, 1].set_ylabel(r"Cumulative Hazard $\Lambda(t)$")
    axes[0, 1].legend(loc="upper left")

    if "er_status" in df.columns:
        er_clean = df["er_status"].replace({"Positive": "Pos", "Negative": "Neg"})
        for group, color in zip(["Pos", "Neg"], ["#2ca02c", "#d62728"]):
            mask = er_clean == group
            if mask.sum() > 0:
                kmf_g = KaplanMeierFitter()
                kmf_g.fit(df.loc[mask, "duration"], event_observed=df.loc[mask, "event"], label=f"ER {group} (n={mask.sum()})")
                kmf_g.plot_survival_function(ax=axes[1, 0], ci_show=True, color=color, lw=2)
        
        g1 = df[er_clean == "Pos"]
        g2 = df[er_clean == "Neg"]
        lr = logrank_test(g1["duration"], g2["duration"], event_observed_A=g1["event"], event_observed_B=g2["event"])
        axes[1, 0].annotate(f"Log-Rank p = {lr.p_value:.2e}", xy=(0.05, 0.15), xycoords="axes fraction", bbox=dict(boxstyle="round", fc="white", ec="gray", alpha=0.8))
        axes[1, 0].set_title("C. Survival Stratified by ER Status", fontweight="bold")
        axes[1, 0].set_xlabel("Follow-up Time (Months)")
        axes[1, 0].set_ylabel("Survival Probability")
        axes[1, 0].set_ylim(0, 1.05)

    if "neoplasm_histologic_grade" in df.columns:
        grades = sorted(df["neoplasm_histologic_grade"].dropna().unique())
        palette = sns.color_palette("Blues_r", len(grades))
        for grade, color in zip(grades, palette):
            mask = df["neoplasm_histologic_grade"] == grade
            kmf_g = KaplanMeierFitter()
            kmf_g.fit(df.loc[mask, "duration"], event_observed=df.loc[mask, "event"], label=f"Grade {int(grade)} (n={mask.sum()})")
            kmf_g.plot_survival_function(ax=axes[1, 1], ci_show=False, color=color, lw=2.2)
        
        axes[1, 1].set_title("D. Survival Stratified by Histologic Grade", fontweight="bold")
        axes[1, 1].set_xlabel("Follow-up Time (Months)")
        axes[1, 1].set_ylabel("Survival Probability")
        axes[1, 1].set_ylim(0, 1.05)

    plt.tight_layout()
    fig1_path = fig_dir / "composite_survival_dashboard.png"
    plt.savefig(fig1_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Generated 4-Panel Dashboard: {fig1_path}")

    # FIGURE 2: Clinical & Molecular Feature Correlation Heatmap
    num_cols = ["age_at_diagnosis", "tumor_size", "lymph_nodes_examined_positive", "duration", "event"]
    mut_cols = [c for c in df.columns if c.endswith("_mut")][:10]
    
    corr_df = df[num_cols + mut_cols].copy()
    for col in mut_cols:
        corr_df[col] = (~corr_df[col].astype(str).isin(["0", "nan", "NaN"])).astype(int)

    plt.figure(figsize=(12, 10))
    corr_matrix = corr_df.corr(method="spearman")
    
    sns.heatmap(
        corr_matrix, 
        cmap="coolwarm", 
        vmax=0.5, 
        vmin=-0.5, 
        annot=True, 
        fmt=".2f", 
        linewidths=0.5, 
        cbar_kws={"shrink": 0.8, "label": "Spearman Correlation"}
    )
    plt.title("Clinical Covariates & Top Mutation Correlation Matrix", fontsize=14, fontweight="bold", pad=15)
    plt.xticks(rotation=45, ha="right")
    
    fig2_path = fig_dir / "clinical_molecular_correlation_matrix.png"
    plt.savefig(fig2_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Generated Correlation Matrix: {fig2_path}")

    # FIGURE 3: Risk Stratification & Outcome Distribution Breakdown
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    sns.scatterplot(
        data=df, 
        x="age_at_diagnosis", 
        y="tumor_size", 
        hue="event", 
        palette={0: "#1f77b4", 1: "#d62728"}, 
        alpha=0.6, 
        s=40, 
        ax=ax1
    )
    ax1.set_title("Age at Diagnosis vs. Tumor Size (Event Distribution)", fontweight="bold")
    ax1.set_xlabel("Age at Diagnosis (Years)")
    ax1.set_ylabel("Tumor Size (mm)")
    
    handles, _ = ax1.get_legend_handles_labels()
    ax1.legend(handles=handles, labels=["Censored (Survived)", "Event (Deceased)"], loc="upper left")

    if "er_status" in df.columns:
        df_er = df.copy()
        df_er["er_status"] = df_er["er_status"].replace({"Positive": "Pos", "Negative": "Neg"})
        sns.boxplot(
            data=df_er, 
            x="er_status", 
            y="lymph_nodes_examined_positive", 
            hue="event", 
            palette={0: "#1f77b4", 1: "#d62728"}, 
            ax=ax2
        )
        ax2.set_title("Positive Lymph Nodes Distribution by ER Status & Outcome", fontweight="bold")
        ax2.set_xlabel("ER Status")
        ax2.set_ylabel("Positive Lymph Nodes Examined")
        ax2.set_ylim(-1, 25)
        
        handles, _ = ax2.get_legend_handles_labels()
        ax2.legend(handles=handles, labels=["Censored", "Deceased"], loc="upper right")

    plt.tight_layout()
    fig3_path = fig_dir / "risk_stratification_breakdown.png"
    plt.savefig(fig3_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Generated Risk Stratification Breakdown: {fig3_path}")


if __name__ == "__main__":
    generate_advanced_visualizations()
