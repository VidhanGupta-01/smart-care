# Smart Care

**AI-powered patient triage & healthcare analytics platform** — built for frontline intake decision support, exploratory data analysis, and ML-driven risk stratification.

Developed for the **Kanini Hackathon (Chennai)**.

[![Live Demo](https://img.shields.io/badge/Live_Demo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://smart-care-triage.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)]()
[![ML](https://img.shields.io/badge/Model-AdaBoost-22C55E?style=flat-square)]()
[![Accuracy](https://img.shields.io/badge/Accuracy-95%25-blue?style=flat-square)]()

**🔗 Live App:** [smart-care-triage.streamlit.app](https://smart-care-triage.streamlit.app/)  
**📂 Repository:** [github.com/VidhanGupta-01/smart-care](https://github.com/VidhanGupta-01/smart-care)

![Smart Care – Application Home](smart_care_home.png)

---

## Overview

Smart Care helps triage staff **prioritize patients faster** by combining:

- A **live triage web app** (vitals, symptoms, optional EHR upload)
- An **interactive analytics dashboard** (EDA, charts, model metrics)
- A **full data analyst pipeline** (SQL, Excel, Power BI–ready exports)
- A **production ML model** (AdaBoost, 95% test accuracy)

> ⚠️ **Disclaimer:** This is a decision-support tool only. It does **not** diagnose diseases, prescribe treatment, or replace clinical judgment. All data is synthetic.

---

## What It Does

| Capability | Description |
|---|---|
| **Risk Stratification** | Classifies patients into **Low / Medium / High** risk |
| **Care Routing** | Recommends care level (OPD / Ward / ICU) and department |
| **Explainability** | Surfaces key factors driving each triage decision |
| **Safety Checks** | Escalates care when model confidence is low |
| **EHR Ingestion** | Optional PDF/TXT upload with basic field extraction |
| **Multilingual UI** | English, Hindi, and Tamil |

---

## Key Highlights

### For AI / ML roles
- Benchmarked **13 classifiers** (Decision Tree, Random Forest, AdaBoost, XGBoost, LightGBM, SVM, and more)
- Selected **AdaBoost** as production model — **95% test accuracy**, **94.8% CV accuracy**
- Feature importance, confusion matrix, and classification reports
- Reproducible training via `train_model.py` and `compare_models.py`

### For Data Analyst roles
- **EDA dashboard** with distributions, correlation heatmaps, and clinical pattern analysis
- **SQLite database** with schema, views, and sample analyst queries
- **Excel workbook** (multi-sheet) and CSV exports for BI tools
- **Power BI integration guide** with recommended visuals and DAX measures

---

## Tech Stack

| Layer | Tools |
|---|---|
| **App & Dashboard** | Streamlit, Plotly |
| **ML** | scikit-learn, XGBoost, LightGBM, AdaBoost |
| **Data** | Pandas, NumPy |
| **Database** | SQLite |
| **Reporting** | Excel (openpyxl), Power BI |
| **Document / Vision** | pdfplumber, OpenCV, Pillow |
| **Language** | Python 3 |

---

## Model Performance

| Model | CV Accuracy | Test Accuracy |
|---|---|---|
| **AdaBoost** *(production)* | **0.948** | **0.950** |
| LightGBM | 0.940 | 0.920 |
| Gradient Boosting | 0.920 | 0.890 |
| XGBoost | 0.910 | 0.900 |
| Decision Tree *(baseline)* | 0.722 | 0.800 |

Run `python compare_models.py` to reproduce the full benchmark.

---

## Project Structure

```
smart-care/
├── app.py                      # Main triage application
├── predict.py                  # Inference & care routing logic
├── analytics.py                # EDA & model evaluation helpers
├── features.py                 # Shared feature engineering
├── models_registry.py          # All ML model definitions
├── train_model.py              # Train & save production model
├── compare_models.py           # Benchmark all models
├── synthetic_patients.csv      # Dataset (500 records)
├── risk_classifier.pkl         # Trained AdaBoost model
├── pages/
│   └── 1_Data_Analytics.py     # Analytics dashboard page
├── database/
│   ├── schema.sql              # SQLite schema & views
│   ├── analyst_queries.sql     # Sample SQL for portfolio
│   ├── setup_db.py             # Build DB + export files
│   └── smart_care.db           # SQLite database
├── exports/
│   ├── smart_care_analytics.xlsx
│   └── *.csv                   # Power BI / Tableau ready
└── powerbi/
    └── POWERBI_SETUP.md        # Power BI dashboard guide
```

---

## Quick Start

### 1. Clone & install

```bash
git clone https://github.com/VidhanGupta-01/smart-care.git
cd smart-care
pip install -r requirements.txt
```

### 2. Run the app

```bash
streamlit run app.py
```

Open the sidebar → **Data Analytics** for EDA, model metrics, and BI exports.

### 3. Train or compare models

```bash
python compare_models.py                    # benchmark all models
python train_model.py --model adaboost      # train production model
```

### 4. Generate SQL / Excel / Power BI files

```bash
python database/setup_db.py
```

Then import `exports/smart_care_analytics.xlsx` into **Power BI Desktop**.  
Full instructions: [`powerbi/POWERBI_SETUP.md`](powerbi/POWERBI_SETUP.md)

---

## System Flow

```
Patient Input (vitals, symptoms, optional EHR)
        ↓
Feature Encoding
        ↓
AdaBoost Risk Prediction (Low / Medium / High)
        ↓
Confidence & Safety Checks
        ↓
Care Level + Department + Specialty Routing
        ↓
Explainable Triage Output
```

---

## Skills Demonstrated

`Python` · `Pandas` · `EDA` · `Data Visualization` · `SQL` · `SQLite` · `Excel` · `Power BI` · `scikit-learn` · `Model Evaluation` · `Feature Engineering` · `Cross-Validation` · `Streamlit` · `Git/GitHub`

---

## Safety & Ethics

- No disease diagnosis or treatment recommendations
- No replacement for licensed clinical judgment
- Synthetic data only — privacy-safe for demos and portfolios
- Conservative escalation when confidence is low

---

## Future Scope

- Temporal patient re-evaluation over time
- Queue-level triage simulation
- Published Power BI dashboard link
- Audio-based intake signals (e.g., cough patterns)

---

## Author

**Vidhan Gupta**  
Kanini Hackathon (Chennai)

If this project helped you or you'd like to collaborate, feel free to star the repo or open an issue.

---

<p align="center">
  <strong>Smart Care</strong> — Triage smarter. Analyze deeper. Decide safer.
</p>
