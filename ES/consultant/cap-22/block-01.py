# Extraído de: LibroConsultor/cap-22-unit-economics.md
@dataclass
class AugmentedEconomics:
    """Motor de cálculo de unit economics del consultor aumentado."""
    baseline: ConsultantProfile
    ai_cost: AIStackCost
    compression_factor: float = 0.52    # FCE: 52% reducción de esfuerzo
    price_retention: float = 0.80       # FAP: retiene 80% del precio
    capacity_conversion: float = 0.60   # CI: 60% del tiempo liberado se factura
    year: int = 1

    @property
    def hours_saved_per_project(self) -> float:
        """Horas ahorradas por proyecto medio."""
        avg_project_hours = self.baseline.billable_hours / self._baseline_projects
        return avg_project_hours * self.compression_factor

    @property
    def _baseline_projects(self) -> float:
        """Número estimado de proyectos anuales en modelo tradicional."""
        avg_project_hours = 120  # Horas medias por proyecto
        return self.baseline.billable_hours / avg_project_hours

    @property
    def augmented_hours_per_project(self) -> float:
        """Horas requeridas por proyecto con IA."""
        return 120 * (1 - self.compression_factor)

    @property
    def augmented_projects(self) -> float:
        """Proyectos completados con modelo aumentado."""
        freed_hours = self.baseline.billable_hours * self.compression_factor
        additional_billable = freed_hours * self.capacity_conversion
        total_hours = (self.baseline.billable_hours
                       - freed_hours + additional_billable + freed_hours)
        return total_hours / self.augmented_hours_per_project

    @property
    def augmented_revenue_per_project(self) -> float:
        """Ingreso por proyecto con modelo aumentado."""
        baseline_revenue_per_project = 120 * self.baseline.avg_bill_rate
        return baseline_revenue_per_project * self.price_retention

    @property
    def augmented_annual_revenue(self) -> float:
        """Facturación anual del consultor aumentado."""
        return self.augmented_projects * self.augmented_revenue_per_project

    @property
    def augmented_total_cost(self) -> float:
        """Coste total incluyendo IA."""
        return self.baseline.loaded_cost + self.ai_cost.total_year(self.year)

    @property
    def augmented_gross_margin(self) -> float:
        return self.augmented_annual_revenue - self.augmented_total_cost

    @property
    def augmented_margin_pct(self) -> float:
        if self.augmented_annual_revenue == 0:
            return 0
        return self.augmented_gross_margin / self.augmented_annual_revenue

    @property
    def roi_on_ai_investment(self) -> float:
        """ROI de la inversión en IA."""
        incremental_margin = self.augmented_gross_margin - self.baseline.gross_margin
        ai_investment = self.ai_cost.total_year(self.year)
        return incremental_margin / ai_investment if ai_investment > 0 else 0

    @property
    def breakeven_days(self) -> float:
        """Días para alcanzar break-even de la inversión en IA."""
        daily_incremental = (
            (self.augmented_gross_margin - self.baseline.gross_margin) / 365
        )
        if daily_incremental <= 0:
            return float('inf')
        return self.ai_cost.total_year(self.year) / daily_incremental
