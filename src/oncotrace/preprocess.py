import subprocess
from pathlib import Path
import pandas as pd


def run_rust_validator(
    csv_path: Path, manifest_path: Path = Path("rust/Cargo.toml")
) -> bool:
    """Executes the Rust validator binary against the raw CSV file."""
    cmd = [
        "cargo",
        "run",
        "--quiet",
        "--manifest-path",
        str(manifest_path),
        "--",
        str(csv_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise ValueError(f"Rust Data Validation Failed:\n{result.stderr}")
    return True


def preprocess_metabric(raw_path: Path, output_path: Path, rust_manifest: Path = Path("rust/Cargo.toml")) -> pd.DataFrame:
    """Sanitize METABRIC data and construct survival targets."""
    run_rust_validator(raw_path, rust_manifest)
    df = pd.read_csv(raw_path, low_memory=False)
    df["event"] = (df["overall_survival"] == 0).astype(int)
    df["duration_original"] = pd.to_numeric(df["overall_survival_months"], errors="raise")
    df["duration"] = df["duration_original"].clip(lower=0.1)
    mixed_mut_cols = ["rasgef1b_mut", "hras_mut", "smarcb1_mut", "siah1_mut"]
    for col in mixed_mut_cols:
        if col in df.columns:
            df[col] = df[col].astype(str)
    leakage_cols = ["overall_survival", "death_from_cancer"]
    df = df.drop(columns=[c for c in leakage_cols if c in df.columns])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return df
