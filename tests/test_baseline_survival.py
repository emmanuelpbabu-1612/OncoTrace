import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from oncotrace.baseline_survival import run_baseline_survival_analysis


def test_baseline_survival_execution():
    processed_csv = Path("data/processed/metabric_cleaned.csv")
    assert processed_csv.exists(), "Processed METABRIC dataset must exist"

    metrics = run_baseline_survival_analysis()

    assert metrics["median_survival"] > 0.0
    assert 0.0 <= metrics["surv_5yr"] <= 1.0
    assert 0.0 <= metrics["surv_10yr"] <= 1.0
    assert Path("results/figures/km_overall_survival.png").exists()
    assert Path("results/reports/baseline_survival_report.md").exists()
