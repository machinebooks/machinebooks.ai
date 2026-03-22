# Extraído de: LibroCISO/cap-14-gobernanza-ia-ai-act.md
# Ejemplo didáctico: servicios/ai_monitoring_service.py
# Servicio de evaluación de métricas y generación de alertas

from datetime import datetime, timedelta


def evaluate_metric(
    metric_type: MetricType,
    current_value: float,
    thresholds: dict,
    historical_values: list[float]
) -> dict:
    """Evalúa una métrica contra umbrales y calcula tendencia.

    Para métricas donde menor es mejor (error_rate, drift, fairness_dpd, bias_score):
      normal < warning < alert < critical

    Para métricas donde mayor es mejor (accuracy):
      critical < alert < warning < normal
    """
    # Métricas inversas: mayor valor = peor
    inverse_metrics = {MetricType.ERROR_RATE, MetricType.DRIFT_PSI,
                       MetricType.FAIRNESS_DPD, MetricType.BIAS_SCORE,
                       MetricType.LATENCY_P99}

    is_inverse = metric_type in inverse_metrics

    # Evaluar nivel de alerta
    warning = thresholds.get("warning")
    alert = thresholds.get("alert")
    critical = thresholds.get("critical")

    if is_inverse:
        # Para error_rate, drift, etc.: valor alto = malo
        if critical and current_value >= critical:
            alert_level = AlertLevel.CRITICAL
        elif alert and current_value >= alert:
            alert_level = AlertLevel.ALERT
        elif warning and current_value >= warning:
            alert_level = AlertLevel.WARNING
        else:
            alert_level = AlertLevel.NORMAL
    else:
        # Para accuracy: valor bajo = malo
        if critical and current_value <= critical:
            alert_level = AlertLevel.CRITICAL
        elif alert and current_value <= alert:
            alert_level = AlertLevel.ALERT
        elif warning and current_value <= warning:
            alert_level = AlertLevel.WARNING
        else:
            alert_level = AlertLevel.NORMAL

    # Calcular tendencia (últimos 5 valores vs anteriores 5)
    trend = MetricTrend.STABLE
    if len(historical_values) >= 10:
        recent = sum(historical_values[-5:]) / 5
        previous = sum(historical_values[-10:-5]) / 5
        delta = recent - previous

        # Umbral de cambio significativo: 5% del valor medio
        avg = (recent + previous) / 2 if (recent + previous) != 0 else 1
        threshold = abs(avg * 0.05)

        if abs(delta) > threshold:
            if is_inverse:
                trend = MetricTrend.IMPROVING if delta < 0 else MetricTrend.DEGRADING
            else:
                trend = MetricTrend.IMPROVING if delta > 0 else MetricTrend.DEGRADING

    return {
        "alert_level": alert_level,
        "trend": trend,
        "needs_action": alert_level in (AlertLevel.ALERT, AlertLevel.CRITICAL),
        "is_urgent": alert_level == AlertLevel.CRITICAL and trend == MetricTrend.DEGRADING
    }


# Umbrales por defecto (configurables por sistema)
DEFAULT_THRESHOLDS = {
    MetricType.ACCURACY: {
        "warning": 0.80,     # < 80% precisión: investigar
        "alert": 0.70,       # < 70%: acción requerida
        "critical": 0.60     # < 60%: considerar suspender
    },
    MetricType.FAIRNESS_DPD: {
        "warning": 0.10,     # > 10% diferencia: investigar
        "alert": 0.20,       # > 20%: posible discriminación
        "critical": 0.30     # > 30%: sesgo grave
    },
    MetricType.DRIFT_PSI: {
        "warning": 0.10,     # PSI > 0.1: cambio moderado
        "alert": 0.25,       # PSI > 0.25: drift significativo
        "critical": 0.50     # PSI > 0.5: distribución muy diferente
    },
    MetricType.LATENCY_P99: {
        "warning": 10000,    # > 10s: lento
        "alert": 30000,      # > 30s: impacto operativo
        "critical": 60000    # > 60s: inutilizable
    },
    MetricType.ERROR_RATE: {
        "warning": 0.05,     # > 5% errores: investigar
        "alert": 0.10,       # > 10%: problema serio
        "critical": 0.20     # > 20%: considerar suspender
    },
    MetricType.BIAS_SCORE: {
        "warning": 0.15,     # > 15%: sesgo detectable
        "alert": 0.25,       # > 25%: sesgo significativo
        "critical": 0.40     # > 40%: sesgo grave
    },
}
