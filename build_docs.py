
from pathlib import Path
import json

root = Path(__file__).resolve().parent

readme_path = root / "README.md"

if not readme_path.exists():
    readme_path.write_text(
        "# OncoTrace\n\n"
        "A Python and Rust research-engineering project for "
        "breast cancer survival analysis using METABRIC.\n\n"
        "## Dataset\n\n"
        "Input: `data/raw/METABRIC_RNA_Mutation.csv`\n\n"
        "## Current goals\n\n"
        "1. Audit the clinical and molecular dataset.\n"
        "2. Verify survival-event coding and data quality.\n"
        "3. Build a reproducible survival-analysis pipeline.\n"
        "4. Evaluate models without data leakage.\n"
        "5. Document verified results and limitations.\n\n"
        "## Disclaimer\n\n"
        "Educational research only; not a clinical diagnostic "
        "or treatment tool.\n",
        encoding="utf-8",
    )
    print("Created README.md")
else:
    print("README.md already exists; unchanged")

notebook_path = root / "notebooks" / "01_oncotrace_analysis.ipynb"
notebook_path.parent.mkdir(parents=True, exist_ok=True)

if not notebook_path.exists():
    cells = [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# OncoTrace: METABRIC Data Audit\n",
                "\n",
                "Inspect the dataset before building survival models.\n",
            ],
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "from pathlib import Path\n",
                "import pandas as pd\n",
                '\ndata_path = Path("../data/raw/METABRIC_RNA_Mutation.csv")\n',
                "if not data_path.exists():\n",
                "    raise FileNotFoundError(data_path.resolve())\n",
                '\ndf = pd.read_csv(data_path, low_memory=False)\n',
                'print("Shape:", df.shape)\n',
                'print("\\nOverall survival coding:")\n',
                'print(df["overall_survival"].value_counts(dropna=False).sort_index())\n',
                'print("\\nDeath-from-cancer values:")\n',
                'print(df["death_from_cancer"].value_counts(dropna=False))\n',
                'print("\\nSurvival months:")\n',
                'print(df["overall_survival_months"].describe())\n',
            ],
        },
    ]

    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }

    notebook_path.write_text(
        json.dumps(notebook, indent=2),
        encoding="utf-8",
    )
    print("Created notebook:", notebook_path)
else:
    print("Notebook already exists; unchanged")
