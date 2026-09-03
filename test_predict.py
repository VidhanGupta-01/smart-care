from predict import predict_patient

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

def test_high_risk_case():
    patient = {
        "Age": 70,
        "Gender": "Female",
        "Heart_Rate": 125,
        "Systolic_BP": 165,
        "Temperature": 102.5,
        "Symptoms": "chest pain, breathlessness",
        "Pre_Existing_Conditions": "heart disease",
    }
    result = predict_patient(patient, uploaded_image=None)
    assert result["Risk_Level"] == "High"
    assert result["Recommended_Care_Level"] == "ICU-level attention"
    assert "Emergency" in result["Recommended_Department"]
    
