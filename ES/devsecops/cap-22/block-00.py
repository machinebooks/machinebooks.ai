# Extraído de: LibroDevSecOps/cap-22-compliance-continuo.md
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class ComplianceStatus(Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIAL = "partial"
    NOT_ASSESSED = "not_assessed"


class EvidenceSource(Enum):
    SAST_SCAN = "sast_scan"           # Semgrep
    SCA_SCAN = "sca_scan"             # Grype
    CONTAINER_SCAN = "container_scan"  # Trivy
    SECRET_SCAN = "secret_scan"       # Gitleaks
    POLICY_CHECK = "policy_check"     # OPA
    CI_GATE = "ci_gate"               # GitHub Actions gate
    CODE_REVIEW = "code_review"       # PR review aprobado
    AGENT_AUDIT = "agent_audit"       # Agente Claude


@dataclass
class Control:
    """Un control normativo de cualquier framework."""
    framework: str        # "ISO27001", "ENS", "SOC2"
    control_id: str       # "A.8.9", "op.exp.3", "CC6.1"
    title: str
    description: str
    category: str         # "technical", "organizational", "physical"
    evidence_sources: list[EvidenceSource] = field(default_factory=list)
    automation_level: str = "full"  # "full", "partial", "manual"


@dataclass
class Evidence:
    """Una evidencia generada por el pipeline."""
    source: EvidenceSource
    timestamp: datetime
    artifact_path: str    # Ruta al artefacto en el repositorio
    pipeline_run_id: str
    commit_sha: str
    summary: str          # Resumen legible del resultado
    passed: bool          # Si el check fue exitoso
    metadata: dict = field(default_factory=dict)


@dataclass
class ControlAssessment:
    """Evaluación de un control en un momento dado."""
    control: Control
    status: ComplianceStatus
    evidences: list[Evidence]
    assessed_at: datetime
    assessed_by: str      # "pipeline", "agent:compliance", "human:jperez"
    justification: str
    next_review: Optional[datetime] = None
