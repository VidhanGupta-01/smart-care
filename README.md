# Smart Care — PatientTriage.ai

![CI](https://github.com/VidhanGupta-01/smart-care/actions/workflows/ci.yml/badge.svg)

<img width="494" height="895" alt="smart_care_home (2)" src="https://github.com/user-attachments/assets/9ef37f6e-a9c0-4ccc-9447-0dbc005e54f0" />


**AI-powered, queue-aware patient triage system** — built for frontline ER intake decision support, combining a trained ML risk model with an age-stratified safety layer and live multi-patient queue management.

Built for the **Accenture Innovation Challenge 2026** (Round 2 — PatientTriage.ai track). Originally developed as a single-patient triage tool for the Kanini Hackathon (Chennai); extended here into a full queue-aware system.

> ⚠️ **Disclaimer:** This is a decision-support tool only. It does **not** diagnose diseases, prescribe treatment, or replace clinical judgment. All data is synthetic/simulated.

---

## What This Solves

In a crowded ER, patient sequencing depends on a nurse's judgment under pressure, made largely one patient at a time. The real challenge isn't diagnosing a single case — it's continuously ranking many patients against each other as new ones arrive, vitals change, and the queue shifts by the minute, often with incomplete data and under time pressure.

This system addresses that with two integrated layers:

1. **Single-patient assessment** (original ML model) — a trained classifier gives a fast risk read for one patient at intake, now with an added age-stratified safety cross-check.
2. **Live queue engine** (new, Round 2) — continuously monitors every waiting patient at once, decides what needs a nurse's immediate attention, and always leaves final prioritization and routing as a recommendation a clinician can review or override.

---

## Key Design Principles

| Principle | How it's implemented |
|---|---|
| **Decide vs. recommend** | The system auto-flags which patients need a nurse's eyes *right now* (low-stakes, reversible). Risk tier, priority order, and department routing are always **recommendations**, overridable in one action. |
| **Age-stratified, not one-size-fits-all** | Vital sign thresholds differ by age band (pediatric / adolescent / adult / geriatric) — see `age_thresholds.py`. A fixed adult-calibrated threshold would silently miss danger signs in children and the elderly; this is fixed at the threshold level, not just flagged. |
| **Confidence, always** | Every triage output ships with a confidence score and label — never a bare number. Ambiguous or data-sparse cases are explicitly shown as lower-confidence, not falsely precise. |
| **Asymmetric cost, demonstrated** | Missing a critical case is worse than over-prioritizing a minor one. When confidence is below threshold, the system **escalates** the risk tier rather than leaving it as-is — implemented as an explicit, logged rule (`scoring.py: _apply_escalation_bias`), not left implicit in model weights. |
| **Worst-case design** | The queue is continuously monitored — patients are re-assessed if their wait exceeds a safe interval for their risk tier, or if newly recorded vitals show deterioration. Tested under a simulated 3× surge. |
| **Reviewable & overridable** | Every clinician override is logged with who overrode, what the system recommended, what was chosen instead, and why — the system's original call is never erased, only superseded. |
├── .github/workflows/ci.yml    

---

## Architecture

```
smart-care/
│
├── app.py                    # Main Streamlit app — 2 tabs (see below)
│
├── --- Single-patient ML path (original) ---
├── predict.py                 # AdaBoost inference + age-band safety cross-check (NEW addition)
├── features.py                 # Feature engineering for the ML model
├── train_model.py              # Trains the production AdaBoost classifier
├── compare_models.py           # Benchmarks 13 classifiers
├── generate_data.py            # Synthetic training data generator (500 rows, adult-calibrated)
├── risk_classifier.pkl         # Trained model artifact
├── ehr_utils.py                 # Optional EHR PDF/TXT parsing
├── analytics.py / pages/        # EDA dashboard, SQL/Excel/Power BI exports
│
├── --- Queue-aware engine (NEW, Round 2) ---
├── age_thresholds.py           # Age-band-specific vital sign thresholds
├── scoring.py                   # Rule-based risk scoring with confidence + escalation bias
├── simulated_patients.py        # 18 simulated patients incl. required test cases
├── queue_monitor.py             # Live queue, re-assessment triggers, surge handling
├── audit_log.py                  # Override capture + append-only audit trail
└── simulate_scenarios.py        # Standalone script demonstrating all required behaviors
```

### Why two scoring approaches coexist

The original AdaBoost model (`predict.py`) is trained on synthetic data with **fixed adult-calibrated thresholds** (see `generate_data.py`). Rather than discarding this trained model, Round 2 adds a **transparent, rule-based age cross-check** (`age_thresholds.py`) on top of it: if a patient's vitals are abnormal for *their* age band but within general adult-normal range — the exact "silent safety risk" scenario called out in the brief — the system escalates and logs why. This is intentionally a hybrid: the ML model gives a fast baseline, and a transparent, auditable rule layer catches what a single fixed-threshold model would miss.

The queue engine (`scoring.py`) is deliberately fully rule-based rather than ML-based, so that the asymmetric escalation logic Round 2 asks teams to demonstrate is directly readable and auditable in code, not buried in model weights.

---

## Stated Assumptions

Per the brief's instruction to state assumptions explicitly:

- **Regulatory jurisdiction:** US-based deployment, HIPAA-equivalent. This shapes the audit trail design (append-only, actor-identified, minimum-necessary logging) and the override record format (who / what was recommended / what was chosen / why).
- **Age bands:** Pediatric (0–12), Adolescent (13–17), Adult (18–64), Geriatric (65+) — a simplified stratification for prototype purposes, not clinically validated thresholds.
- **Safe re-check intervals:** High risk → 10 min, Medium → 30 min, Low → 60 min. Illustrative, not clinically validated.
- **Triage framework:** A simplified 3-tier (Low/Medium/High) scale is used rather than a full 5-level ESI scale, for prototype clarity.
- **Data availability:** Roughly half of simulated patients have prior history on file; half are zero-history/first-time patients, per the brief's reference parameters.

---

## Round 2 Minimum Expectations — Coverage

| Requirement | Where it's demonstrated |
|---|---|
| 15–20 simulated patient records | `simulated_patients.py` — 18 records |
| Ambiguous presentation | Patient `P07` |
| Pediatric or geriatric case | `P03` (pediatric), `P11` (geriatric) |
| Zero-history patient | `P14` |
| Simulated 3× surge | `simulate_scenarios.py: scenario_surge()` |
| Confidence indicator on every output | `scoring.py` — `confidence` field always populated |
| At least one clinician override, logged | `simulate_scenarios.py: scenario_override_demo()` |

## Engineering Practices

- **CI/CD:** GitHub Actions runs the test suite automatically on every push (`test_predict.py`, `test_env.py`)
- **Deep learning:** Visual irregularity detection combines OpenCV heuristics with MobileNetV2 (TensorFlow) transfer-learned features

---

## Installation & Execution

### 1. Clone and install dependencies

```bash
git clone https://github.com/VidhanGupta-01/smart-care.git
cd smart-care
pip install -r requirements.txt
```

### 2. Run the app

```bash
streamlit run app.py
```

This opens a two-tab interface:
- **🧍 Single Patient Assessment** — original ML-based intake form (vitals, symptoms, optional EHR upload, multilingual: English/Hindi/Tamil)
- **🚑 Live Queue (Multi-Patient)** — the new queue-aware engine: admit patients, advance the simulated clock, trigger a 3× surge, view live rankings, and submit clinician overrides

### 3. Run the standalone scenario demonstration

To see all required Round 2 behaviors run end-to-end in the terminal (normal load, worsening vitals, override, and 3× surge):

```bash
python simulate_scenarios.py
```

### 4. Retrain or benchmark the ML model (optional)

```bash
python compare_models.py                    # benchmark all models
python train_model.py --model adaboost      # retrain production model
```

---

## Tech Stack

| Layer | Tools |
|---|---|
| App | Streamlit |
| ML | scikit-learn (AdaBoost), XGBoost, LightGBM (benchmarked) |
| Queue engine | Pure Python, rule-based, no external ML dependency |
| Data | Pandas, NumPy |
| Document / Vision | pdfplumber, OpenCV, Pillow, TensorFlow (MobileNetV2 transfer learning) |
| Reporting | Excel (openpyxl), Power BI, SQLite |

---

## Safety & Ethics

- No disease diagnosis or treatment recommendations
- No replacement for licensed clinical judgment — every recommendation is reviewable and overridable
- Synthetic/simulated data only — no real patient data used
- Deliberately biased toward escalation under uncertainty, not average-case accuracy
- Audit trail is append-only — nothing is silently overwritten or deleted

---

## Future Scope

- Multilingual support extended to the queue view (currently English-only; single-patient tab supports Hindi/Tamil)
- Formal role-based access control and encryption at rest for the audit log
- Integration with hospital bed management and staff rostering systems
- Full 5-level ESI triage scale option
- Retraining the ML model itself on age-stratified data, rather than layering a rule-based cross-check on top

---

## Author

**Vidhan Gupta**
NIT Tiruchirappalli — Accenture Innovation Challenge 2026
