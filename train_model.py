import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib
from sklearn.model_selection import cross_val_score

df = pd.read_csv("data/synthetic_patients.csv")

df["Gender"] = df["Gender"].map({"Male": 0, "Female": 1})

df["Has_Chest_Pain"] = df["Symptoms"].str.contains("chest pain").astype(int)
df["Has_Fever"] = df["Symptoms"].str.contains("fever").astype(int)
df["Has_Heart_Disease"] = df["Pre_Existing_Conditions"].str.contains("heart disease").astype(int)

X = df[
    [
        "Age",
        "Gender",
        "Heart_Rate",
        "Systolic_BP",
        "Temperature",
        "Has_Chest_Pain",
        "Has_Fever",
        "Has_Heart_Disease",
    ]
]

y = df["Risk_Level"]


X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = DecisionTreeClassifier(
    max_depth=5,
    random_state=42
)

cv_scores = cross_val_score(
    model,
    X,
    y,
    cv=5,          
    scoring="accuracy"
)

print("Cross-validation scores:", cv_scores)
print("Mean CV accuracy:", cv_scores.mean())

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print("Model Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n")
print(classification_report(y_test, y_pred))

joblib.dump(model, "data/risk_classifier.pkl")
print("\nModel saved as data/risk_classifier.pkl ✅")