# Extraído de: LibroFinOps/cap-16-forecasting.md
# forecasting/llm_adjuster.py
import anthropic
import json
from datetime import date

client = anthropic.Anthropic()

FORECASTING_SYSTEM_PROMPT = """Eres un analista FinOps experto en forecasting
de costes cloud. Recibes una proyección estadística base y contexto de negocio.

Tu función es:
1. Evaluar si el contexto justifica ajustar la proyección estadística
2. Cuantificar ajustes con argumentación (no inventar números)
3. Producir un rango: optimista / esperado / conservador
4. Explicar en lenguaje que entienda un CFO

PRINCIPIOS:
- Si el contexto no justifica ajuste, mantén la base estadística
- Los ajustes se basan en datos históricos o analogías documentadas
- Siempre produce un rango, nunca un número único
- La explicación debe ser legible sin conocimientos de cloud

Responde en JSON:
{
  "statistical_base_usd": ...,
  "adjusted_forecast_usd": ...,
  "range_low_usd": ...,
  "range_high_usd": ...,
  "confidence_level": "high|medium|low",
  "adjustments": [
    {"factor": "descripción", "impact_usd": ..., "reasoning": "..."}
  ],
  "executive_summary": "2-3 frases para el CFO",
  "key_uncertainties": ["incertidumbre 1", "incertidumbre 2"]
}"""


def adjust_forecast_with_context(
    statistical_data: dict,
    business_context: str,
    historical_context: str
) -> dict:
    """
    Ajusta el forecast estadístico con contexto de negocio.
    Devuelve el forecast con rango y explicación ejecutiva.
    """
    today = date.today()

    user_message = f"""Ajusta este forecast de coste cloud.

PROYECCIÓN ESTADÍSTICA BASE:
{json.dumps(statistical_data, indent=2)}

CONTEXTO DE NEGOCIO ({today.strftime('%B %Y')}):
{business_context}

CONTEXTO HISTÓRICO (periodos similares):
{historical_context}

Produce el forecast ajustado con justificación detallada."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=FORECASTING_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}]
    )

    try:
        return json.loads(response.content[0].text)
    except json.JSONDecodeError:
        # Fallback: proyección estadística sin ajuste LLM
        base = statistical_data.get('trend_adjusted_projection_usd')
        return {
            'statistical_base_usd': base,
            'adjusted_forecast_usd': base,
            'range_low_usd': base * 0.9,
            'range_high_usd': base * 1.1,
            'confidence_level': 'low',
            'adjustments': [],
            'executive_summary': 'Forecast estadístico sin ajuste '
                                 'contextual (error de análisis LLM).',
            'key_uncertainties': [
                'Error en análisis LLM: usar proyección base'
            ]
        }
