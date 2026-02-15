import pandas as pd
import numpy as np
import random

random.seed(42)
np.random.seed(42)

NUM_SAMPLES = 500

def generate_patient():
    age = random.randint(1, 90)
    gender = random.choice(["Male", "Female"])

    heart_rate = random.randint(50, 140)
    heart_rate += random.randint(-5, 5)
    heart_rate = max(40, min(160, heart_rate))
    systolic_bp = random.randint(90, 180)
    systolic_bp += random.randint(-8, 8)
    systolic_bp = max(80, min(200, systolic_bp))
    temperature = round(random.uniform(96.0, 104.0), 1)

    symptoms_pool = [
        "chest pain", "fever", "cough", "breathlessness",
        "headache", "dizziness", "fatigue", "nausea"
    ]
    symptoms = random.sample(symptoms_pool, random.randint(1, 3))
    symptoms = ", ".join(symptoms)

    conditions_pool = [
        "diabetes", "hypertension", "asthma", "heart disease"
    ]
    pre_existing = random.sample(conditions_pool, random.randint(0, 2))
    pre_existing = ", ".join(pre_existing) if pre_existing else "none"

    risk_score = 0

    if age > 60:
        risk_score += 1
    if heart_rate > 110:
        risk_score += 1
    if systolic_bp > 150:
        risk_score += 1
    if temperature > 101:
        risk_score += 1
    if "heart disease" in pre_existing:
        risk_score += 1
    if "chest pain" in symptoms:
        risk_score += 1

    if risk_score >= 4:
        risk_level = "High"
    elif risk_score >= 2:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return {
        "Age": age,
        "Gender": gender,
        "Heart_Rate": heart_rate,
        "Systolic_BP": systolic_bp,
        "Temperature": temperature,
        "Symptoms": symptoms,
        "Pre_Existing_Conditions": pre_existing,
        "Risk_Level": risk_level
    }

data = [generate_patient() for _ in range(NUM_SAMPLES)]
df = pd.DataFrame(data)

df.to_csv("data/synthetic_patients.csv", index=False)

print("Synthetic dataset generated ✅")
print(df.head())