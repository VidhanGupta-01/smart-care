import joblib
import pandas as pd
import cv2
import numpy as np
from PIL import Image

from features import MODEL_PATH, prepare_features
from age_thresholds import vital_risk_flags, get_age_band

model = joblib.load(MODEL_PATH)

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
    features = prepare_features(pd.DataFrame([patient]))

    risk = model.predict(features)[0]
    confidence = max(model.predict_proba(features)[0])
    confidence_label = confidence_level(confidence)

    care_level = recommend_care_level(risk)
    department = recommend_department(risk, patient["Symptoms"])

    escalation_reasons = []

    if confidence < CONFIDENCE_THRESHOLD:
        care_level = CARE_ESCALATION_MAP[care_level]
        escalation_reasons.append("Low model confidence – clinician review advised")

    # --- Age-band safety cross-check -----------------------------------
    # The trained model above was fit on fixed adult-calibrated vital
    # thresholds (see generate_data.py). That means a pediatric or
    # geriatric patient with vitals that are abnormal FOR THEIR AGE, but
    # within the adult "normal" range, could be scored Low by the model
    # while genuinely needing escalation. This cross-check catches that
    # gap without needing to retrain the model — it runs the same vitals
    # through age-specific thresholds (age_thresholds.py) and escalates
    # if the model's fixed-threshold view would have missed something.
    age_band = get_age_band(patient["Age"])
    age_flags = vital_risk_flags(
        age=patient["Age"],
        heart_rate=patient["Heart_Rate"],
        systolic_bp=patient["Systolic_BP"],
        temperature=patient["Temperature"],
    )
    age_flag_count = sum(v for k, v in age_flags.items() if k.endswith("_flag"))

    RISK_ORDER = ["Low", "Medium", "High"]
    if age_flag_count >= 2 and RISK_ORDER.index(risk) < RISK_ORDER.index("Medium"):
        risk = "Medium"
        care_level = recommend_care_level(risk)
        department = recommend_department(risk, patient["Symptoms"])
        escalation_reasons.append(
            f"Age-band safety check: vitals are abnormal for a {age_band} patient "
            f"even though they fall within general adult-normal ranges — escalated "
            f"per age-stratified thresholds."
        )

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
    if age_band in ("pediatric", "geriatric") and age_flag_count > 0:
        factors.append(
            f"{age_flag_count} vital sign(s) abnormal specifically for {age_band} "
            f"age-band thresholds."
        )

    return {
        "Risk_Level": risk,
        "Confidence": confidence_label,
        "Recommended_Department": department,
        "Recommended_Care_Level": care_level,
        "Key_Factors": factors,
        "Escalation_Reasons": escalation_reasons,
        "Suggested_Specialties": specialties,
        "Age_Band": age_band,
    }
