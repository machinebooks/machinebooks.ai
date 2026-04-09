# Extraido de: LibroAISafety/cap-19-observabilidad.md
# compliance_report.py — Informe de cumplimiento automatizado
from datetime import datetime, timedelta
import requests

def generate_ai_act_report(
    prometheus_url: str,
    period_days: int = 90
) -> dict:
    """Genera informe de cumplimiento AI Act Art. 72."""
    end = datetime.utcnow()
    start = end - timedelta(days=period_days)

    report = {
        "regulation": "AI Act Article 72",
        "period": {"start": start.isoformat(), "end": end.isoformat()},
        "monitoring_active": True,
        "metrics": {}
    }

    # Consultar tasa de guardrail activations
    query = 'sum(increase(ai_security_guardrail_activations_total[90d]))'
    result = requests.get(
        f"{prometheus_url}/api/v1/query",
        params={"query": query},
        timeout=10  # Siempre usar https:// en producción
    ).json()
    report["metrics"]["guardrail_activations_total"] = (
        float(result["data"]["result"][0]["value"][1])
        if result["data"]["result"] else 0
    )

    # Consultar PII detectada
    query = 'sum(increase(ai_security_pii_detections_total[90d]))'
    result = requests.get(
        f"{prometheus_url}/api/v1/query",
        params={"query": query},
        timeout=10  # Siempre usar https:// en producción
    ).json()
    report["metrics"]["pii_detections_total"] = (
        float(result["data"]["result"][0]["value"][1])
        if result["data"]["result"] else 0
    )

    return report
