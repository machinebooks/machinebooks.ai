# Extraído de: LibroBugBounty/cap-28-economics-bounty.md
"""
bounty_roi_calculator.py -- Calculadora de ROI para bug bounty hunters
Calcula metricas de rentabilidad considerando severidad, duplicados,
rechazos, impuestos y coste de herramientas.
"""
from dataclasses import dataclass, field
from typing import Optional
import json

# Medianas de pago por severidad (HackerOne, 2024)
MEDIAN_PAYOUTS = {
    "critical": 3000,
    "high": 1000,
    "medium": 500,
    "low": 150,
}

# Tasas de impuestos por jurisdiccion (simplificado)
TAX_RATES = {
    "spain_autonomo": 0.30,  # IRPF estimacion + IVA neto
    "spain_empresa": 0.25,   # Impuesto de Sociedades
    "us_selfemployed": 0.35, # Federal + self-employment
    "eu_average": 0.28,      # Media UE para autonomos
}

@dataclass
class BountyReport:
    """Un report enviado a una plataforma."""
    vuln_id: str
    severity: str           # critical, high, medium, low
    platform: str           # hackerone, bugcrowd, direct
    hours_spent: float      # horas de investigacion
    status: str = "pending" # pending, accepted, duplicate, rejected
    payout: Optional[float] = None  # pago real (si se conoce)
    
    @property
    def estimated_payout(self) -> float:
        """Pago estimado si no se conoce el real."""
        if self.payout is not None:
            return self.payout
        if self.status in ("duplicate", "rejected"):
            return 0.0
        return MEDIAN_PAYOUTS.get(self.severity, 0)

@dataclass
class MonthlyROI:
    """Calculo de ROI mensual."""
    reports: list[BountyReport] = field(default_factory=list)
    tool_cost_monthly: float = 74.0  # nuestro coste real
    hours_total: float = 0.0
    tax_jurisdiction: str = "spain_autonomo"
    
    def add_report(self, report: BountyReport):
        self.reports.append(report)
        self.hours_total += report.hours_spent
    
    @property
    def gross_income(self) -> float:
        """Ingreso bruto estimado."""
        return sum(r.estimated_payout for r in self.reports)
    
    @property
    def accepted_count(self) -> int:
        return sum(1 for r in self.reports 
                   if r.status not in ("duplicate", "rejected"))
    
    @property
    def duplicate_rate(self) -> float:
        """Tasa de duplicados."""
        dupes = sum(1 for r in self.reports if r.status == "duplicate")
        return dupes / len(self.reports) if self.reports else 0
    
    @property
    def net_income(self) -> float:
        """Ingreso neto despues de impuestos y herramientas."""
        tax_rate = TAX_RATES.get(self.tax_jurisdiction, 0.30)
        after_tax = self.gross_income * (1 - tax_rate)
        return after_tax - self.tool_cost_monthly
    
    @property
    def hourly_rate_gross(self) -> float:
        """Tarifa horaria bruta."""
        return self.gross_income / self.hours_total if self.hours_total else 0
    
    @property
    def hourly_rate_net(self) -> float:
        """Tarifa horaria neta."""
        return self.net_income / self.hours_total if self.hours_total else 0
    
    def summary(self) -> dict:
        """Resumen completo del mes."""
        return {
            "reports_total": len(self.reports),
            "accepted": self.accepted_count,
            "duplicate_rate": f"{self.duplicate_rate:.1%}",
            "hours_total": self.hours_total,
            "gross_income": f"${self.gross_income:,.0f}",
            "tool_cost": f"${self.tool_cost_monthly:.0f}",
            "tax_rate": f"{TAX_RATES.get(self.tax_jurisdiction, 0.30):.0%}",
            "net_income": f"${self.net_income:,.0f}",
            "hourly_gross": f"${self.hourly_rate_gross:,.0f}/h",
            "hourly_net": f"${self.hourly_rate_net:,.0f}/h",
            "roi_on_tools": f"{self.gross_income / self.tool_cost_monthly:.0f}:1"
                if self.tool_cost_monthly > 0 else "N/A",
        }
