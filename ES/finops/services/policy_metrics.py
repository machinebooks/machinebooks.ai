# Extraído de: LibroFinOps/cap-20-policy-as-code.md
# services/policy_metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Solicitudes bloqueadas por política
policy_blocks = Counter(
    "finops_policy_blocks_total",
    "Solicitudes bloqueadas por política FinOps",
    ["tenant_id", "task_type", "reason"],
)

# Solicitudes que activaron alerta de presupuesto
policy_alerts = Counter(
    "finops_policy_budget_alerts_total",
    "Solicitudes que superaron el umbral de alerta",
    ["tenant_id", "task_type"],
)

# Latencia de evaluación de política
policy_eval_duration = Histogram(
    "finops_policy_eval_seconds",
    "Latencia de evaluación de política por solicitud",
    ["task_type"],
)

# Presupuesto consumido como porcentaje del límite
budget_usage_ratio = Gauge(
    "finops_budget_usage_ratio",
    "Porcentaje del presupuesto consumido en el periodo",
    ["tenant_id", "task_type"],
)
