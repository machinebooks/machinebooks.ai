# Extraído de: LibroConsultor/cap-22-unit-economics.md
from dataclasses import dataclass, field
from typing import Optional
import json

@dataclass
class ConsultantProfile:
    """Perfil económico de un consultor individual."""
    name: str
    annual_salary: float          # Salario bruto anual
    loaded_cost: float            # Coste cargado (salario + SS + overhead)
    available_hours: int = 1760   # Horas disponibles al año
    target_utilization: float = 0.75
    actual_utilization: float = 0.67
    avg_bill_rate: float = 105.0  # Tarifa media por hora

    @property
    def billable_hours(self) -> int:
        return int(self.available_hours * self.actual_utilization)

    @property
    def annual_revenue(self) -> float:
        return self.billable_hours * self.avg_bill_rate

    @property
    def gross_margin(self) -> float:
        return self.annual_revenue - self.loaded_cost

    @property
    def gross_margin_pct(self) -> float:
        return self.gross_margin / self.annual_revenue if self.annual_revenue > 0 else 0


@dataclass
class AIStackCost:
    """Costes del stack de IA por consultor."""
    api_licenses_monthly: float = 100.0    # Claude API
    rag_infra_monthly: float = 30.0        # Qdrant + compute
    tools_monthly: float = 20.0            # Pandoc, CI, etc.
    first_year_training: float = 3200.0    # Formación
    first_year_setup: float = 2800.0       # Configuración inicial

    @property
    def monthly_recurring(self) -> float:
        return self.api_licenses_monthly + self.rag_infra_monthly + self.tools_monthly

    @property
    def annual_recurring(self) -> float:
        return self.monthly_recurring * 12

    def total_year(self, year: int = 1) -> float:
        """Coste total para un año dado."""
        base = self.annual_recurring
        if year == 1:
            base += self.first_year_training + self.first_year_setup
        return base
