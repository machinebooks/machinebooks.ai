# Extraído de: LibroDevSecOps/cap-20-respuesta-incidentes.md
# Exportar métricas a Prometheus
from prometheus_client import Histogram, Counter, Gauge

incident_duration = Histogram(
    "incident_response_duration_seconds",
    "Duración de cada fase de respuesta",
    labelnames=["phase", "severity"],
    buckets=[60, 120, 300, 600, 1800, 3600, 14400]
)

containment_actions = Counter(
    "incident_containment_actions_total",
    "Acciones de contención ejecutadas",
    labelnames=["action_type", "status"]  # status: approved, rejected, auto
)

active_incidents = Gauge(
    "incident_active_count",
    "Número de incidentes activos",
    labelnames=["severity"]
)

agent_cost = Histogram(
    "incident_agent_cost_usd",
    "Coste en USD del agente por incidente",
    buckets=[0.05, 0.10, 0.20, 0.50, 1.00, 2.00, 5.00]
)
