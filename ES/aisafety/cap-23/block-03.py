# Extraido de: LibroAISafety/cap-23-programa-safety.md
@dataclass
class MonthlyReport:
    """Informe mensual del programa de AI Safety para dirección."""
    month: str
    total_ai_systems: int
    systems_with_current_review: int
    incidents_critical: int
    incidents_high: int
    incidents_medium: int
    incidents_low: int
    avg_containment_hours: float
    vulns_found_pre_production: int
    vulns_found_in_production: int
    red_team_evaluations_completed: int
    training_sessions_delivered: int

    @property
    def coverage_pct(self) -> float:
        return (self.systems_with_current_review / self.total_ai_systems) * 100

    @property
    def prevention_ratio(self) -> float:
        """Ratio de vulnerabilidades encontradas antes de producción."""
        total = self.vulns_found_pre_production + self.vulns_found_in_production
        if total == 0:
            return 0.0
        return self.vulns_found_pre_production / total

    def executive_summary(self) -> str:
        return (
            f"Cobertura: {self.coverage_pct:.0f}% | "
            f"Incidentes críticos: {self.incidents_critical} | "
            f"Prevención: {self.prevention_ratio:.0%} hallazgos en pre-prod | "
            f"Contención media: {self.avg_containment_hours:.1f}h"
        )
