import joblib
import pandas as pd
import cv2
import numpy as np
from PIL import Image

model = joblib.load("data/risk_classifier.pkl")

CONFIDENCE_THRESHOLD = 0.65

CARE_ESCALATION_MAP = {
    "OPD-level care": "Ward / Observation",
    "Ward / Observation": "ICU-level attention",
    "ICU-level attention": "ICU-level attention"
}

def detect_skin_irregularity(uploaded_image):
    image = Image.open(uploaded_image).convert("RGB")
    img = np.array(image)
    img = cv2.resize(img, (224, 224))

    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    _, s, v = cv2.split(hsv)

    color_variation = np.std(s) + np.std(v)

    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    texture_variation = np.std(gray)

    irregularity_score = color_variation + texture_variation
    return irregularity_score > 40   

def suggest_specialty(symptoms, conditions, vitals):
    specialties = set()

    if "chest pain" in symptoms or "heart disease" in conditions:
        specialties.add("Cardiology")

    if "fever" in symptoms or "cough" in symptoms:
        specialties.add("General Medicine")

    if "breathlessness" in symptoms:
        specialties.add("Pulmonology")

    if "dizziness" in symptoms:
        specialties.add("Neurology")

    if vitals.get("skin_flag", False):
        specialties.add("Dermatology")

    if not specialties:
        specialties.add("General Medicine")

    return sorted(list(specialties))

def recommend_department(risk, symptoms):
    if risk == "High":
        if "chest pain" in symptoms:
            return "Emergency / Cardiology"
        return "Emergency"
    elif risk == "Medium":
        return "General Medicine"
    else:
        return "Outpatient / General Medicine"

def recommend_care_level(risk):
    if risk == "High":
        return "ICU-level attention"
    elif risk == "Medium":
        return "Ward / Observation"
    else:
        return "OPD-level care"
    
def confidence_level(confidence):
    if confidence >= 0.85:
        return "High"
    elif confidence >= 0.65:
        return "Medium"
    else:
        return "Low"
    
def predict_patient(patient, uploaded_image=None):
    df = pd.DataFrame([patient])

    df["Gender"] = df["Gender"].map({"Male": 0, "Female": 1})
    df["Has_Chest_Pain"] = df["Symptoms"].str.contains("chest pain").astype(int)
    df["Has_Fever"] = df["Symptoms"].str.contains("fever").astype(int)
    df["Has_Heart_Disease"] = df["Pre_Existing_Conditions"].str.contains("heart disease").astype(int)

    features = df[
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

    risk = model.predict(features)[0]
    confidence = max(model.predict_proba(features)[0])
    confidence_label = confidence_level(confidence)

    care_level = recommend_care_level(risk)
    department = recommend_department(risk, patient["Symptoms"])

    escalation_reasons = []

    if confidence < CONFIDENCE_THRESHOLD:
        care_level = CARE_ESCALATION_MAP[care_level]
        escalation_reasons.append("Low model confidence – clinician review advised")

    visual_irregularity = False
    if uploaded_image is not None:
        visual_irregularity = detect_skin_irregularity(uploaded_image)
        if visual_irregularity and care_level == "OPD-level care":
            care_level = "Ward / Observation"
            escalation_reasons.append("Visual skin irregularity detected")

    
    symptom_list = [s.strip() for s in patient["Symptoms"].split(",") if s.strip()]
    condition_list = [c.strip() for c in patient["Pre_Existing_Conditions"].split(",") if c.strip()]

    specialties = suggest_specialty(
    symptoms=symptom_list,
    conditions=condition_list,
    vitals={
        "skin_flag": visual_irregularity})

    factors = []
    if patient["Heart_Rate"] > 110:
        factors.append("Elevated heart rate increases immediate clinical risk.")
    if patient["Systolic_BP"] > 150:
        factors.append("High blood pressure contributes to cardiovascular stress.")
    if patient["Temperature"] > 101:
        factors.append("High body temperature indicates possible systemic stress.")
    if "chest pain" in patient["Symptoms"]:
        factors.append("Chest pain is a high-priority triage symptom.")

    return {
        "Risk_Level": risk,
        "Confidence": confidence_label,
        "Recommended_Department": department,
        "Recommended_Care_Level": care_level,
        "Key_Factors": factors,
        "Escalation_Reasons": escalation_reasons,
        "Suggested_Specialties": specialties,
    }