# Extraído de: LibroCISO/cap-24-calidad-ia.md
from celery import shared_task
from datetime import datetime, timedelta
from sqlalchemy import func
import numpy as np

@shared_task(queue='maintenance', name='ai.calculate_quality_metrics')
def calculate_quality_metrics(period_type: str = 'daily'):
    """Calcula métricas agregadas de calidad IA.

    Se ejecuta diariamente vía Celery Beat.
    Cada métrica se compara contra el período anterior
    para calcular la tendencia automáticamente.

    Métricas calculadas:
    - accuracy: % de respuestas evaluadas como correctas
    - hallucination_rate: % de respuestas con alucinaciones
    - groundedness_avg: media de groundedness del RAG
    - error_rate: % de llamadas que fallaron
    - avg_latency_ms: latencia media en milisegundos
    - monthly_cost_usd: coste acumulado del mes
    - fairness_dpd: Demographic Parity Difference (si aplica)
    - drift_psi: Population Stability Index vs baseline
    """
    from app.database import db_session
    from app.models import LLMUsageLog, LLMQualityScore, AIMonitoringMetric

    now = datetime.utcnow()

    if period_type == 'daily':
        period_start = now.replace(hour=0, minute=0, second=0) - timedelta(days=1)
        period_end = now.replace(hour=0, minute=0, second=0)
    elif period_type == 'weekly':
        period_start = now - timedelta(days=7)
        period_end = now

    # ── Obtener registros del período ──
    usage_logs = db_session.query(LLMUsageLog).filter(
        LLMUsageLog.created_at >= period_start,
        LLMUsageLog.created_at < period_end
    ).all()

    quality_scores = db_session.query(LLMQualityScore).filter(
        LLMQualityScore.created_at >= period_start,
        LLMQualityScore.created_at < period_end
    ).all()

    if not usage_logs:
        return {'status': 'no_data', 'period': period_type}

    # ── Agrupar por service_type ──
    services = set(log.service_type for log in usage_logs)
    metrics_created = 0

    for service in services:
        svc_logs = [l for l in usage_logs if l.service_type == service]
        svc_quality = [q for q in quality_scores
                       if q.service_type == service]

        # Error rate
        error_rate = sum(1 for l in svc_logs if not l.success) / len(svc_logs)
        _store_metric(db_session, 'error_rate', service,
                      error_rate, len(svc_logs),
                      period_type, period_start, period_end)

        # Latencia media
        latencies = [l.latency_ms for l in svc_logs if l.latency_ms]
        if latencies:
            _store_metric(db_session, 'avg_latency_ms', service,
                          np.mean(latencies), len(latencies),
                          period_type, period_start, period_end)

        # Coste acumulado
        total_cost = sum(l.cost_total for l in svc_logs)
        _store_metric(db_session, 'period_cost_usd', service,
                      total_cost, len(svc_logs),
                      period_type, period_start, period_end)

        # Métricas de calidad (si hay evaluaciones)
        if svc_quality:
            # Hallucination rate
            halluc_scores = [q.hallucination_score for q in svc_quality
                             if q.hallucination_score is not None]
            if halluc_scores:
                halluc_rate = np.mean(halluc_scores)
                _store_metric(db_session, 'hallucination_rate', service,
                              halluc_rate, len(halluc_scores),
                              period_type, period_start, period_end)

            # Groundedness media
            ground_scores = [q.groundedness_score for q in svc_quality
                             if q.groundedness_score is not None]
            if ground_scores:
                _store_metric(db_session, 'groundedness_avg', service,
                              np.mean(ground_scores), len(ground_scores),
                              period_type, period_start, period_end)

            # Bias score media
            bias_scores = [q.bias_score for q in svc_quality
                           if q.bias_score is not None]
            if bias_scores:
                _store_metric(db_session, 'bias_score_avg', service,
                              np.mean(bias_scores), len(bias_scores),
                              period_type, period_start, period_end)

        metrics_created += 1

    db_session.commit()
    return {'status': 'ok', 'services_processed': metrics_created}


def _store_metric(session, metric_name, service_type,
                  value, sample_size,
                  period_type, period_start, period_end):
    """Almacena una métrica y calcula tendencia vs período anterior."""
    from app.models import AIMonitoringMetric, AIMonitoringThreshold

    # Obtener umbrales configurados para esta métrica
    threshold = session.query(AIMonitoringThreshold).filter_by(
        metric_name=metric_name,
        service_type=service_type
    ).first()

    # Determinar estado según umbrales
    status = 'normal'
    if threshold:
        if threshold.critical_value and _exceeds(
            value, threshold.critical_value, threshold.direction
        ):
            status = 'critical'
        elif threshold.alert_value and _exceeds(
            value, threshold.alert_value, threshold.direction
        ):
            status = 'alert'
        elif threshold.warning_value and _exceeds(
            value, threshold.warning_value, threshold.direction
        ):
            status = 'warning'

    # Calcular tendencia vs período anterior
    trend, delta_pct = _calculate_trend(
        session, metric_name, service_type,
        period_type, period_start, value
    )

    metric = AIMonitoringMetric(
        metric_name=metric_name,
        service_type=service_type,
        value=round(value, 6),
        sample_size=sample_size,
        period_type=period_type,
        period_start=period_start,
        period_end=period_end,
        threshold_warning=threshold.warning_value if threshold else None,
        threshold_alert=threshold.alert_value if threshold else None,
        threshold_critical=threshold.critical_value if threshold else None,
        status=status,
        trend=trend,
        trend_delta_pct=delta_pct,
    )
    session.add(metric)


def _calculate_trend(session, metric_name, service_type,
                     period_type, current_start, current_value):
    """Calcula tendencia usando media ponderada de 3 períodos anteriores.

    Pesos: período más reciente 0.5, anterior 0.3, más antiguo 0.2.
    Variación < 5% = stable. Dirección depende de si la métrica
    es 'higher is better' o 'lower is better'.
    """
    from app.models import AIMonitoringMetric

    # Obtener últimos 3 valores de esta métrica
    previous = session.query(AIMonitoringMetric).filter(
        AIMonitoringMetric.metric_name == metric_name,
        AIMonitoringMetric.service_type == service_type,
        AIMonitoringMetric.period_type == period_type,
        AIMonitoringMetric.period_start < current_start,
    ).order_by(
        AIMonitoringMetric.period_start.desc()
    ).limit(3).all()

    if not previous:
        return None, None

    # Media ponderada
    weights = [0.5, 0.3, 0.2][:len(previous)]
    total_weight = sum(weights)
    weighted_avg = sum(
        p.value * w for p, w in zip(previous, weights)
    ) / total_weight

    if weighted_avg == 0:
        return 'stable', 0.0

    delta_pct = ((current_value - weighted_avg) / abs(weighted_avg)) * 100

    # Métricas donde "más bajo es mejor"
    lower_is_better = {
        'error_rate', 'hallucination_rate', 'avg_latency_ms',
        'period_cost_usd', 'monthly_cost_usd', 'bias_score_avg',
        'fairness_dpd', 'drift_psi',
    }

    if abs(delta_pct) < 5.0:
        trend = 'stable'
    elif metric_name in lower_is_better:
        trend = 'improving' if delta_pct < 0 else 'degrading'
    else:
        trend = 'improving' if delta_pct > 0 else 'degrading'

    return trend, round(delta_pct, 2)


def _exceeds(value, threshold, direction):
    """Verifica si un valor supera un umbral según la dirección."""
    if direction == 'upper':
        return value > threshold  # Malo si sube (error rate, latencia)
    else:
        return value < threshold  # Malo si baja (accuracy, groundedness)
