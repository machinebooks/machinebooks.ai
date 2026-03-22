# Extraído de: LibroDevSecOps/cap-23-excepciones-deuda.md
from prometheus_client import Gauge, Counter

# Gauges para estado actual
active_exceptions = Gauge(
    "security_debt_active_exceptions",
    "Excepciones de seguridad activas",
    ["severity"]
)
debt_score_total = Gauge(
    "security_debt_score_total",
    "Puntuación total de deuda de seguridad"
)
avg_exception_age = Gauge(
    "security_debt_avg_age_days",
    "Edad media de excepciones activas en días"
)
expired_unresolved = Gauge(
    "security_debt_expired_unresolved",
    "Excepciones expiradas sin resolver"
)

# Counters para eventos
exceptions_requested = Counter(
    "security_exceptions_requested_total",
    "Total de excepciones solicitadas",
    ["severity"]
)
exceptions_approved = Counter(
    "security_exceptions_approved_total",
    "Total de excepciones aprobadas",
    ["severity"]
)
exceptions_denied = Counter(
    "security_exceptions_denied_total",
    "Total de excepciones denegadas",
    ["severity"]
)


def update_prometheus_metrics(debt_data: dict):
    """Actualiza métricas de Prometheus con datos de deuda."""
    debt_score_total.set(debt_data["total_debt_score"])
    avg_exception_age.set(debt_data["average_exception_age_days"])
    expired_unresolved.set(debt_data["expired_unresolved"])

    for severity, score in debt_data["debt_by_severity"].items():
        active_exceptions.labels(severity=severity).set(score)
