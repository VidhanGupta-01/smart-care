import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import cross_val_score, train_test_split

from features import DATASET_PATH, FEATURE_COLUMNS, MODEL_PATH, prepare_features
from models_registry import RANDOM_STATE, get_models

RISK_ORDER = ["Low", "Medium", "High"]


def load_dataset():
    return pd.read_csv(DATASET_PATH)


def _split_data(df):
    X = prepare_features(df)
    y = df["Risk_Level"]
    return train_test_split(X, y, test_size=0.2, random_state=RANDOM_STATE)


def dataset_overview(df):
    risk_counts = df["Risk_Level"].value_counts().reindex(RISK_ORDER, fill_value=0)
    return {
        "total_patients": len(df),
        "feature_count": len(df.columns),
        "avg_age": round(df["Age"].mean(), 1),
        "avg_heart_rate": round(df["Heart_Rate"].mean(), 1),
        "avg_systolic_bp": round(df["Systolic_BP"].mean(), 1),
        "avg_temperature": round(df["Temperature"].mean(), 1),
        "risk_counts": risk_counts.to_dict(),
        "gender_counts": df["Gender"].value_counts().to_dict(),
        "dominant_risk": risk_counts.idxmax(),
    }


def numeric_summary_by_risk(df):
    numeric_cols = ["Age", "Heart_Rate", "Systolic_BP", "Temperature"]
    summary = (
        df.groupby("Risk_Level")[numeric_cols]
        .agg(["mean", "median", "std"])
        .round(2)
    )
    summary = summary.reindex(RISK_ORDER)
    return summary


def parse_token_counts(series):
    counts = {}
    for value in series.fillna(""):
        for token in str(value).split(","):
            token = token.strip().lower()
            if token and token != "none":
                counts[token] = counts.get(token, 0) + 1
    return pd.Series(counts).sort_values(ascending=False)


def symptom_frequency(df):
    return parse_token_counts(df["Symptoms"])


def condition_frequency(df):
    return parse_token_counts(df["Pre_Existing_Conditions"])


def symptom_risk_crosstab(df):
    rows = []
    for _, row in df.iterrows():
        risk = row["Risk_Level"]
        for symptom in str(row["Symptoms"]).split(","):
            symptom = symptom.strip().lower()
            if symptom:
                rows.append({"Symptom": symptom, "Risk_Level": risk})
    if not rows:
        return pd.DataFrame()
    symptom_df = pd.DataFrame(rows)
    return pd.crosstab(symptom_df["Symptom"], symptom_df["Risk_Level"]).reindex(
        columns=RISK_ORDER, fill_value=0
    )


def correlation_matrix(df):
    encoded = prepare_features(df).copy()
    encoded["Risk_Score"] = df["Risk_Level"].map({"Low": 0, "Medium": 1, "High": 2})
    return encoded.corr().round(3)


def load_production_model():
    return joblib.load(MODEL_PATH)


def evaluate_production_model(df=None):
    df = load_dataset() if df is None else df
    model = load_production_model()
    X_train, X_test, y_train, y_test = _split_data(df)

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    report = classification_report(y_test, y_pred, output_dict=True)
    labels = [label for label in RISK_ORDER if label in set(y_test)]

    return {
        "model_name": type(model).__name__,
        "accuracy": accuracy_score(y_test, y_pred),
        "macro_f1": f1_score(y_test, y_pred, average="macro"),
        "weighted_f1": f1_score(y_test, y_pred, average="weighted"),
        "confusion_matrix": confusion_matrix(y_test, y_pred, labels=labels),
        "labels": labels,
        "classification_report": report,
    }


def feature_importance_df(df=None):
    df = load_dataset() if df is None else df
    model = load_production_model()
    X = prepare_features(df)
    y = df["Risk_Level"]
    model.fit(X, y)

    if not hasattr(model, "feature_importances_"):
        return pd.DataFrame(columns=["Feature", "Importance"])

    importance = pd.DataFrame(
        {"Feature": FEATURE_COLUMNS, "Importance": model.feature_importances_}
    ).sort_values("Importance", ascending=False)
    return importance


def compare_all_models(df=None):
    df = load_dataset() if df is None else df
    X_train, X_test, y_train, y_test = _split_data(df)
    rows = []

    for name, model in get_models().items():
        cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring="accuracy")
        model.fit(X_train, y_train)
        test_accuracy = accuracy_score(y_test, model.predict(X_test))
        rows.append(
            {
                "model": name,
                "cv_accuracy": round(cv_scores.mean(), 4),
                "cv_std": round(cv_scores.std(), 4),
                "test_accuracy": round(test_accuracy, 4),
            }
        )

    return pd.DataFrame(rows).sort_values("cv_accuracy", ascending=False)


def generate_insights(df=None):
    df = load_dataset() if df is None else df
    overview = dataset_overview(df)
    insights = []

    low, medium, high = (
        overview["risk_counts"].get("Low", 0),
        overview["risk_counts"].get("Medium", 0),
        overview["risk_counts"].get("High", 0),
    )
    total = overview["total_patients"]
    insights.append(
        f"{medium / total:.0%} of patients are classified as Medium risk — the largest triage bucket."
    )
    insights.append(
        f"High-risk patients make up {high / total:.0%} of the dataset, requiring urgent care routing."
    )

    high_risk = df[df["Risk_Level"] == "High"]
    low_risk = df[df["Risk_Level"] == "Low"]
    if len(high_risk) and len(low_risk):
        hr_gap = high_risk["Heart_Rate"].mean() - low_risk["Heart_Rate"].mean()
        bp_gap = high_risk["Systolic_BP"].mean() - low_risk["Systolic_BP"].mean()
        insights.append(
            f"High-risk patients average {hr_gap:.0f} bpm higher heart rate than low-risk patients."
        )
        insights.append(
            f"High-risk patients show {bp_gap:.0f} mmHg higher systolic BP on average."
        )

    top_symptom = symptom_frequency(df).head(1)
    if not top_symptom.empty:
        insights.append(
            f"'{top_symptom.index[0].title()}' is the most frequently reported symptom."
        )

    top_condition = condition_frequency(df).head(1)
    if not top_condition.empty:
        insights.append(
            f"'{top_condition.index[0].title()}' is the most common pre-existing condition."
        )

    importance = feature_importance_df(df)
    if not importance.empty:
        top_feature = importance.iloc[0]
        insights.append(
            f"'{top_feature['Feature']}' is the strongest predictor in the AdaBoost model."
        )

    return insights
