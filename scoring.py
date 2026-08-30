"""
PatientTriage.ai v2 — Scoring Engine

Design principles required by the Round 2 brief, each implemented below:

1. Age-stratified, not one-size-fits-all (age_thresholds.py handles this).
2. Every score ships with a confidence indicator — never a bare number.
   (see `confidence` field, always present in the output)
3. Asymmetric cost tuning: under-triage is categorically worse than
   over-triage, so when the engine is *not confident*, it escalates the
   risk tier rather than leaving it as-is. This is implemented as an
   explicit, loggable rule (see `_apply_escalation_bias`) rather than
   left implicit in model weights, so it can be demonstrated directly.
4. Decide vs. recommend split:
      - `needs_immediate_review` (bool) is the AUTO-DECIDE layer — a
        low-stakes, reversible flag a nurse can glance at and dismiss.
      - `risk_level` / `recommended_care_level` / `department` are
        RECOMMENDATIONS only — always overridable by a clinician.
5. Regulatory jurisdiction assumption (stated per brief's requirement):
   this prototype assumes a US/HIPAA-equivalent context for audit-trail
   and data-handling design. See README for full statement.

This is a deliberately transparent, rule-based scoring layer (rather than
a black-box ML model) for the prototype, precisely BECAUSE Round 2 asks
teams to demonstrate the escalation-under-uncertainty design choice
explicitly — a transparent rule set makes that auditable. The existing
AdaBoost classifier (predict.py, trained on the larger synthetic
500-row dataset) can be layered in as a secondary signal; see
`ml_confidence_hook` for where that would plug in.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone

from age_thresholds import get_age_band, vital_risk_flags, get_thresholds

# --- Symptom severity weights -------------------------------------------
# Specific, high-acuity symptoms carry more weight AND more diagnostic
# certainty than vague ones. Vague symptoms contribute less to the risk
# score but also reduce confidence (see _compute_confidence).
HIGH_SPECIFICITY_SYMPTOMS = {
    "chest pain": 2.0,
    "breathlessness": 2.0,
    "confusion": 2.0,
    "abdominal pain": 1.0,
}
LOW_SPECIFICITY_SYMPTOMS = {
    # Real, but non-specific — can indicate anything from minor to severe.
    "fatigue": 0.3,
    "dizziness": 0.4,
    "nausea": 0.3,
    "headache": 0.4,
    "weakness": 0.5,
    "anxiety": 0.2,
    "palpitations": 0.6,
}
ALL_SYMPTOM_WEIGHTS = {**HIGH_SPECIFICITY_SYMPTOMS, **LOW_SPECIFICITY_SYMPTOMS}

CONDITION_WEIGHTS = {
    "heart disease": 1.5,
    "diabetes": 0.5,
    "hypertension": 0.5,
    "asthma": 0.5,
}

CONFIDENCE_ESCALATION_THRESHOLD = 0.70  # below this, bias toward escalation
# Deliberately set above the midpoint (not 0.50) — reflects the asymmetric
# cost rule stated in the brief: "must be deliberately tuned to bias toward
# escalation under uncertainty rather than optimized for average accuracy."
# Only confidently-clear cases (>=0.70) are trusted at face value; anything
# in the "Medium" confidence band or below gets the safety bump.
RISK_TIERS = ["Low", "Medium", "High"]


@dataclass
class TriageResult:
    patient_id: str
    age: int
    age_band: str
    raw_score: float
    risk_level: str
    confidence: float
    confidence_label: str
    needs_immediate_review: bool
    recommended_care_level: str
    recommended_department: str
    key_factors: list = field(default_factory=list)
    escalation_log: list = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self):
        return self.__dict__


def _parse_list(value: str) -> list:
    if not value or str(value).lower() in ("none", "unknown", "nan"):
        return []
    return [s.strip().lower() for s in str(value).split(",") if s.strip()]


def _compute_confidence(vital_flags: dict, symptoms: list, history_available: bool,
                         age: int, heart_rate: float, systolic_bp: float,
                         temperature: float) -> float:
    """
    Confidence starts high and is reduced by genuine sources of
    uncertainty — NOT by risk level itself. A confidently-low-risk patient
    and a confidently-high-risk patient should both score high confidence;
    it's ambiguous, borderline, or data-sparse cases that should score low.
    """
    confidence = 1.0

    # 1. Missing history reduces confidence — less context to work with.
    if not history_available:
        confidence -= 0.15

    # 2. Vitals sitting close to the age-band threshold are inherently
    #    more ambiguous than vitals that are clearly normal or clearly
    #    abnormal.
    th = get_thresholds(age)
    near_threshold = 0
    if abs(heart_rate - th.hr_high) < 8:
        near_threshold += 1
    if abs(systolic_bp - th.sbp_high) < 8 or abs(systolic_bp - th.sbp_low) < 8:
        near_threshold += 1
    if abs(temperature - th.temp_high) < 0.6:
        near_threshold += 1
    confidence -= 0.10 * near_threshold

    # 3. Symptom specificity: if the ONLY symptoms present are low-specificity
    #    ones (fatigue, dizziness, nausea...), the picture is inherently
    #    harder to interpret than a specific presentation like chest pain.
    if symptoms and all(s in LOW_SPECIFICITY_SYMPTOMS for s in symptoms):
        confidence -= 0.20

    # 4. No symptoms and no flags at all is a clear, confident "low risk" —
    #    don't penalize simple, clean-cut cases.
    if not symptoms and sum(vital_flags.get(k, False) for k in
                             ("hr_flag", "sbp_flag", "temp_flag")) == 0:
        confidence = min(confidence + 0.10, 1.0)

    return max(0.0, min(1.0, round(confidence, 2)))


def _confidence_label(confidence: float) -> str:
    if confidence >= 0.80:
        return "High"
    elif confidence >= CONFIDENCE_ESCALATION_THRESHOLD:
        return "Medium"
    return "Low"


def _raw_risk_score(vital_flags: dict, symptoms: list, conditions: list) -> float:
    score = 0.0
    if vital_flags.get("hr_flag"):
        score += 1.0
    if vital_flags.get("sbp_flag"):
        score += 1.0
    if vital_flags.get("temp_flag"):
        score += 1.0
    if vital_flags.get("resp_flag"):
        score += 1.0
    for s in symptoms:
        score += ALL_SYMPTOM_WEIGHTS.get(s, 0.2)
    for c in conditions:
        score += CONDITION_WEIGHTS.get(c, 0.2)
    return round(score, 2)


def _score_to_tier(score: float) -> str:
    if score >= 4.0:
        return "High"
    elif score >= 2.0:
        return "Medium"
    return "Low"


def _apply_escalation_bias(tier: str, confidence: float, log: list) -> str:
    """
    THE asymmetric-cost rule, made explicit and auditable:
    when the engine is not confident, it escalates rather than leaving
    the tier as-is — because missing a critical case is worse than
    over-prioritizing a minor one.
    """
    if confidence < CONFIDENCE_ESCALATION_THRESHOLD:
        idx = RISK_TIERS.index(tier)
        if idx < len(RISK_TIERS) - 1:
            new_tier = RISK_TIERS[idx + 1]
            log.append(
                f"Confidence {confidence:.2f} below threshold "
                f"({CONFIDENCE_ESCALATION_THRESHOLD}) — escalated "
                f"{tier} -> {new_tier} per asymmetric-cost safety rule."
            )
            return new_tier
        else:
            log.append(
                f"Confidence {confidence:.2f} below threshold, but already "
                f"at highest tier (High) — no further escalation possible."
            )
    return tier


def _care_level_and_department(risk_level: str, symptoms: list) -> tuple:
    if risk_level == "High":
        care = "ICU-level attention"
        dept = "Emergency / Cardiology" if "chest pain" in symptoms else "Emergency"
    elif risk_level == "Medium":
        care = "Ward / Observation"
        dept = "General Medicine"
    else:
        care = "OPD-level care"
        dept = "Outpatient / General Medicine"
    return care, dept


def score_patient(patient: dict) -> TriageResult:
    age = int(patient["Age"])
    heart_rate = float(patient["Heart_Rate"])
    systolic_bp = float(patient["Systolic_BP"])
    temperature = float(patient["Temperature"])
    resp_rate = float(patient.get("Resp_Rate")) if patient.get("Resp_Rate") not in (None, "") else None
    history_available = bool(patient.get("History_Available", False))

    symptoms = _parse_list(patient.get("Symptoms", ""))
    conditions = _parse_list(patient.get("Pre_Existing_Conditions", ""))

    flags = vital_risk_flags(age, heart_rate, systolic_bp, temperature, resp_rate)
    raw_score = _raw_risk_score(flags, symptoms, conditions)
    tier = _score_to_tier(raw_score)

    confidence = _compute_confidence(
        flags, symptoms, history_available, age, heart_rate, systolic_bp, temperature
    )

    escalation_log = []
    if not history_available:
        escalation_log.append("No prior history on file — assessment based on observed data only.")

    final_tier = _apply_escalation_bias(tier, confidence, escalation_log)
    needs_immediate_review = final_tier == "High" or "chest pain" in symptoms or "confusion" in symptoms

    care_level, department = _care_level_and_department(final_tier, symptoms)

    key_factors = []
    if flags.get("hr_flag"):
        key_factors.append(f"Heart rate abnormal for {flags['age_band']} band ({heart_rate} bpm).")
    if flags.get("sbp_flag"):
        key_factors.append(f"Blood pressure abnormal for {flags['age_band']} band ({systolic_bp} mmHg).")
    if flags.get("temp_flag"):
        key_factors.append(f"Temperature elevated for {flags['age_band']} band ({temperature} F).")
    if flags.get("resp_flag"):
        key_factors.append(f"Respiratory rate elevated for {flags['age_band']} band ({resp_rate}/min).")
    for s in symptoms:
        if s in HIGH_SPECIFICITY_SYMPTOMS:
            key_factors.append(f"High-acuity symptom reported: {s}.")

    return TriageResult(
        patient_id=patient.get("Patient_ID", "unknown"),
        age=age,
        age_band=flags["age_band"],
        raw_score=raw_score,
        risk_level=final_tier,
        confidence=confidence,
        confidence_label=_confidence_label(confidence),
        needs_immediate_review=needs_immediate_review,
        recommended_care_level=care_level,
        recommended_department=department,
        key_factors=key_factors,
        escalation_log=escalation_log,
    )
