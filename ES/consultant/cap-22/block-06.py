# Extraído de: LibroConsultor/cap-22-unit-economics.md
@dataclass
class ProjectComparison:
    """Comparativa antes/después para un proyecto individual."""
    project_name: str
    project_type: str

    # Modelo tradicional
    traditional_hours: float
    traditional_bill_rate: float
    traditional_cost_rate: float = 58.0  # Coste/hora del consultor

    # Modelo aumentado
    augmented_hours: float
    augmented_price: float               # Precio total cobrado (fee fijo)
    ai_token_cost: float                 # Coste de tokens para este proyecto
    ai_infra_cost: float                 # Cuota proporcional de infra

    @property
    def traditional_revenue(self) -> float:
        return self.traditional_hours * self.traditional_bill_rate

    @property
    def traditional_cost(self) -> float:
        return self.traditional_hours * self.traditional_cost_rate

    @property
    def traditional_margin(self) -> float:
        return self.traditional_revenue - self.traditional_cost

    @property
    def augmented_cost(self) -> float:
        return (self.augmented_hours * self.traditional_cost_rate
                + self.ai_token_cost + self.ai_infra_cost)

    @property
    def augmented_margin(self) -> float:
        return self.augmented_price - self.augmented_cost

    @property
    def margin_improvement(self) -> float:
        if self.traditional_margin == 0:
            return 0
        return ((self.augmented_margin - self.traditional_margin)
                / self.traditional_margin)

    @property
    def client_savings(self) -> float:
        """Ahorro para el cliente respecto al precio tradicional."""
        return self.traditional_revenue - self.augmented_price

    @property
    def client_savings_pct(self) -> float:
        if self.traditional_revenue == 0:
            return 0
        return self.client_savings / self.traditional_revenue

    def summary(self) -> dict:
        trad_rev = self.traditional_revenue
        return {
            "proyecto": self.project_name,
            "tipo": self.project_type,
            "tradicional": {
                "horas": self.traditional_hours,
                "facturación": f"€{trad_rev:,.0f}",
                "coste": f"€{self.traditional_cost:,.0f}",
                "margen": f"€{self.traditional_margin:,.0f}",
                "margen_pct": f"{self.traditional_margin / trad_rev:.0%}",
            },
            "aumentado": {
                "horas": self.augmented_hours,
                "facturación": f"€{self.augmented_price:,.0f}",
                "coste": f"€{self.augmented_cost:,.0f}",
                "margen": f"€{self.augmented_margin:,.0f}",
                "margen_pct": f"{self.augmented_margin / self.augmented_price:.0%}",
            },
            "ahorro_cliente": (
                f"€{self.client_savings:,.0f} ({self.client_savings_pct:.0%})"
            ),
            "mejora_margen": f"{self.margin_improvement:.0%}",
        }

# Ejemplo: auditoría de cumplimiento ISO 27001 + ENS
audit = ProjectComparison(
    project_name="Auditoría cumplimiento sector público",
    project_type="audit",
    traditional_hours=300,
    traditional_bill_rate=105,
    augmented_hours=120,
    augmented_price=25_200,  # 80% del precio tradicional
    ai_token_cost=85,
    ai_infra_cost=35,
)

print(json.dumps(audit.summary(), indent=2, ensure_ascii=False))
