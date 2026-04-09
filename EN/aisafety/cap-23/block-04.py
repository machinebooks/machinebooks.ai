# Extracted from: LibroAISafety/ch-23-safety-program.md
@dataclass
class ProgramKPIs:
    """Operational KPIs for the AI Safety program."""
    period: str  # e.g., "2026-Q2"
    
    # Detection
    mttd_hours_ai_incidents: float
    
    # Control effectiveness
    guardrail_effectiveness_pct: float
    guardrail_total_interactions: int
    
    # Coverage
    systems_critical_covered_pct: float
    systems_high_covered_pct: float
    systems_medium_covered_pct: float
    
    # Red teaming
    red_team_evaluations_completed: int
    red_team_evaluations_planned: int
    
    # Training
    training_level1_completion_pct: float
    training_level2_completion_pct: float
    
    # Prevention
    findings_pre_production: int
    findings_in_production: int
    
    @property
    def prevention_ratio(self) -> float:
        total = self.findings_pre_production + self.findings_in_production
        return self.findings_pre_production / total if total > 0 else 0.0
    
    @property
    def guardrail_failures_per_day(self) -> float:
        """Estimated number of unblocked interactions per day."""
        failure_rate = 1 - (self.guardrail_effectiveness_pct / 100)
        return self.guardrail_total_interactions * failure_rate / 90  # quarter
