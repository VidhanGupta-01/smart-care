import argparse

import pandas as pd
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import cross_val_score, train_test_split

from features import DATASET_PATH, prepare_features
from models_registry import RANDOM_STATE, get_models


def load_data():
    df = pd.read_csv(DATASET_PATH)
    X = prepare_features(df)
    y = df["Risk_Level"]
    return train_test_split(X, y, test_size=0.2, random_state=RANDOM_STATE)


def compare_models(verbose=False):
    models = get_models()
    X_train, X_test, y_train, y_test = load_data()
    results = []

    print("Comparing risk classifiers on synthetic patient data\n")
    print(f"{'Model':<26} {'CV Accuracy':>14} {'Test Accuracy':>14}")
    print("-" * 56)

    for name, model in models.items():
        cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring="accuracy")
        model.fit(X_train, y_train)
        test_accuracy = accuracy_score(y_test, model.predict(X_test))

        results.append(
            {
                "model": name,
                "cv_mean": cv_scores.mean(),
                "cv_std": cv_scores.std(),
                "test_accuracy": test_accuracy,
                "estimator": model,
            }
        )

        print(f"{name:<26} {cv_scores.mean():>13.3f} {test_accuracy:>14.3f}")

        if verbose:
            print(classification_report(y_test, model.predict(X_test)))
            print()

    results.sort(key=lambda row: row["cv_mean"], reverse=True)

    print("\nRanking (by CV accuracy):")
    for index, row in enumerate(results, start=1):
        print(f"  {index}. {row['model']}: {row['cv_mean']:.3f}")

    best = results[0]
    print(f"\nBest: {best['model']} (CV {best['cv_mean']:.3f}, test {best['test_accuracy']:.3f})")
    return results, best


def main():
    parser = argparse.ArgumentParser(
        description="Compare sklearn classifiers for patient risk stratification."
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Print classification report per model"
    )
    parser.add_argument(
        "--list", action="store_true", help="List available model names and exit"
    )
    parser.add_argument(
        "--export",
        default="model_comparison_results.csv",
        nargs="?",
        const="model_comparison_results.csv",
        help="Export comparison table to CSV",
    )
    args = parser.parse_args()

    if args.list:
        for name in get_models():
            print(name)
        return

    results, best = compare_models(verbose=args.verbose)

    if args.export:
        export_rows = [
            {
                "model": row["model"],
                "cv_accuracy": round(row["cv_mean"], 4),
                "cv_std": round(row["cv_std"], 4),
                "test_accuracy": round(row["test_accuracy"], 4),
            }
            for row in results
        ]
        export_df = pd.DataFrame(export_rows)
        export_df.to_csv(args.export, index=False)
        print(f"\nResults exported to {args.export}")


if __name__ == "__main__":
    main()
