# Extraído de: LibroFinOps/cap-13-anomaly-detection.md
# tasks/anomaly_detection.py
from celery import Celery
from celery.schedules import crontab
import numpy as np
from datetime import datetime, timedelta
from models.cloud_cost_metric import CloudCostMetric, CostAnomaly

celery_app = Celery('anomaly_detection')


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Análisis estadístico cada hora
    sender.add_periodic_task(
        crontab(minute=0),
        detect_cost_anomalies.s(),
        name='detect-cost-anomalies-hourly'
    )


@celery_app.task(name='detect_cost_anomalies')
def detect_cost_anomalies():
    """
    Analiza los costes de las últimas 2 horas contra el histórico de 30 días.
    Las anomalías estadísticas significativas se envían al análisis LLM.
    """
    db = next(get_db())
    anomalies_for_llm = []

    services = db.query(
        CloudCostMetric.provider,
        CloudCostMetric.service
    ).distinct().all()

    for provider, service in services:
        anomaly = _check_service_anomaly(db, provider, service)
        if anomaly:
            anomalies_for_llm.append(anomaly)

    if anomalies_for_llm:
        analyze_anomalies_with_llm.delay(anomalies_for_llm)

    db.close()
    return f"Analizado {len(services)} servicios, {len(anomalies_for_llm)} anomalías"


def _check_service_anomaly(db, provider: str, service: str) -> dict | None:
    """
    Calcula el Z-score del coste actual respecto al histórico de 30 días.
    Devuelve None si no hay anomalía estadística significativa.
    """
    now = datetime.utcnow()
    two_hours_ago = now - timedelta(hours=2)
    thirty_days_ago = now - timedelta(days=30)

    recent_costs = db.query(CloudCostMetric.cost_usd).filter(
        CloudCostMetric.provider == provider,
        CloudCostMetric.service == service,
        CloudCostMetric.period_start >= two_hours_ago
    ).all()

    if not recent_costs:
        return None

    current_cost = sum(r.cost_usd for r in recent_costs)

    historical_costs = db.query(CloudCostMetric.cost_usd).filter(
        CloudCostMetric.provider == provider,
        CloudCostMetric.service == service,
        CloudCostMetric.period_start >= thirty_days_ago,
        CloudCostMetric.period_start < two_hours_ago
    ).all()

    # Mínimo 2 días de historia para calcular Z-score fiable
    if len(historical_costs) < 48:
        return None

    hist_values = [r.cost_usd for r in historical_costs]
    mean = np.mean(hist_values)
    std = np.std(hist_values)

    if std == 0:
        # Servicio sin variabilidad: cualquier cambio >10% es significativo
        if current_cost > mean * 1.10 or current_cost < mean * 0.90:
            return _build_anomaly_dict(provider, service, current_cost, mean, 0, 99.0)
        return None

    z_score = (current_cost - mean) / std
    pct_deviation = ((current_cost - mean) / mean) * 100

    # Umbral ajustado por antigüedad del histórico
    threshold = 2.0 if len(historical_costs) > 200 else 1.5

    if abs(z_score) > threshold or abs(pct_deviation) > 20:
        return _build_anomaly_dict(provider, service, current_cost, mean, std, z_score)

    return None
