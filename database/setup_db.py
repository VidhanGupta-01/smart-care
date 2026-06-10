import sqlite3
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from analytics import (
    condition_frequency,
    feature_importance_df,
    load_dataset,
    symptom_frequency,
    symptom_risk_crosstab,
)
from features import DATASET_PATH, prepare_features

DB_PATH = Path(__file__).resolve().parent / "smart_care.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"
EXPORTS_DIR = Path(__file__).resolve().parent.parent / "exports"
MODEL_COMPARISON_PATH = Path(__file__).resolve().parent.parent / "model_comparison_results.csv"


def setup_database(db_path=DB_PATH):
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))

    df = load_dataset()
    patients = df.rename(
        columns={
            "Pre_Existing_Conditions": "pre_existing_conditions",
            "Heart_Rate": "heart_rate",
            "Systolic_BP": "systolic_bp",
            "Temperature": "temperature",
            "Risk_Level": "risk_level",
            "Age": "age",
            "Gender": "gender",
            "Symptoms": "symptoms",
        }
    )
    patients.to_sql("patients", conn, if_exists="append", index=False, index_label="patient_id")

    features = prepare_features(df)
    features["risk_level"] = df["Risk_Level"].values
    features = features.rename(
        columns={
            "Gender": "gender_encoded",
            "Age": "age",
            "Heart_Rate": "heart_rate",
            "Systolic_BP": "systolic_bp",
            "Temperature": "temperature",
            "Has_Chest_Pain": "has_chest_pain",
            "Has_Fever": "has_fever",
            "Has_Heart_Disease": "has_heart_disease",
        }
    )
    features.insert(0, "patient_id", range(1, len(features) + 1))
    features.to_sql("patient_features", conn, if_exists="append", index=False)

    if MODEL_COMPARISON_PATH.exists():
        benchmark = pd.read_csv(MODEL_COMPARISON_PATH).rename(
            columns={
                "model": "model_name",
                "cv_accuracy": "cv_accuracy",
                "cv_std": "cv_std",
                "test_accuracy": "test_accuracy",
            }
        )
        benchmark.to_sql("model_benchmark", conn, if_exists="append", index=False)

    conn.commit()
    conn.close()
    return db_path


def export_bi_files(exports_dir=EXPORTS_DIR):
    exports_dir = Path(exports_dir)
    exports_dir.mkdir(parents=True, exist_ok=True)

    df = load_dataset()

    df.to_csv(exports_dir / "patients.csv", index=False)

    risk_dist = (
        df["Risk_Level"]
        .value_counts()
        .reindex(["Low", "Medium", "High"])
        .reset_index()
    )
    risk_dist.columns = ["Risk_Level", "Patient_Count"]
    risk_dist["Percentage"] = (risk_dist["Patient_Count"] / len(df) * 100).round(1)
    risk_dist.to_csv(exports_dir / "risk_distribution.csv", index=False)

    vitals = (
        df.groupby("Risk_Level")[["Age", "Heart_Rate", "Systolic_BP", "Temperature"]]
        .mean()
        .round(2)
        .reset_index()
    )
    vitals.to_csv(exports_dir / "vitals_by_risk.csv", index=False)

    symptom_frequency(df).reset_index(name="Count").rename(
        columns={"index": "Symptom"}
    ).to_csv(exports_dir / "symptom_frequency.csv", index=False)

    condition_frequency(df).reset_index(name="Count").rename(
        columns={"index": "Condition"}
    ).to_csv(exports_dir / "condition_frequency.csv", index=False)

    symptom_risk = symptom_risk_crosstab(df).reset_index()
    symptom_risk.to_csv(exports_dir / "symptom_risk_matrix.csv", index=False)

    importance = feature_importance_df(df)
    importance.to_csv(exports_dir / "feature_importance.csv", index=False)

    if MODEL_COMPARISON_PATH.exists():
        pd.read_csv(MODEL_COMPARISON_PATH).to_csv(
            exports_dir / "model_comparison.csv", index=False
        )

    excel_path = exports_dir / "smart_care_analytics.xlsx"
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Patients", index=False)
        risk_dist.to_excel(writer, sheet_name="Risk_Distribution", index=False)
        vitals.to_excel(writer, sheet_name="Vitals_by_Risk", index=False)
        symptom_frequency(df).reset_index(name="Count").to_excel(
            writer, sheet_name="Symptoms", index=False
        )
        condition_frequency(df).reset_index(name="Count").to_excel(
            writer, sheet_name="Conditions", index=False
        )
        importance.to_excel(writer, sheet_name="Feature_Importance", index=False)
        if MODEL_COMPARISON_PATH.exists():
            pd.read_csv(MODEL_COMPARISON_PATH).to_excel(
                writer, sheet_name="Model_Comparison", index=False
            )

    return exports_dir, excel_path


def main():
    db_path = setup_database()
    exports_dir, excel_path = export_bi_files()
    print(f"SQLite database created: {db_path}")
    print(f"BI export folder: {exports_dir}")
    print(f"Excel workbook: {excel_path}")
    print(f"Source dataset: {DATASET_PATH}")


if __name__ == "__main__":
    main()
