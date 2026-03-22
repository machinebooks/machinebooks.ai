# Source: The DevSecOps and the Machine -- Chapter 22
# Pattern: Continuous compliance evaluation and audit preparation

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

import anthropic
import json
from datetime import datetime

client = anthropic.Anthropic()

def generate_compliance_report(
    framework: str,
    assessments: list[dict],
    period_start: str,
    period_end: str
) -> str:
    """Genera informe de compliance para auditoría."""

    compliant = [a for a in assessments if a["status"] == "compliant"]
    non_compliant = [a for a in assessments if a["status"] == "non_compliant"]
    partial = [a for a in assessments if a["status"] == "partial"]

    prompt = f"""Genera un informe de compliance para auditoría de {framework}.

Periodo: {period_start} a {period_end}
Total de controles evaluados: {len(assessments)}
Conformes: {len(compliant)}
No conformes: {len(non_compliant)}
Parciales: {len(partial)}

Controles no conformes (requieren atención):
{json.dumps(non_compliant, indent=2, default=str)}

Controles parciales:
{json.dumps(partial, indent=2, default=str)}

Genera el informe con esta estructura:
1. Resumen ejecutivo (estado general, tendencia, riesgos principales)
2. Estado por control (tabla con control, estado, evidencia, observaciones)
3. Controles no conformes (detalle, impacto, plan de remediación sugerido)
4. Recomendaciones (priorizadas por impacto)

El informe debe ser formal, preciso y apto para presentar a un auditor.
No inventes datos ni evidencias que no estén en el contexto proporcionado."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text