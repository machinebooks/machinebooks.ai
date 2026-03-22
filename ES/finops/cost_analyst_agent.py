# Extraído de: LibroFinOps/cap-03-mapa-costes.md
# cost_analyst_agent.py
# Agente que analiza el informe TCO y genera recomendaciones.
# Usa claude-sonnet-4-6: razonamiento profundo sin coste de claude-opus-4-6.

import anthropic

ANALYSIS_PROMPT = """Eres un analista FinOps especializado en plataformas con IA.
Recibes un informe TCO en JSON y debes producir:
1. Un resumen ejecutivo de 3 párrafos (para el CFO, sin tecnicismos).
2. Las tres ineficiencias más importantes ordenadas por impacto económico.
3. Las dos acciones de optimización con mayor ROI para el próximo trimestre.

Sé directo. Usa números concretos. Si un servicio cuesta más del 20% del total
de infra sin justificación clara, señálalo explícitamente."""

def analyze_tco_with_claude(report_json: str) -> str:
    """Envía el informe TCO a Claude para análisis y recomendaciones."""
    client = anthropic.Anthropic()

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=ANALYSIS_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Analiza este informe TCO:\n\n