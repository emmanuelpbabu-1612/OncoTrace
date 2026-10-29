import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from oncotrace.cox_model import train_cox_model


def test_cox_model_execution():
    results = train_cox_model()

    # C-index must be bounded (0.5 = random, 1.0 = perfect discrimination)
    assert 0.5 <= results["mean_c_index"] <= 1.0
    assert results["std_c_index"] >= 0.0

    # Verify generated outputs exist
    assert Path("results/figures/cox_hazard_ratios.png").exists()
    assert Path("results/reports/cox_model_report.md").exists()
