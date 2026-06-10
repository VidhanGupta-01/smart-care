-- Sample analyst SQL queries for Smart Care (portfolio / interview use)

-- 1. Risk distribution with percentages
SELECT * FROM vw_risk_distribution;

-- 2. Average vitals by risk level
SELECT * FROM vw_vitals_by_risk;

-- 3. High-risk patient profile
SELECT
    patient_id,
    age,
    gender,
    heart_rate,
    systolic_bp,
    temperature,
    symptoms,
    pre_existing_conditions
FROM patients
WHERE risk_level = 'High'
ORDER BY systolic_bp DESC;

-- 4. Patients with chest pain and their risk breakdown
SELECT
    risk_level,
    COUNT(*) AS patient_count
FROM patients
WHERE LOWER(symptoms) LIKE '%chest pain%'
GROUP BY risk_level;

-- 5. Gender vs risk cross-tab style result
SELECT * FROM vw_gender_risk
ORDER BY gender, risk_level;

-- 6. Elderly patients (60+) needing medium or high triage
SELECT
    COUNT(*) AS elderly_high_priority_count
FROM patients
WHERE age >= 60
  AND risk_level IN ('Medium', 'High');

-- 7. Top model from benchmarking table
SELECT
    model_name,
    cv_accuracy,
    test_accuracy
FROM model_benchmark
ORDER BY cv_accuracy DESC
LIMIT 1;

-- 8. Patients with elevated heart rate above cohort average
SELECT
    p.patient_id,
    p.heart_rate,
    p.risk_level,
    p.symptoms
FROM patients p
WHERE p.heart_rate > (SELECT AVG(heart_rate) FROM patients)
ORDER BY p.heart_rate DESC;
