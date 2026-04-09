# Extracted from: LibroAISafety/ch-23-safety-program.md
@dataclass
class MonthlyReport:
    """Monthly AI Safety program report for leadership."""
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
        """Ratio of vulnerabilities found before production."""
        total = self.vulns_found_pre_production + self.vulns_found_in_production
        if total == 0:
            return 0.0
        return self.vulns_found_pre_production / total

    def executive_summary(self) -> str:
        return (
            f"Coverage: {self.coverage_pct:.0f}% | "
            f"Critical incidents: {self.incidents_critical} | "
            f"Prevention: {self.prevention_ratio:.0%} findings in pre-prod | "
            f"Mean containment: {self.avg_containment_hours:.1f}h"
        )
