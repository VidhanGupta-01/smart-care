-- Smart Care SQLite schema for analytics, SQL practice, and Power BI connectivity

CREATE TABLE IF NOT EXISTS patients (
    patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
    age INTEGER NOT NULL,
    gender TEXT NOT NULL,
    heart_rate INTEGER NOT NULL,
    systolic_bp INTEGER NOT NULL,
    temperature REAL NOT NULL,
    symptoms TEXT,
    pre_existing_conditions TEXT,
    risk_level TEXT NOT NULL CHECK (risk_level IN ('Low', 'Medium', 'High'))
);

CREATE TABLE IF NOT EXISTS patient_features (
    patient_id INTEGER PRIMARY KEY,
    age INTEGER NOT NULL,
    gender_encoded INTEGER NOT NULL,
    heart_rate INTEGER NOT NULL,
    systolic_bp INTEGER NOT NULL,
    temperature REAL NOT NULL,
    has_chest_pain INTEGER NOT NULL,
    has_fever INTEGER NOT NULL,
    has_heart_disease INTEGER NOT NULL,
    risk_level TEXT NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
);

CREATE TABLE IF NOT EXISTS model_benchmark (
    model_name TEXT PRIMARY KEY,
    cv_accuracy REAL NOT NULL,
    cv_std REAL NOT NULL,
    test_accuracy REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS triage_predictions (
    prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    predicted_risk TEXT NOT NULL,
    confidence_label TEXT,
    recommended_department TEXT,
    recommended_care_level TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
);

CREATE VIEW IF NOT EXISTS vw_risk_distribution AS
SELECT
    risk_level,
    COUNT(*) AS patient_count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM patients), 1) AS percentage
FROM patients
GROUP BY risk_level
ORDER BY CASE risk_level WHEN 'Low' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END;

CREATE VIEW IF NOT EXISTS vw_vitals_by_risk AS
SELECT
    risk_level,
    ROUND(AVG(age), 1) AS avg_age,
    ROUND(AVG(heart_rate), 1) AS avg_heart_rate,
    ROUND(AVG(systolic_bp), 1) AS avg_systolic_bp,
    ROUND(AVG(temperature), 1) AS avg_temperature,
    COUNT(*) AS patient_count
FROM patients
GROUP BY risk_level
ORDER BY CASE risk_level WHEN 'Low' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END;

CREATE VIEW IF NOT EXISTS vw_gender_risk AS
SELECT
    gender,
    risk_level,
    COUNT(*) AS patient_count
FROM patients
GROUP BY gender, risk_level;
