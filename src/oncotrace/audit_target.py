import pandas as pd
from pathlib import Path

def run_audit():
    path = Path("data/raw/METABRIC_RNA_Mutation.csv")
    
    # Load dataset, retaining mixed types for inspection
    df = pd.read_csv(path, low_memory=False)
    
    # Ensure report directory exists
    report_path = Path("results/reports/data_audit.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# OncoTrace Data & Target Audit Report\n\n")
        f.write(f"- **Total Records:** {df.shape[0]}\n")
        f.write(f"- **Total Columns:** {df.shape[1]}\n\n")
        
        f.write("## 1. Value Counts: overall_survival\n```text\n")
        f.write(df['overall_survival'].value_counts(dropna=False).to_string())
        f.write("\n```\n\n")
        
        f.write("## 2. Value Counts: death_from_cancer\n```text\n")
        f.write(df['death_from_cancer'].value_counts(dropna=False).to_string())
        f.write("\n```\n\n")
        
        f.write("## 3. Target Cross-Tabulation\n")
        f.write("Mapping `overall_survival` against `death_from_cancer` to deduce event encoding.\n```text\n")
        f.write(pd.crosstab(df['overall_survival'], df['death_from_cancer'], dropna=False).to_string())
        f.write("\n```\n\n")
        
        f.write("## 4. Mixed-Type Column Inspection\n")
        f.write("Investigating column indices 678, 688, 690, 692 for potential leakage or schema issues.\n")
        mixed_indices = [678, 688, 690, 692]
        for idx in mixed_indices:
            if idx < len(df.columns):
                col = df.columns[idx]
                f.write(f"- **`{col}`** (Index {idx}):\n")
                f.write(f"  - Dtype: `{df[col].dtype}`\n")
                f.write(f"  - Missing: {df[col].isna().sum()}\n")
                f.write(f"  - Sample unique values: `{list(df[col].dropna().unique()[:5])}`\n")
        
        f.write("\n## 5. Patient IDs & Survival Time Anomalies\n")
        f.write(f"- Missing `patient_id`: {df['patient_id'].isna().sum()}\n")
        f.write(f"- Duplicate `patient_id`: {df.duplicated(subset=['patient_id']).sum()}\n")
        f.write(f"- Duplicate full rows: {df.duplicated().sum()}\n")
        f.write(f"- Negative survival months: {(df['overall_survival_months'] < 0).sum()}\n")
        f.write(f"- Zero survival months: {(df['overall_survival_months'] == 0).sum()}\n")
        
    print(f"Audit complete. Results saved to {report_path}")

if __name__ == "__main__":
    run_audit()