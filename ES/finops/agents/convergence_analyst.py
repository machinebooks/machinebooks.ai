# Extraído de: LibroFinOps/cap-29-convergencia.md
# agents/convergence_analyst.py
# Agente que analiza coste desde las tres dimensiones convergentes.

import anthropic
from dataclasses import dataclass


@dataclass
class AnalisisConvergente:
    """Análisis integrado de FinOps + AIOps + GreenOps."""
    periodo: str
    coste_total_eur: float
    kwh_total: float
    co2_kg_total: float
    roi: float
    recomendacion_principal: str
    impacto_estimado: str


class ConvergenceAnalyst:
    """Produce análisis integrados de las tres dimensiones convergentes."""

    def __init__(self):
        self.client = anthropic.Anthropic()

    def analizar(self, metricas: list[dict], objetivo: str) -> AnalisisConvergente:
        metricas_texto = "\n".join([
            f"{m['periodo']}: €{m['coste_total_eur']:.0f}, "
            f"{m['kwh_total']:.1f} kWh, {m['co2_kg_total']:.2f} kgCO₂, "
            f"ROI {m['roi']:.1f}×"
            for m in metricas[-6:]
        ])

        prompt = f"""Eres un analista senior de FinOps convergente.
Analiza esta serie temporal de una plataforma con IA:

{metricas_texto}

OBJETIVO: {objetivo}

Proporciona:
1. Insight económico: patrón de coste, ¿paradoja de Jevons activa?
2. Insight energético: evolución del consumo, eficiencia por euro
3. Insight de carbono: tendencia de emisiones
4. Recomendación principal: la acción de mayor impacto en las tres dimensiones
5. Impacto estimado: cuantifica el efecto esperado

Sin hype. Si hay paradoja de Jevons, dilo y explica las implicaciones.
Responde en español de España."""

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
            impacto_estimado="Cuantificado en el análisis anterior",
        )
