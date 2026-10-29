
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {
    "patient_id",
    "overall_survival",
    "overall_survival_months",
}


def load_metabric(path: str | Path) -> pd.DataFrame:
    """Load METABRIC and validate its basic survival fields."""
    path = Path(path)

    if not path.is_file():
        raise FileNotFoundError(f"METABRIC file not found: {path}")

    df = pd.read_csv(path, low_memory=False)

    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    if df["patient_id"].isna().any():
        raise ValueError("Missing patient IDs detected.")

    if df["patient_id"].duplicated().any():
        raise ValueError("Duplicate patient IDs detected.")

    if df["overall_survival"].isna().any():
        raise ValueError("Missing overall-survival labels detected.")

    if not df["overall_survival"].isin([0, 1]).all():
        raise ValueError("Survival labels must be encoded as 0 or 1.")

    time = pd.to_numeric(
        df["overall_survival_months"], errors="coerce"
    )

    if time.isna().any():
        raise ValueError("Missing or invalid survival times detected.")

    if (time < 0).any():
        raise ValueError("Negative survival times detected.")

    df["overall_survival_months"] = time

    return df


def make_survival_endpoint(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Create time and event fields for overall-survival analysis.

    event=1: death observed
    event=0: right-censored (alive at last follow-up)
    """
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    if not df["overall_survival"].isin([0, 1]).all():
        raise ValueError("Survival labels must be encoded as 0 or 1.")

    time = pd.to_numeric(
        df["overall_survival_months"], errors="coerce"
    )

    if time.isna().any() or (time < 0).any():
        raise ValueError("Survival times must be valid and non-negative.")

    endpoint = pd.DataFrame(index=df.index)
    endpoint["time_months"] = time
    endpoint["event"] = (1 - df["overall_survival"]).astype("int8")

    return endpoint
