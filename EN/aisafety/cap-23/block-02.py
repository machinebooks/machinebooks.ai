# Extracted from: LibroAISafety/ch-23-safety-program.md
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class Finding(Enum):
    CRITICAL = "critical"  # must be fixed before deployment
    HIGH = "high"          # must be fixed within 7 days
    MEDIUM = "medium"      # must be fixed within 30 days
    LOW = "low"            # recommended improvement
    INFO = "info"          # observation with no risk

@dataclass
class SecurityEvaluation:
    """Security evaluation of an AI system."""
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
        """A system is deployable if it has no critical findings."""
        return not any(
            f["severity"] == "critical" for f in self.findings
        )

# Evaluation checklist -- mandatory categories
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
