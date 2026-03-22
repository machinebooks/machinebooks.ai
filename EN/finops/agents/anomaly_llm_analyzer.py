# Source: The FinOps Engineer and the Machine -- Chapter 13
# Pattern: Claude-powered anomaly root cause analysis

# services/anomaly_llm_analyzer.py
import anthropic
import json
from celery import Celery

celery_app = Celery('anomaly_llm_analyzer')
client = anthropic.Anthropic()

ANOMALY_SYSTEM_PROMPT = """You are a FinOps analyst specialized in cloud cost anomaly detection.
You receive statistically pre-filtered anomalies and your task is:

1. Evaluate whether the anomaly deserves urgent human attention
2. Provide an explanation in business language (not technical)
3. Propose the most likely hypotheses about the cause
4. Recommend a concrete action

IMPORTANT: Be concise. The team will read this in 30 seconds before deciding.
Classify urgency as: 'high' (act in <1h), 'medium' (review today), 'low' (monitor)
If the anomaly has a probable business explanation, classify it 'low'.

Respond ONLY in JSON with this exact schema:
{
  "urgency": "high|medium|low",
  "headline": "One sentence summarizing the anomaly",
  "explanation": "2-3 sentences explaining what is happening and why it matters",
  "hypotheses": ["hypothesis 1", "hypothesis 2"],
  "recommended_action": "Concrete action"
}"""


@celery_app.task(name='analyze_anomalies_with_llm')
def analyze_anomalies_with_llm(anomalies: list[dict]):
    """
    Analyzes statistical anomalies with Claude to generate enriched alerts.
    Groups all anomalies in a single prompt to minimize token cost.
    """
    business_context = get_current_business_context()

    user_message = f"""Analyze these cloud cost anomalies detected in the last 2 hours:

{json.dumps(anomalies, indent=2)}

Current business context:
{business_context}

Return a JSON array with one analysis object per anomaly, in the same order."""

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
        # Invalid JSON: save raw response for debugging
        _log_parse_error(anomalies, response.content[0].text)


def _save_and_notify_anomalies(anomalies: list, analyses: list):
    """Saves analyses and sends notifications for urgent ones."""
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
