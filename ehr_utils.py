import pdfplumber
import re

def extract_text_from_file(uploaded_file):
    if uploaded_file.name.endswith(".txt"):
        return uploaded_file.read().decode("utf-8")

    if uploaded_file.name.endswith(".pdf"):
        text = ""
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text

    return ""

def parse_basic_ehr_fields(text):
    extracted = {}

    try:
        import re

        age_match = re.search(r"age[:\s]+(\d{1,3})", text, re.IGNORECASE)
        if age_match:
            extracted["Age"] = int(age_match.group(1))

        if re.search(r"\bmale\b", text, re.IGNORECASE):
            extracted["Gender"] = "Male"
        elif re.search(r"\bfemale\b", text, re.IGNORECASE):
            extracted["Gender"] = "Female"

        hr_match = re.search(r"heart rate[:\s]+(\d{2,3})", text, re.IGNORECASE)
        if hr_match:
            extracted["Heart_Rate"] = int(hr_match.group(1))

        bp_match = re.search(r"bp[:\s]+(\d{2,3})", text, re.IGNORECASE)
        if bp_match:
            extracted["Systolic_BP"] = int(bp_match.group(1))

        temp_match = re.search(r"temp(?:erature)?[:\s]+(\d+\.?\d*)", text, re.IGNORECASE)
        if temp_match:
            extracted["Temperature"] = float(temp_match.group(1))

        conditions = []
        for cond in ["heart disease", "diabetes", "hypertension", "asthma"]:
            if cond in text.lower():
                conditions.append(cond)

        extracted["Conditions"] = conditions

    except Exception:
        extracted["error"] = "Unable to parse some fields from document"

    return extracted