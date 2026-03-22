# Extraído de: LibroDevSecOps/cap-11-remediacion-automatica.md
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class RemediationMetrics:
    """Métricas del agente de remediación por ciclo."""
    total_findings_received: int = 0
    auto_fixes_generated: int = 0
    advisory_prs_generated: int = 0
    excluded_by_policy: int = 0
    fixes_merged: int = 0
    fixes_rejected: int = 0
    fixes_pending_review: int = 0
    avg_confidence: float = 0.0
    total_tokens_used: int = 0
    cost_usd: float = 0.0
    duration_seconds: float = 0.0

    @property
    def fix_acceptance_rate(self) -> float:
        """Tasa de aceptación: fixes merged / generados."""
        total = self.fixes_merged + self.fixes_rejected
        if total == 0:
            return 0.0
        return self.fixes_merged / total

    @property
    def mttr_reduction_ratio(self) -> float:
        """Ratio de reducción de MTTR estimado."""
        # MTTR manual: 42 días (SCA), 28 días (SAST)
        # MTTR con agente: 3 días (review + merge)
        manual_avg = 35.0  # días
        agent_avg = 3.0    # días
        return 1 - (agent_avg / manual_avg)

    def summary(self) -> str:
        return (
            f"Hallazgos: {self.total_findings_received} | "
            f"Auto-fix: {self.auto_fixes_generated} | "
            f"Advisory: {self.advisory_prs_generated} | "
            f"Excluidos: {self.excluded_by_policy} | "
            f"Aceptación: {self.fix_acceptance_rate:.0%} | "
            f"Coste: ${self.cost_usd:.2f}"
        )
