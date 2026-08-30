"""
Age-stratified vital sign thresholds for PatientTriage.ai v2.

Round 2 brief explicitly flags this as a required fix:
"Vital sign thresholds and symptom weights differ significantly across
pediatric, adult, and geriatric populations — a fever of 38.5C carries
different clinical urgency in a 3-year-old versus a 75-year-old.
Solutions that apply a single adult-calibrated scoring model across all
age groups introduce silent safety risk."

Age bands (broadly aligned with standard pediatric/adult/geriatric triage
conventions — simplified for prototype purposes, clearly stated as an
assumption in the README):
    Pediatric : 0–12 years
    Adolescent: 13–17 years
    Adult     : 18–64 years
    Geriatric : 65+ years

All thresholds below are illustrative reference ranges assembled for
prototype purposes, not clinically validated values — this is stated
explicitly in the README/business proposal as an assumption.
"""

from dataclasses import dataclass


@dataclass
class VitalThresholds:
    hr_high: float          # heart rate (bpm) above which is concerning
    hr_low: float           # heart rate below which is concerning
    sbp_high: float         # systolic BP (mmHg) above which is concerning
    sbp_low: float          # systolic BP below which is concerning (hypotension)
    temp_high: float        # temperature (F) above which is concerning
    resp_high: float        # respiratory rate (breaths/min) above which is concerning


AGE_BANDS = {
    "pediatric":  (0, 12),
    "adolescent": (13, 17),
    "adult":      (18, 64),
    "geriatric":  (65, 130),
}

THRESHOLDS = {
    # Children have naturally higher HR/RR and lower BP than adults —
    # applying adult thresholds here would systematically under-triage them.
    "pediatric": VitalThresholds(
        hr_high=140, hr_low=70, sbp_high=120, sbp_low=80,
        temp_high=100.4, resp_high=30,
    ),
    "adolescent": VitalThresholds(
        hr_high=120, hr_low=60, sbp_high=135, sbp_low=85,
        temp_high=100.9, resp_high=24,
    ),
    "adult": VitalThresholds(
        hr_high=110, hr_low=50, sbp_high=150, sbp_low=90,
        temp_high=101.0, resp_high=22,
    ),
    # Geriatric patients often run lower baseline temps and blunted fever
    # response — a "normal-looking" temp can still indicate serious
    # infection. Also more sensitive to tachycardia/hypotension.
    "geriatric": VitalThresholds(
        hr_high=100, hr_low=55, sbp_high=160, sbp_low=100,
        temp_high=100.0, resp_high=20,
    ),
}


def get_age_band(age: int) -> str:
    for band, (lo, hi) in AGE_BANDS.items():
        if lo <= age <= hi:
            return band
    return "adult"  # fallback, should not happen given band coverage


def get_thresholds(age: int) -> VitalThresholds:
    return THRESHOLDS[get_age_band(age)]


def vital_risk_flags(age: int, heart_rate: float, systolic_bp: float,
                      temperature: float, resp_rate: float = None) -> dict:
    """
    Returns which vitals are flagged as abnormal for this patient's age band,
    instead of applying one fixed adult rule to everyone.
    """
    band = get_age_band(age)
    th = THRESHOLDS[band]

    flags = {
        "age_band": band,
        "hr_flag": heart_rate > th.hr_high or heart_rate < th.hr_low,
        "sbp_flag": systolic_bp > th.sbp_high or systolic_bp < th.sbp_low,
        "temp_flag": temperature > th.temp_high,
    }
    if resp_rate is not None:
        flags["resp_flag"] = resp_rate > th.resp_high

    return flags
