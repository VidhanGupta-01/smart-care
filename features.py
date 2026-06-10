import pandas as pd

FEATURE_COLUMNS = [
    "Age",
    "Gender",
    "Heart_Rate",
    "Systolic_BP",
    "Temperature",
    "Has_Chest_Pain",
    "Has_Fever",
    "Has_Heart_Disease",
]

DATASET_PATH = "synthetic_patients.csv"
MODEL_PATH = "risk_classifier.pkl"


def prepare_features(df):
    df = df.copy()
    df["Gender"] = df["Gender"].map({"Male": 0, "Female": 1})
    df["Has_Chest_Pain"] = df["Symptoms"].str.contains("chest pain").astype(int)
    df["Has_Fever"] = df["Symptoms"].str.contains("fever").astype(int)
    df["Has_Heart_Disease"] = df["Pre_Existing_Conditions"].str.contains(
        "heart disease"
    ).astype(int)
    return df[FEATURE_COLUMNS]
