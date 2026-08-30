"""
PatientTriage.ai v2 — Override Logging & Audit Trail

Round 2 requirements this satisfies:
- "Capture at least one clinician override and show what the system logs."
- "Clinical accountability and liability mean any recommendation must
   remain reviewable and overridable by a licensed clinician, with a
   clear audit trail and compliance with health-data regulation."
- "State your assumed regulatory jurisdiction... This affects your audit
   trail design, data retention policy, consent model, and what a
   clinician override must legally record."

STATED ASSUMPTION (per brief's explicit instruction to state this):
This prototype assumes a US-based deployment under HIPAA. Design choices
that follow from that assumption:
  - Every access to, or change of, a patient's triage record is logged
    with a timestamp and the acting clinician's identifier (minimum
    necessary standard).
  - Overrides must record WHO overrode, WHAT the system recommended vs.
    what was chosen, and WHY (reason code + optional free text) — this
    is the "accountable override" record a HIPAA-covered entity would
    need to produce under audit.
  - Audit records themselves are treated as retained health-adjacent
    metadata: append-only, never edited or deleted, consistent with
    HIPAA's audit-control requirement (45 CFR 164.312(b)).
  - This is a simplified illustrative implementation for prototype
    purposes — a production system would need encryption at rest,
    role-based access control, and formal retention-period policy,
    which are noted as future work in the README rather than built here.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class OverrideReason(Enum):
    CLINICAL_JUDGMENT = "clinical_judgment"       # nurse's direct assessment disagrees
    ADDITIONAL_INFO = "additional_info_available"  # info the system didn't have
    SYSTEM_ERROR_SUSPECTED = "system_error_suspected"
    PATIENT_REQUEST = "patient_or_family_request"
    OTHER = "other"


@dataclass
class AuditEntry:
    timestamp: str
    patient_id: str
    actor_id: str            # clinician/nurse identifier
    action: str               # e.g. "system_assessment", "override", "reassessment_view"
    system_recommendation: str = None
    final_decision: str = None
    override_reason: str = None
    override_note: str = None

    def to_dict(self):
        return self.__dict__


class AuditLog:
    """
    Append-only audit trail. Entries are never edited or deleted, per the
    HIPAA audit-control assumption stated above — this is enforced here
    by only exposing an `append` method, no update/delete.
    """

    def __init__(self):
        self._entries: list[AuditEntry] = []

    def log_system_assessment(self, patient_id: str, result):
        entry = AuditEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            patient_id=patient_id,
            actor_id="SYSTEM",
            action="system_assessment",
            system_recommendation=(
                f"{result.risk_level} | conf={result.confidence} | "
                f"{result.recommended_care_level} -> {result.recommended_department}"
            ),
        )
        self._entries.append(entry)
        return entry

    def log_override(self, patient_id: str, actor_id: str, system_result,
                      final_risk_level: str, final_department: str,
                      reason: OverrideReason, note: str = ""):
        """
        Records a clinician override. Both the system's original
        recommendation AND the human's final decision are captured, so
        the record shows exactly what was overridden and by how much —
        this is what makes the override auditable rather than just logged.
        """
        entry = AuditEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            patient_id=patient_id,
            actor_id=actor_id,
            action="override",
            system_recommendation=(
                f"{system_result.risk_level} -> {system_result.recommended_department}"
            ),
            final_decision=f"{final_risk_level} -> {final_department}",
            override_reason=reason.value,
            override_note=note,
        )
        self._entries.append(entry)
        return entry

    def log_reassessment_trigger(self, patient_id: str, trigger_reason: str):
        entry = AuditEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            patient_id=patient_id,
            actor_id="SYSTEM",
            action="reassessment_triggered",
            system_recommendation=trigger_reason,
        )
        self._entries.append(entry)
        return entry

    def history_for(self, patient_id: str):
        return [e for e in self._entries if e.patient_id == patient_id]

    def all_entries(self):
        return list(self._entries)  # defensive copy — caller can't mutate the log

    def override_rate(self) -> float:
        """
        A basic trust/monitoring metric: what fraction of system
        recommendations get overridden by clinicians? Tracked because
        the brief calls out "adoption & change management" — if this
        number is high, it's a signal the model needs retuning, or staff
        don't trust it, and that's worth surfacing rather than hiding.
        """
        assessments = [e for e in self._entries if e.action == "system_assessment"]
        overrides = [e for e in self._entries if e.action == "override"]
        if not assessments:
            return 0.0
        return round(len(overrides) / len(assessments), 3)
