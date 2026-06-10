# Smart Care × Power BI Setup Guide

Use this guide to connect your Smart Care project to **Power BI Desktop** for a portfolio-ready analyst dashboard.

## Step 1 — Generate data files

From the project root, run:

```bash
pip install -r requirements.txt
python database/setup_db.py
```

This creates:

| Output | Purpose |
|---|---|
| `database/smart_care.db` | SQLite database (SQL + Power BI) |
| `exports/smart_care_analytics.xlsx` | Excel workbook (multi-sheet) |
| `exports/*.csv` | Individual tables for Power BI |

## Step 2 — Import into Power BI (recommended: Excel)

1. Open **Power BI Desktop**
2. **Home → Get Data → Excel**
3. Select `exports/smart_care_analytics.xlsx`
4. Load these sheets:
   - `Patients`
   - `Risk_Distribution`
   - `Vitals_by_Risk`
   - `Symptoms`
   - `Conditions`
   - `Feature_Importance`
   - `Model_Comparison`

### Alternative: SQLite

1. **Get Data → Database → SQLite**
2. Browse to `database/smart_care.db`
3. Load tables: `patients`, `model_benchmark`
4. Load views: `vw_risk_distribution`, `vw_vitals_by_risk`, `vw_gender_risk`

## Step 3 — Recommended visuals

| Visual | Field setup |
|---|---|
| **KPI cards** | Total patients, % High risk, avg heart rate |
| **Donut chart** | `Risk_Level` vs `Patient_Count` |
| **Clustered bar** | `Symptom` vs `Count` |
| **Grouped bar** | `Risk_Level` vs avg `Heart_Rate`, `Systolic_BP` |
| **Matrix** | `gender` × `risk_level` × count |
| **Bar chart (horizontal)** | `model` vs `cv_accuracy` from Model_Comparison |
| **Table** | Top high-risk patients with vitals and symptoms |

## Step 4 — Sample DAX measures

```dax
Total Patients = COUNTROWS(Patients)

High Risk % =
DIVIDE(
    CALCULATE(COUNTROWS(Patients), Patients[Risk_Level] = "High"),
    COUNTROWS(Patients)
)

Avg Heart Rate = AVERAGE(Patients[Heart_Rate])

Best Model Accuracy =
MAXX(Model_Comparison, Model_Comparison[cv_accuracy])
```

## Step 5 — Publish and add to resume

1. **File → Publish to web** (or publish to Power BI Service)
2. Add to resume:

> Built Power BI executive dashboard on Smart Care triage data (500 patients) with risk KPIs, symptom trends, vitals analysis, and ML model benchmarking — alongside Python EDA pipeline.

## SQL portfolio angle

Use `database/analyst_queries.sql` to demonstrate SQL skills in interviews.

Example talking point:

> "I structured patient data in SQLite, wrote analyst queries for risk segmentation, and connected the same database to Power BI for stakeholder dashboards."
