# Extraído de: LibroFinOps/cap-18-business-case-cfo.md
class BusinessCaseGenerator:
    """
    Genera el business case ejecutivo a partir de datos reales.
    Combina datos de ROITracker con parámetros financieros.
    """
    STANDARD_LIMITATIONS = [
        "El ROI depende del factor de productividad capturada "
        "(asumido 0.70). Si es 0.50, el ROI baja ~30%.",
        "El coste crece linealmente con el uso. Presupuesto "
        "automático activado al 80% del límite mensual.",
        "Tiempos HumanBaseline revisados trimestralmente. "
        "Varianza estimada: ±20%.",
        "Calidad del modelo LLM puede variar con actualizaciones "
        "del proveedor. Alertas de degradación activas.",
    ]

    def __init__(self, db: Session):
        self.db = db
        self.roi_tracker = ROITracker(db)

    def generate(
        self,
        tenant_id: Optional[int],
        engineering_investment_eur: float,
        days_of_data: int = 30,
    ) -> BusinessCaseSummary:
        """Genera business case con tres escenarios."""
        roi_summary = self.roi_tracker.get_summary(
            tenant_id=tenant_id, days=days_of_data,
        )
        monthly_llm_cost = roi_summary.get("total_llm_cost_eur", 0)
        monthly_value = roi_summary.get("total_value_eur", 0)
        roi_adjusted = roi_summary.get("roi_global", 0)

        # Break-even: meses para recuperar inversión
        monthly_net = monthly_value - monthly_llm_cost
        break_even = (
            int(engineering_investment_eur / monthly_net) + 1
            if monthly_net > 0 else 999
        )
        year1_net = (monthly_net * 12) - engineering_investment_eur

        return BusinessCaseSummary(
            generated_at=datetime.utcnow(),
            period_days=days_of_data,
            monthly_llm_cost_eur=round(monthly_llm_cost, 2),
            monthly_value_liberated_eur=round(monthly_value, 2),
            roi_adjusted=round(roi_adjusted, 1),
            engineering_investment_eur=engineering_investment_eur,
            break_even_month=break_even,
            year1_net_value_eur=round(year1_net, 2),
            scenarios=self._build_scenarios(
                monthly_llm_cost, monthly_value
            ),
            limitations=self.STANDARD_LIMITATIONS.copy(),
            assumptions=[
                f"Datos basados en {days_of_data} días reales.",
                "Tipo de cambio USD/EUR: 0.92 (fijo).",
                "Precios LLM estables en la proyección.",
            ],
        )
