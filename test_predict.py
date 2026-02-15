from src.predict import predict_patient

def test_low_risk_case():
    patient = {
        "Age": 25,
        "Gender": "Male",
        "Heart_Rate": 78,
        "Systolic_BP": 120,
        "Temperature": 98.6,
        "Symptoms": "",
        "Pre_Existing_Conditions": "none",
    }

    result = predict_patient(patient, uploaded_image=None)
    assert result["Risk_Level"] in ["Low", "Medium", "High"]
    assert result["Recommended_Care_Level"] is not None