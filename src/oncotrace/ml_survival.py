from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance
from sklearn.model_selection import train_test_split
from sksurv.ensemble import RandomSurvivalForest
import pandas as pd
pd.set_option('future.no_silent_downcasting', True)  # Add this line


def train_rsf_model(
    data_path: Path = Path("data/processed/metabric_cleaned.csv"),
    fig_dir: Path = Path("results/figures"),
    report_dir: Path = Path("results/reports"),
) -> dict:
    df = pd.read_csv(data_path, low_memory=False)

    # 1. Feature Selection: Clinical + Molecular (Mutations)
    clinical_cols = [
        "age_at_diagnosis", "tumor_size", "lymph_nodes_examined_positive", 
        "er_status", "neoplasm_histologic_grade"
    ]
    mut_cols = [c for c in df.columns if c.endswith("_mut")]
    
    selected_cols = [c for c in clinical_cols + mut_cols if c in df.columns]
    
    # SPEED OPTIMIZATION 1: Extract only necessary columns at ingestion using .loc
    X = df.loc[:, selected_cols].copy()

    # 2. Preprocessing
    if "er_status" in X.columns:
        X["er_status"] = X["er_status"].replace(
            {"Positive": 1, "Negative": 0, "Pos": 1, "Neg": 0}
        )
        X["er_status"] = X["er_status"].infer_objects(copy=False)
        X["er_status"] = pd.to_numeric(X["er_status"], errors="coerce")
    # Binarize mutation strings efficiently
    for col in mut_cols:
        if col in X.columns:
            X[col] = X[col].astype(str)
            X[col] = (~X[col].isin(["0", "nan", "NaN"])).astype(int)

    X = X.fillna(X.median())

    # 3. Construct scikit-survival target array
    y = np.array(
        [(bool(e), d) for e, d in zip(df["event"], df["duration"])],
        dtype=[("event", "?"), ("duration", "<f8")]
    )

    # 4. Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # 5. Train Random Survival Forest
    # SPEED OPTIMIZATION 2: Algorithmic limits 
    # - n_estimators reduced from 100 to 50
    # - max_depth set to 10 to prevent infinite tree growth
    # - max_features="sqrt" for faster node splitting
    rsf = RandomSurvivalForest(
        n_estimators=50, 
        max_depth=10,
        max_features="sqrt",
        min_samples_split=10, 
        min_samples_leaf=5, 
        n_jobs=1, 
        random_state=42
    )
    rsf.fit(X_train, y_train)

    train_c_index = rsf.score(X_train, y_train)
    test_c_index = rsf.score(X_test, y_test)

    # 6. Compute Permutation Feature Importance
    # SPEED OPTIMIZATION 3: Reduced n_repeats from 5 to 3
    result = permutation_importance(
        rsf, X_test, y_test, n_repeats=3, random_state=42, n_jobs=1
    )
    importances = pd.DataFrame(
        {
            "Feature": X.columns,
            "Importance": result.importances_mean,
            "Std": result.importances_std,
        }
    ).sort_values(by="Importance", ascending=False)

    top_features = importances.head(15)

    # 7. Generate Deliverables
    fig_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(10, 6))
    plt.barh(top_features["Feature"][::-1], top_features["Importance"][::-1], xerr=top_features["Std"][::-1], color="#2ca02c")
    plt.title("Random Survival Forest — Top 15 Feature Importances", fontsize=14, fontweight="bold")
    plt.xlabel("Permutation Importance (Drop in C-Index)", fontsize=12)
    plt.grid(axis="x", linestyle="--", alpha=0.7)
    
    importance_path = fig_dir / "rsf_feature_importance.png"
    plt.savefig(importance_path, dpi=300, bbox_inches="tight")
    
    # SPEED OPTIMIZATION 4: Close pyplot instance instantly to free memory
    plt.close()

    report_path = report_dir / "rsf_model_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# OncoTrace Random Survival Forest Report\n\n")
        f.write("## Model Performance (80/20 Split)\n")
        f.write(f"- **Training C-Index:** {train_c_index:.4f}\n")
        f.write(f"- **Testing C-Index:** {test_c_index:.4f}\n")
        f.write(f"- **Total Features Used:** {X.shape[1]}\n\n")
        
        f.write("## Top 10 Predictive Features\n\n")
        f.write("| Feature | Mean Importance | Std Dev |\n")
        f.write("| --- | --- | --- |\n")
        for _, row in importances.head(10).iterrows():
            f.write(f"| `{row['Feature']}` | {row['Importance']:.5f} | {row['Std']:.5f} |\n")
            
        f.write("\n## Deliverables\n")
        f.write(f"- Feature Importance Plot: `{importance_path}`\n")

    return {
        "train_c_index": float(train_c_index),
        "test_c_index": float(test_c_index),
        "feature_count": X.shape[1]
    }


if __name__ == "__main__":
    res = train_rsf_model()
    print("Random Survival Forest Trained:")
    print(f"  - Features processed: {res['feature_count']}")
    print(f"  - Testing C-Index: {res['test_c_index']:.4f}")