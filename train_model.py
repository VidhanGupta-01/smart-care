import argparse

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import cross_val_score, train_test_split

from features import DATASET_PATH, MODEL_PATH, prepare_features
from models_registry import RANDOM_STATE, get_models


def train(model_name="decision_tree"):
    models = get_models()
    if model_name not in models:
        available = ", ".join(sorted(models))
        raise ValueError(f"Unknown model '{model_name}'. Choose from: {available}")

    df = pd.read_csv(DATASET_PATH)
    X = prepare_features(df)
    y = df["Risk_Level"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE
    )

    model = models[model_name]

    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring="accuracy")
    print(f"Training model: {model_name}")
    print("Cross-validation scores:", cv_scores)
    print("Mean CV accuracy:", cv_scores.mean())

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    print("Test accuracy:", accuracy_score(y_test, y_pred))
    print("\nClassification Report:\n")
    print(classification_report(y_test, y_pred))

    joblib.dump(model, MODEL_PATH)
    print(f"\nModel saved as {MODEL_PATH}")


def main():
    parser = argparse.ArgumentParser(
        description="Train a risk classifier and save it for the Smart Care app."
    )
    parser.add_argument(
        "--model",
        default="decision_tree",
        choices=sorted(get_models()),
        help="Classifier to train (default: decision_tree)",
    )
    parser.add_argument(
        "--list", action="store_true", help="List available models and exit"
    )
    args = parser.parse_args()

    if args.list:
        for name in sorted(get_models()):
            print(name)
        return

    train(args.model)


if __name__ == "__main__":
    main()
