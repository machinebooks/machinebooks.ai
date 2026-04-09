# Extraido de: LibroAISafety/cap-23-programa-safety.md
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class Finding(Enum):
    CRITICAL = "critical"  # debe corregirse antes de despliegue
    HIGH = "high"          # debe corregirse en 7 días
    MEDIUM = "medium"      # debe corregirse en 30 días
    LOW = "low"            # mejora recomendada
    INFO = "info"          # observación sin riesgo

@dataclass
class SecurityEvaluation:
    """Evaluación de seguridad de un sistema de IA."""
    system_id: str
    evaluator: str
    date: datetime
    findings: list[dict] = field(default_factory=list)

    def add_finding(self, category: str, severity: Finding,
                    description: str, recommendation: str):
        self.findings.append({
            "category": category,
            "severity": severity.value,
            "description": description,
            "recommendation": recommendation,
        })

    def is_deployable(self) -> bool:
        """Un sistema es desplegable si no tiene findings critical."""
        return not any(
            f["severity"] == "critical" for f in self.findings
        )

# Checklist de evaluación — categorías obligatorias
EVAL_CATEGORIES = [
    "prompt_injection_resistance",
    "system_prompt_leakage",
    "pii_handling",
    "tool_use_permissions",
    "output_filtering",
    "cross_tenant_isolation",
    "rate_limiting",
    "logging_and_audit",
    "incident_response_plan",
    "model_update_process",
]
