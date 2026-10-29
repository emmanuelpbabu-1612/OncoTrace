
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.oncotrace.data_audit import (
    load_metabric,
    make_survival_endpoint,
)


def test_survival_endpoint_coding():
    df = pd.DataFrame({
        "patient_id": [101, 102, 103],
        "overall_survival": [0, 1, 0],
        "overall_survival_months": [12.0, 24.0, 36.0],
    })

    endpoint = make_survival_endpoint(df)

    assert endpoint["event"].tolist() == [1, 0, 1]
    assert endpoint["time_months"].tolist() == [12.0, 24.0, 36.0]
    assert endpoint.isna().sum().sum() == 0


def test_invalid_survival_label_is_rejected():
    df = pd.DataFrame({
        "patient_id": [101],
        "overall_survival": [2],
        "overall_survival_months": [12.0],
    })

    with pytest.raises(ValueError, match="encoded as 0 or 1"):
        make_survival_endpoint(df)


def test_negative_survival_time_is_rejected():
    df = pd.DataFrame({
        "patient_id": [101],
        "overall_survival": [0],
        "overall_survival_months": [-5.0],
    })

    with pytest.raises(ValueError, match="non-negative"):
        make_survival_endpoint(df)


def test_missing_required_column_is_rejected():
    df = pd.DataFrame({
        "patient_id": [101],
        "overall_survival": [0],
    })

    with pytest.raises(ValueError, match="Missing required columns"):
        make_survival_endpoint(df)


def test_load_metabric_rejects_duplicate_patient_ids(tmp_path):
    path = tmp_path / "duplicate_patients.csv"

    pd.DataFrame({
        "patient_id": [101, 101],
        "overall_survival": [0, 1],
        "overall_survival_months": [12.0, 24.0],
    }).to_csv(path, index=False)

    with pytest.raises(ValueError, match="Duplicate patient IDs"):
        load_metabric(path)
