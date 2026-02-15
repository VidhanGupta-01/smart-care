import streamlit as st
from src.predict import predict_patient
from src.ehr_utils import extract_text_from_file, parse_basic_ehr_fields

st.set_page_config(
    page_title="Smart Care",
    page_icon="🩺",
    layout="centered"
)

st.caption("Language")
language = st.selectbox(
    "",
    ["English", "Hindi", "Tamil"],
    label_visibility="collapsed"
)

TEXT = {
    "English": {
        "title": "🩺 AI-Powered Smart Patient Triage",
        "caption": "Decision-support triage system • Developed as part of the Kanini Hackathon",
        "ehr_upload": "Optional Health Document Upload (EHR / Report)",
        "patient_details": "Patient Details",
        "skin_observation": "Optional Skin Observation",
        "assess": "🧠 Generate Triage Summary",
        "triage_result": "Triage Result",
        "confidence": "Assessment Confidence",
        "recommended_department": "Recommended Department",
        "recommended_care": "Recommended Care Level",
        "key_factors": "Key Factors Influencing Triage",
        "what_next": "What happens next?",
    },

    "Hindi": {
        "title": "🩺 एआई आधारित रोगी प्राथमिकता प्रणाली",
        "caption": "निर्णय-सहायता ट्रायेज प्रणाली • कनिनी हैकाथॉन",
        "ehr_upload": "वैकल्पिक स्वास्थ्य दस्तावेज़ अपलोड करें",
        "patient_details": "रोगी विवरण",
        "skin_observation": "वैकल्पिक त्वचा निरीक्षण",
        "assess": "🧠 रोगी का मूल्यांकन करें",
        "triage_result": "प्राथमिकता मूल्यांकन",
        "confidence": "मूल्यांकन का विश्वास स्तर",
        "recommended_department": "अनुशंसित विभाग",
        "recommended_care": "अनुशंसित देखभाल स्तर",
        "key_factors": "मूल्यांकन को प्रभावित करने वाले कारक",
        "what_next": "आगे क्या होगा?",
    },

    "Tamil": {
        "title": "🩺 AI ஆதாரமான நோயாளர் முன்னுரிமை அமைப்பு",
        "caption": "மருத்துவ முடிவு ஆதரவு அமைப்பு • கனினி ஹேக்கத்தான்",
        "ehr_upload": "விருப்பமான மருத்துவ ஆவணம் பதிவேற்றம்",
        "patient_details": "நோயாளர் விவரங்கள்",
        "skin_observation": "விருப்பமான தோல் கவனம்",
        "assess": "🧠 நோயாளியை மதிப்பிடு",
        "triage_result": "முன்னுரிமை மதிப்பீடு",
        "confidence": "மதிப்பீட்டு நம்பிக்கை",
        "recommended_department": "பரிந்துரைக்கப்பட்ட துறை",
        "recommended_care": "பரிந்துரைக்கப்பட்ட பராமரிப்பு நிலை",
        "key_factors": "மதிப்பீட்டில் தாக்கம் செலுத்தும் காரணங்கள்",
        "what_next": "அடுத்த கட்டம் என்ன?",
    }
}

col_logo, col_title = st.columns([1, 6])

with col_logo:
    st.image("assets\Gemini_Generated_Image_w4t6h5w4t6h5w4t6-removebg-preview.png", width=300)

with col_title:
    st.markdown(
        f"""
        <h1 style="margin-bottom: 0;">Smart Care</h1>
        <p style="margin-top: 0; color: #9ca3af;">
        For frontline triage staff and patient intake support
        </p>
        """,
        unsafe_allow_html=True
    )

st.divider()


st.subheader("Upload Medical Report (Optional)")
ehr_file = st.file_uploader(
    "Upload a health document (PDF or TXT)",
    type=["pdf", "txt"]
)

ehr_data = {}

if ehr_file is not None:
    text = extract_text_from_file(ehr_file)
    ehr_data = parse_basic_ehr_fields(text)

    if "error" in ehr_data:
        st.warning("Some information in the uploaded document could not be parsed correctly.")

    st.success("Health document processed. Extracted information applied where available.")

st.divider()


st.subheader(TEXT[language]["patient_details"])

col1, col2 = st.columns(2)

with col1:
    age = st.slider("Age", 1, 100, ehr_data.get("Age", 45))
    gender = st.selectbox(
        "Gender",
        ["Male", "Female"],
        index=0 if ehr_data.get("Gender", "Male") == "Male" else 1
    )
    heart_rate = st.slider("Heart Rate (bpm)", 40, 160, ehr_data.get("Heart_Rate", 80))

with col2:
    systolic_bp = st.slider("Systolic BP (mmHg)", 80, 200, ehr_data.get("Systolic_BP", 120))
    temperature = st.slider("Temperature (°F)", 95.0, 105.0, ehr_data.get("Temperature", 98.6))

symptoms = st.multiselect(
    "Symptoms",
    ["chest pain", "fever", "cough", "breathlessness", "fatigue", "dizziness"]
)

conditions = st.multiselect(
    "Pre-existing Conditions",
    ["heart disease", "diabetes", "hypertension", "asthma"],
    default=ehr_data.get("Conditions", [])
)


st.subheader("Visible Skin Concern (Optional)")
uploaded_image = st.file_uploader(
    "Upload image if you have concerns about a visible skin issue (optional)",
    type=["jpg", "jpeg", "png"]
)

st.caption(
    "Images are used only to flag possible visual irregularities and do not perform diagnosis."
)

st.divider()


if st.button(TEXT[language]["assess"], type="primary"):

    patient = {
        "Age": age,
        "Gender": gender,
        "Heart_Rate": heart_rate,
        "Systolic_BP": systolic_bp,
        "Temperature": temperature,
        "Symptoms": ", ".join(symptoms),
        "Pre_Existing_Conditions": ", ".join(conditions) if conditions else "none",
    }

    result = predict_patient(patient, uploaded_image)

    st.info(
        "This assessment represents an initial triage snapshot based on current inputs. "
        "Re-evaluation is recommended if the patient’s condition changes."
    )

    st.subheader(TEXT[language]["triage_result"])


    RISK_COLORS = {"Low": "green", "Medium": "orange", "High": "red"}
    risk_color = RISK_COLORS.get(result["Risk_Level"], "gray")

    st.markdown(
        f"<h2 style='color:{risk_color};'>Risk Level: {result['Risk_Level']}</h2>",
        unsafe_allow_html=True
    )

    st.write(f"**Assessment Confidence:** {result['Confidence']}")
    st.write(f"**Recommended Department:** {result['Recommended_Department']}")
    st.write(f"**Recommended Care Level:** {result['Recommended_Care_Level']}")

    if result.get("Suggested_Specialties"):
        st.write("**Suggested Clinical Specialty (for initial evaluation):**")
        for spec in result["Suggested_Specialties"]:
            st.write(f"- {spec}")

        st.caption("Specialty suggestions are indicative and intended only to support triage routing.")

    if result["Key_Factors"]:
        st.write("**Key Factors Influencing Triage:**")
        for factor in result["Key_Factors"]:
            st.write(f"- {factor}")

    if result["Escalation_Reasons"]:
        st.info("Care level adjusted due to:")
        for reason in result["Escalation_Reasons"]:
            st.write(f"- {reason}")

    st.divider()

    st.subheader("Triage Overview (At a Glance)")

    with st.container():
        st.markdown(
            """
            <div style="
                border: 1px solid #2c2c2c;
                border-radius: 10px;
                padding: 16px;
                background-color: #111;
            ">
            """,
            unsafe_allow_html=True
        )

        colA, colB, colC = st.columns(3)

        with colA:
            st.metric("Overall Risk", result["Risk_Level"])

        with colB:
            st.metric("Care Priority", result["Recommended_Care_Level"])

        with colC:
            st.metric("Assigned Department", result["Recommended_Department"])

        st.markdown("</div>", unsafe_allow_html=True)

    st.subheader(TEXT[language]["what_next"])

    st.write(
        f"- Patient is prioritized for **{result['Recommended_Care_Level']}**\n"
        f"- Directed to **{result['Recommended_Department']}**\n"
        "- Final clinical decisions remain with healthcare professionals"
    )

    st.markdown(
        f"""
        <div style="
            margin-top: 12px;
            padding: 12px;
            border-radius: 8px;
            background-color: #0f172a;
            border-left: 5px solid {'#22c55e' if result['Risk_Level']=='Low' else '#f59e0b' if result['Risk_Level']=='Medium' else '#ef4444'};
        ">
            <strong>Current Triage Status:</strong><br>
            Patient can be directed to <strong>{result['Recommended_Department']}</strong> with 
            <strong>{result['Recommended_Care_Level']}</strong>.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.caption(
        "This system supports triage prioritization and does not provide diagnosis or treatment recommendations."
    )