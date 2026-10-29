import subprocess
import sys


def run_step(step_name, command):
    print("")
    print(f"--- Running: {step_name} ---")
    result = subprocess.run(command)
    if result.returncode != 0:
        print("")
        print(f"[ERROR] {step_name} failed. Halting pipeline.")
        sys.exit(result.returncode)
    print(f"[SUCCESS] {step_name} complete.")


if __name__ == "__main__":
    print("Starting OncoTrace End-to-End Pipeline...")
    print("")

    run_step(
        "Rust Validation Engine",
        [
            "cargo",
            "run",
            "--quiet",
            "--manifest-path",
            "rust/Cargo.toml",
            "--",
            "data/raw/METABRIC_RNA_Mutation.csv",
        ],
    )
    run_step("Data Preprocessing", ["python", "src/oncotrace/preprocess.py"])
    run_step(
        "Baseline Survival Analysis",
        ["python", "src/oncotrace/baseline_survival.py"],
    )
    run_step(
        "Cox Proportional Hazards Model",
        ["python", "src/oncotrace/cox_model.py"],
    )
    run_step(
        "Random Survival Forest",
        ["python", "src/oncotrace/ml_survival.py"],
    )
    run_step(
        "Advanced Visual Analytics Suite",
        ["python", "src/oncotrace/advanced_visualizations.py"],
    )
    run_step("Automated Test Suite", ["pytest", "tests/"])

    print("")
    print(
        "All pipeline stages executed successfully! Check results/ for updated"
        " figures and reports."
    )