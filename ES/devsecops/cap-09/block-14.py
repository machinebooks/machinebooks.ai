# Extraído de: LibroDevSecOps/cap-09-agente-triaje.md
@dataclass
class TriageMetrics:
    """Métricas de calidad del agente de triaje."""
    total_findings: int
    agreement_rate: float      # 0.0 - 1.0
    false_negative_rate: float # 0.0 - 1.0
    triage_duration_seconds: float
    total_tokens_used: int
    cost_usd: float

    @property
    def cost_per_finding(self) -> float:
        if self.total_findings == 0:
            return 0.0
        return self.cost_usd / self.total_findings

    def is_healthy(self) -> bool:
        """Verifica que las métricas están dentro de umbrales."""
        return (
            self.agreement_rate >= 0.90
            and self.false_negative_rate <= 0.03
            and self.cost_per_finding <= 0.002
        )
