# Extraído de: LibroFinOps/cap-13-anomaly-detection.md
# services/anomaly_llm_analyzer.py
import anthropic
import json
from celery import Celery

celery_app = Celery('anomaly_llm_analyzer')
client = anthropic.Anthropic()

ANOMALY_SYSTEM_PROMPT = """Eres un analista FinOps especializado en detección de anomalías
en costes cloud. Recibes anomalías estadísticas ya filtradas y tu tarea es:

1. Evaluar si la anomalía merece atención humana urgente
2. Proporcionar una explicación en lenguaje de negocio (no técnico)
3. Plantear las hipótesis más probables sobre la causa
4. Recomendar una acción concreta

IMPORTANTE: Sé conciso. El equipo leerá esto en 30 segundos antes de decidir.
Clasifica urgencia como: 'high' (actuar en <1h), 'medium' (revisar hoy), 'low' (monitorizar)
Si la anomalía tiene explicación probable de negocio, clasifícala 'low'.

Responde SOLO en JSON con este esquema exacto:
{
  "urgency": "high|medium|low",
  "headline": "Una frase que resume la anomalía",
  "explanation": "2-3 frases explicando qué está pasando y por qué importa",
  "hypotheses": ["hipótesis 1", "hipótesis 2"],
  "recommended_action": "Acción concreta"
}"""


@celery_app.task(name='analyze_anomalies_with_llm')
def analyze_anomalies_with_llm(anomalies: list[dict]):
    """
    Analiza las anomalías estadísticas con Claude para generar alertas enriquecidas.
    Agrupa todas las anomalías en un único prompt para minimizar el coste de tokens.
    """
    business_context = get_current_business_context()

    user_message = f"""Analiza estas anomalías de coste cloud detectadas en las últimas 2 horas:

{json.dumps(anomalies, indent=2)}

Contexto de negocio actual:
{business_context}

Devuelve un array JSON con un objeto de análisis por anomalía, en el mismo orden."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=ANOMALY_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}]
    )

    try:
        analyses = json.loads(response.content[0].text)
        if isinstance(analyses, dict):
            analyses = [analyses]
        _save_and_notify_anomalies(anomalies, analyses)
    except json.JSONDecodeError:
        # JSON inválido: guardamos la respuesta en bruto para debugging
        _log_parse_error(anomalies, response.content[0].text)


def _save_and_notify_anomalies(anomalies: list, analyses: list):
    """Guarda los análisis y envía notificaciones para las urgentes."""
    db = next(get_db())

    for anomaly_data, analysis in zip(anomalies, analyses):
        db_anomaly = CostAnomaly(
            provider=anomaly_data['provider'],
            service=anomaly_data['service'],
            z_score=anomaly_data['z_score'],
            cost_usd=anomaly_data['current_cost_usd'],
            expected_cost_usd=anomaly_data['historical_mean_usd'],
            pct_deviation=anomaly_data['pct_deviation'],
            urgency=analysis.get('urgency', 'medium'),
            llm_explanation=analysis.get('explanation', '')
        )
        db.add(db_anomaly)

        if analysis.get('urgency') in ['high', 'medium']:
            _send_alert_notification(anomaly_data, analysis)

    db.commit()
    db.close()
