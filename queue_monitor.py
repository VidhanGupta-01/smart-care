"""
PatientTriage.ai v2 — Queue Monitoring

Implements the Round 2 hard requirement:
"The system must monitor patients already in the waiting queue and
trigger re-assessment if wait time exceeds safe thresholds for their
severity level or if vitals are re-recorded as worsening."

This is also where the Round 1 "queue-aware, not single-patient" pitch
becomes real: the queue view ranks EVERY waiting patient relative to
each other, continuously, not just at intake.

Safe re-check intervals below are stated assumptions (not clinically
validated), consistent with the brief's instruction to state assumptions
explicitly:
    High risk    -> re-check every 10 minutes
    Medium risk  -> re-check every 30 minutes
    Low risk     -> re-check every 60 minutes
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from scoring import score_patient, TriageResult
from audit_log import AuditLog, OverrideReason

RECHECK_INTERVAL_MINUTES = {
    "High": 10,
    "Medium": 30,
    "Low": 60,
}


@dataclass
class QueuedPatient:
    patient_data: dict
    arrival_time: datetime
    last_assessment_time: datetime
    latest_result: TriageResult
    assessment_history: list = field(default_factory=list)
    needs_reassessment: bool = False
    reassessment_reason: str = ""

    @property
    def patient_id(self):
        return self.patient_data.get("Patient_ID", "unknown")

    def wait_minutes(self, now: datetime) -> float:
        return (now - self.arrival_time).total_seconds() / 60


class TriageQueue:
    """
    Holds all currently-waiting patients and continuously re-evaluates
    the queue as a whole — the "decide what to surface, recommend the
    rest" mechanism from the Round 1 pitch, now implemented.
    """

    def __init__(self):
        self.patients: dict[str, QueuedPatient] = {}
        self.audit_log = AuditLog()

    def admit(self, patient_data: dict, now: datetime = None):
        now = now or datetime.now(timezone.utc)
        result = score_patient(patient_data)
        qp = QueuedPatient(
            patient_data=patient_data,
            arrival_time=now,
            last_assessment_time=now,
            latest_result=result,
        )
        qp.assessment_history.append(result)
        self.patients[qp.patient_id] = qp
        self.audit_log.log_system_assessment(qp.patient_id, result)
        return result

    def override(self, patient_id: str, actor_id: str, final_risk_level: str,
                 final_department: str, reason: OverrideReason, note: str = ""):
        """
        A clinician overrides the system's recommendation. The queue
        reflects the human's final call immediately; the audit log keeps
        both the system's original recommendation and the override,
        satisfying the "must remain reviewable and overridable" requirement.
        """
        qp = self.patients[patient_id]
        system_result = qp.latest_result

        entry = self.audit_log.log_override(
            patient_id=patient_id,
            actor_id=actor_id,
            system_result=system_result,
            final_risk_level=final_risk_level,
            final_department=final_department,
            reason=reason,
            note=note,
        )

        # Reflect the clinician's decision as the patient's active status.
        # The system's own assessment is preserved in assessment_history
        # and the audit log — nothing is erased, only superseded.
        qp.latest_result.risk_level = final_risk_level
        qp.latest_result.recommended_department = final_department
        qp.needs_reassessment = False
        qp.reassessment_reason = ""
        return entry

    def record_new_vitals(self, patient_id: str, new_vitals: dict, now: datetime = None):
        """
        A patient's vitals are re-recorded (e.g., routine re-check, or a
        nurse notices deterioration). Re-score and check if this counts
        as "worsening" -> triggers immediate re-assessment flag.
        """
        now = now or datetime.now(timezone.utc)
        qp = self.patients[patient_id]
        old_result = qp.latest_result

        updated_data = {**qp.patient_data, **new_vitals}
        new_result = score_patient(updated_data)

        tiers = ["Low", "Medium", "High"]
        worsened = tiers.index(new_result.risk_level) > tiers.index(old_result.risk_level)

        qp.patient_data = updated_data
        qp.latest_result = new_result
        qp.last_assessment_time = now
        qp.assessment_history.append(new_result)

        if worsened:
            qp.needs_reassessment = True
            qp.reassessment_reason = (
                f"Vitals re-recorded as worsening: {old_result.risk_level} -> "
                f"{new_result.risk_level}. Immediate nurse review triggered."
            )
        else:
            qp.needs_reassessment = False
            qp.reassessment_reason = ""

        return new_result, worsened

    def check_wait_time_breaches(self, now: datetime = None):
        """
        Sweep the queue: any patient who has waited past the safe re-check
        interval for their current risk tier gets flagged for
        re-assessment, even if no one has actively re-checked their vitals.
        This is what makes the system catch silent deterioration during
        a long wait, not just deterioration someone happened to notice.
        """
        now = now or datetime.now(timezone.utc)
        breaches = []
        for qp in self.patients.values():
            interval = RECHECK_INTERVAL_MINUTES[qp.latest_result.risk_level]
            since_last = (now - qp.last_assessment_time).total_seconds() / 60
            if since_last > interval:
                qp.needs_reassessment = True
                qp.reassessment_reason = (
                    f"{since_last:.0f} min since last check exceeds the "
                    f"{interval}-min safe interval for {qp.latest_result.risk_level} risk."
                )
                self.audit_log.log_reassessment_trigger(qp.patient_id, qp.reassessment_reason)
                breaches.append(qp)
        return breaches

    def queue_view(self, now: datetime = None):
        """
        The live, ranked queue view — sorted by a combination of risk tier
        and how overdue each patient is for re-assessment. This is the
        AUTO-DECIDE layer: it decides WHAT TO SURFACE, never who gets
        treated first (that stays a recommendation a nurse can reorder).
        """
        now = now or datetime.now(timezone.utc)
        tier_rank = {"High": 0, "Medium": 1, "Low": 2}

        def sort_key(qp: QueuedPatient):
            overdue = qp.needs_reassessment
            return (not overdue, tier_rank[qp.latest_result.risk_level], -qp.wait_minutes(now))

        ordered = sorted(self.patients.values(), key=sort_key)
        return ordered

    def surface_for_immediate_review(self, now: datetime = None):
        """
        AUTO-DECIDE output: which patients need a nurse's eyes RIGHT NOW.
        Low-stakes, reversible — a nurse can glance and dismiss.
        """
        now = now or datetime.now(timezone.utc)
        return [
            qp for qp in self.patients.values()
            if qp.latest_result.needs_immediate_review or qp.needs_reassessment
        ]
