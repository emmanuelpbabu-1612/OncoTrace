import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from oncotrace.ml_survival import train_rsf_model


def test_rsf_model_execution():
    processed_csv = Path("data/processed/metabric_cleaned.csv")
    assert processed_csv.exists(), "Processed METABRIC dataset missing"

    results = train_rsf_model()

    # C-index must be bounded validly
    assert 0.5 <= results["train_c_index"] <= 1.0
    assert 0.0 <= results["test_c_index"] <= 1.0
    assert results["feature_count"] > 5  # Ensures mutations were included

    # Verify generated outputs exist
    assert Path("results/figures/rsf_feature_importance.png").exists()
    assert Path("results/reports/rsf_model_report.md").exists()
