# Extraído de: LibroDevSecOps/cap-22-compliance-continuo.md
from dataclasses import dataclass


@dataclass
class ComplianceDrift:
    """Representa un cambio en el estado de un control."""
    control_id: str
    framework: str
    previous_status: ComplianceStatus
    current_status: ComplianceStatus
    detected_at: datetime
    cause: str
    severity: str  # "critical", "high", "medium", "low"


class DriftDetector:
    """Detecta cambios en el estado de compliance entre evaluaciones."""

    SEVERITY_MAP = {
        (ComplianceStatus.COMPLIANT, ComplianceStatus.NON_COMPLIANT): "critical",
        (ComplianceStatus.COMPLIANT, ComplianceStatus.PARTIAL): "high",
        (ComplianceStatus.PARTIAL, ComplianceStatus.NON_COMPLIANT): "high",
        (ComplianceStatus.NON_COMPLIANT, ComplianceStatus.COMPLIANT): "info",
        (ComplianceStatus.PARTIAL, ComplianceStatus.COMPLIANT): "info",
    }

    def detect(
        self,
        previous: list[ControlAssessment],
        current: list[ControlAssessment],
    ) -> list[ComplianceDrift]:
        """Compara dos evaluaciones y detecta derivas."""
        prev_map = {
            a.control.control_id: a for a in previous
        }
        drifts = []

        for assessment in current:
            cid = assessment.control.control_id
            prev = prev_map.get(cid)

            if prev and prev.status != assessment.status:
                severity = self.SEVERITY_MAP.get(
                    (prev.status, assessment.status), "medium"
                )
                drifts.append(ComplianceDrift(
                    control_id=cid,
                    framework=assessment.control.framework,
                    previous_status=prev.status,
                    current_status=assessment.status,
                    detected_at=assessment.assessed_at,
                    cause=assessment.justification,
                    severity=severity,
                ))

        return drifts
