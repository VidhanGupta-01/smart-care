"""
Simulated patient dataset for PatientTriage.ai v2 prototype.

Round 2 minimum expectations this file satisfies:
- 15-20 simulated patient records                         -> 18 records
- At least one ambiguous presentation                      -> P07
- At least one pediatric OR geriatric case                 -> P03 (pediatric), P11 (geriatric)
- At least one zero-history (first-time) patient            -> P14
- Mixed data availability (~half with prior history)        -> History_Available column

Each record is illustrative/simulated, not real patient data, as expected
by the brief ("no single correct dataset").
"""

import pandas as pd

PATIENTS = [
    # --- Straightforward low risk ---
    dict(Patient_ID="P01", Age=29, Gender="Female", Heart_Rate=78, Systolic_BP=118,
         Temperature=98.6, Resp_Rate=14, Symptoms="headache",
         Pre_Existing_Conditions="none", History_Available=True,
         Case_Tag="baseline_low"),

    dict(Patient_ID="P02", Age=41, Gender="Male", Heart_Rate=82, Systolic_BP=124,
         Temperature=99.1, Resp_Rate=16, Symptoms="cough, fatigue",
         Pre_Existing_Conditions="none", History_Available=True,
         Case_Tag="baseline_low"),

    # --- Pediatric case: fever that looks mild by ADULT threshold (101.0)
    # but is actually clinically significant for a 3-year-old (>100.4) ---
    dict(Patient_ID="P03", Age=3, Gender="Female", Heart_Rate=132, Systolic_BP=95,
         Temperature=100.8, Resp_Rate=32, Symptoms="fever, fussiness",
         Pre_Existing_Conditions="none", History_Available=False,
         Case_Tag="pediatric_age_sensitive"),

    dict(Patient_ID="P04", Age=55, Gender="Male", Heart_Rate=118, Systolic_BP=158,
         Temperature=99.9, Resp_Rate=20, Symptoms="chest pain, breathlessness",
         Pre_Existing_Conditions="heart disease, hypertension", History_Available=True,
         Case_Tag="high_risk_cardiac"),

    dict(Patient_ID="P05", Age=34, Gender="Male", Heart_Rate=95, Systolic_BP=130,
         Temperature=98.9, Resp_Rate=15, Symptoms="minor laceration",
         Pre_Existing_Conditions="none", History_Available=True,
         Case_Tag="baseline_low"),

    dict(Patient_ID="P06", Age=67, Gender="Female", Heart_Rate=88, Systolic_BP=142,
         Temperature=98.4, Resp_Rate=18, Symptoms="joint pain",
         Pre_Existing_Conditions="diabetes", History_Available=True,
         Case_Tag="baseline_medium"),

    # --- Ambiguous presentation: vague, overlapping symptoms, near-normal
    # vitals — doesn't map cleanly to a severity level. This is the
    # required "ambiguous" case; system should show LOW confidence, not
    # a falsely precise score. ---
    dict(Patient_ID="P07", Age=26, Gender="Female", Heart_Rate=98, Systolic_BP=112,
         Temperature=99.4, Resp_Rate=18, Symptoms="fatigue, dizziness, nausea",
         Pre_Existing_Conditions="none", History_Available=False,
         Case_Tag="ambiguous_presentation"),

    dict(Patient_ID="P08", Age=45, Gender="Male", Heart_Rate=140, Systolic_BP=88,
         Temperature=103.2, Resp_Rate=26, Symptoms="fever, breathlessness, confusion",
         Pre_Existing_Conditions="diabetes", History_Available=True,
         Case_Tag="high_risk_sepsis"),

    dict(Patient_ID="P09", Age=8, Gender="Male", Heart_Rate=110, Systolic_BP=98,
         Temperature=99.0, Resp_Rate=22, Symptoms="cough, mild fever",
         Pre_Existing_Conditions="asthma", History_Available=True,
         Case_Tag="pediatric_baseline"),

    dict(Patient_ID="P10", Age=52, Gender="Female", Heart_Rate=90, Systolic_BP=136,
         Temperature=98.7, Resp_Rate=16, Symptoms="headache, blurred vision",
         Pre_Existing_Conditions="hypertension", History_Available=True,
         Case_Tag="baseline_medium"),

    # --- Geriatric case: blunted fever response. Temperature looks almost
    # "normal" by adult threshold (101.0) but is actually elevated and
    # concerning for a 78-year-old (geriatric threshold: 100.0), combined
    # with tachycardia and low BP — classic silent sepsis presentation
    # in the elderly. ---
    dict(Patient_ID="P11", Age=78, Gender="Male", Heart_Rate=104, Systolic_BP=96,
         Temperature=100.3, Resp_Rate=21, Symptoms="weakness, confusion",
         Pre_Existing_Conditions="hypertension, diabetes", History_Available=True,
         Case_Tag="geriatric_age_sensitive"),

    dict(Patient_ID="P12", Age=19, Gender="Female", Heart_Rate=100, Systolic_BP=110,
         Temperature=98.8, Resp_Rate=16, Symptoms="anxiety, palpitations",
         Pre_Existing_Conditions="none", History_Available=False,
         Case_Tag="baseline_low"),

    dict(Patient_ID="P13", Age=61, Gender="Male", Heart_Rate=126, Systolic_BP=164,
         Temperature=99.6, Resp_Rate=22, Symptoms="chest pain",
         Pre_Existing_Conditions="heart disease", History_Available=True,
         Case_Tag="high_risk_cardiac"),

    # --- Zero-history, first-time patient: no prior hospital record at
    # all, only what's observed right now. Required case. ---
    dict(Patient_ID="P14", Age=37, Gender="Female", Heart_Rate=112, Systolic_BP=94,
         Temperature=101.8, Resp_Rate=24, Symptoms="fever, abdominal pain",
         Pre_Existing_Conditions="unknown", History_Available=False,
         Case_Tag="zero_history_first_time"),

    dict(Patient_ID="P15", Age=70, Gender="Female", Heart_Rate=92, Systolic_BP=150,
         Temperature=98.2, Resp_Rate=17, Symptoms="fatigue",
         Pre_Existing_Conditions="diabetes, hypertension", History_Available=True,
         Case_Tag="geriatric_baseline"),

    dict(Patient_ID="P16", Age=15, Gender="Male", Heart_Rate=105, Systolic_BP=118,
         Temperature=99.5, Resp_Rate=18, Symptoms="ankle injury",
         Pre_Existing_Conditions="none", History_Available=True,
         Case_Tag="adolescent_baseline"),

    dict(Patient_ID="P17", Age=48, Gender="Male", Heart_Rate=88, Systolic_BP=128,
         Temperature=98.6, Resp_Rate=15, Symptoms="rash",
         Pre_Existing_Conditions="none", History_Available=False,
         Case_Tag="baseline_low"),

    dict(Patient_ID="P18", Age=83, Gender="Female", Heart_Rate=112, Systolic_BP=88,
         Temperature=99.8, Resp_Rate=24, Symptoms="fall, confusion, weakness",
         Pre_Existing_Conditions="heart disease, hypertension", History_Available=True,
         Case_Tag="geriatric_high_risk"),
]


def load_simulated_patients() -> pd.DataFrame:
    return pd.DataFrame(PATIENTS)


if __name__ == "__main__":
    df = load_simulated_patients()
    df.to_csv("simulated_patients.csv", index=False)
    print(f"Generated {len(df)} simulated patients -> simulated_patients.csv")
    print(df[["Patient_ID", "Age", "Case_Tag"]].to_string(index=False))
