# Source: The FinOps Engineer and the Machine -- Chapter 29
# Pattern: Convergence analyst agent

# agents/convergence_analyst.py
# Agent that analyzes cost from the three convergent dimensions.

import anthropic
from dataclasses import dataclass


@dataclass
class AnalisisConvergente:
    """Integrated analysis of FinOps + AIOps + GreenOps."""
    periodo: str
    coste_total_eur: float
    kwh_total: float
    co2_kg_total: float
    roi: float
    recomendacion_principal: str
    impacto_estimado: str


class ConvergenceAnalyst:
    """Produces integrated analyses of the three convergent dimensions."""

    def __init__(self):
        self.client = anthropic.Anthropic()

    def analizar(self, metricas: list[dict], objetivo: str) -> AnalisisConvergente:
        metricas_texto = "\n".join([
            f"{m['periodo']}: €{m['coste_total_eur']:.0f}, "
            f"{m['kwh_total']:.1f} kWh, {m['co2_kg_total']:.2f} kgCO₂, "
            f"ROI {m['roi']:.1f}×"
            for m in metricas[-6:]
        ])

        prompt = f"""You are a senior convergent FinOps analyst.
Analyze this time series from an AI-powered platform:

{metricas_texto}

OBJETIVO: {objetivo}

Provide:
1. Economic insight: cost pattern, Jevons paradox active?
2. Energy insight: consumption evolution, efficiency per euro
3. Carbon insight: emissions trend
4. Main recommendation: the highest impact action across all three dimensions
5. Estimated impact: quantify the expected effect

No hype. If there is a Jevons paradox, state it and explain the implications.
Respond in European Spanish."""

        response = self.client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )

        ultimo = metricas[-1] if metricas else {}
        return AnalisisConvergente(
            periodo=ultimo.get("periodo", "N/A"),
            coste_total_eur=ultimo.get("coste_total_eur", 0),
            kwh_total=ultimo.get("kwh_total", 0),
            co2_kg_total=ultimo.get("co2_kg_total", 0),
            roi=ultimo.get("roi", 0),
            recomendacion_principal=response.content[0].text,
            impacto_estimado="Quantified in the analysis above",
        )
