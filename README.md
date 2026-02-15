# Smart Care

Smart Care is a patient triage and care prioritization system designed to support frontline healthcare intake decisions.

This project was developed as part of the **Kanini Hackathon (Chennai)**.

![Smart Care – Application Home](assets/smart_care_home.png)
---

## 🩺 What Smart Care Does

Smart Care provides **decision-support** for patient triage by:
- Categorizing patients into **Low / Medium / High risk**
- Recommending an appropriate **care level** (OPD / Ward / ICU)
- Suggesting relevant **clinical departments or specialties**
- Highlighting **key contributing factors**
- Escalating conservatively when confidence is low

> ⚠️ This system does **not** provide diagnosis, treatment, or bed allocation.

---

## 🔍 Key Features

- Structured patient intake (age, vitals, symptoms)
- Optional EHR / medical report ingestion (PDF / TXT)
- Optional visual flagging for skin-related concerns
- Explainable, interpretable risk stratification
- Multilingual interface (English, Hindi, Tamil)
- Safety-first scope boundaries

---

## 🧠 System Flow

→ Patient Inputs  
→ Feature Encoding  
→ Risk Stratification  
→ Confidence & Safety Checks  
→ Care-Level & Department Routing  
→ Explainable Triage Output

---

## 🧰 Technology Stack

- **Frontend:** Streamlit (Python)
- **Risk Stratification Model:** Decision Tree (scikit-learn)
- **Data:** Synthetic patient dataset
- **Supporting Libraries:** Pandas, NumPy, OpenCV
- **Language:** Python 3

Technology choices prioritize **explainability, safety, and rapid deployment**.

---

## ▶️ How to Run Locally

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the application
```bash
streamlit run app.py
```

---

## 📌 Safety & Ethics

- No disease diagnosis
- No treatment recommendations
- No clinical decision replacement
- Synthetic data only (privacy-safe)
- Intended for triage support, not final decisions

---

## 🚀 Future Scope

- Temporal re-evaluation of patient status
- Queue-level triage simulation
- Audio-based intake signals (e.g., cough patterns)

---

## 👤 Author

Developed by **Vidhan Gupta**
Kanini Hackathon Submission
