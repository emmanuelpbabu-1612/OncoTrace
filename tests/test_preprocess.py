import sys
from pathlib import Path
import pandas as pd
import pytest

# Ensure src/ is on Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from oncotrace.preprocess import preprocess_metabric


def test_preprocessing_target_and_leakage(tmp_path):
    raw_path = Path("data/raw/METABRIC_RNA_Mutation.csv")
    output_path = tmp_path / "metabric_test.csv"

    df_clean = preprocess_metabric(raw_path, output_path)

    # Verify leakage columns are removed
    assert "overall_survival" not in df_clean.columns
    assert "death_from_cancer" not in df_clean.columns

    # Verify survival target construction
    assert "event" in df_clean.columns
    assert "duration" in df_clean.columns

    # Verify event mapping (1103 deaths, 801 censored)
    event_counts = df_clean["event"].value_counts().to_dict()
    assert event_counts[1] == 1103
    assert event_counts[0] == 801

    # Original duration must remain unchanged.
    assert "duration_original" in df_clean.columns

    # The raw zero-month observation must be preserved.
    zero_time = df_clean["overall_survival_months"] == 0.0
    assert zero_time.sum() == 1
    assert df_clean.loc[zero_time, "duration_original"].iloc[0] == 0.0

    # Modeling duration must be positive.
    assert (df_clean["duration"] > 0.0).all()
    assert df_clean.loc[zero_time, "duration"].iloc[0] == pytest.approx(0.1)

def test_processed_output_file_exists(tmp_path):
    raw_path = Path("data/raw/METABRIC_RNA_Mutation.csv")
    output_path = tmp_path / "metabric_test.csv"

    preprocess_metabric(raw_path, output_path)
    assert output_path.exists()
