# Extraido de: LibroAISafety/cap-10-governance-operativa.md
# ai_safety_metrics.py — Métricas Prometheus para sistemas de IA
from prometheus_client import Counter, Histogram, Gauge

# Métricas de guardrails
guardrail_input_triggers = Counter(
    "ai_guardrail_input_triggers_total",
    "Peticiones bloqueadas por guardrails de input",
    ["system", "guardrail_type", "reason"]
)

guardrail_output_triggers = Counter(
    "ai_guardrail_output_triggers_total",
    "Respuestas filtradas por guardrails de output",
    ["system", "guardrail_type", "reason"]
)

guardrail_false_positives = Counter(
    "ai_guardrail_false_positives_total",
    "Peticiones legítimas bloqueadas incorrectamente",
    ["system", "guardrail_type"]
)

guardrail_latency = Histogram(
    "ai_guardrail_latency_seconds",
    "Latencia añadida por evaluación de guardrails",
    ["system", "guardrail_type"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0]
)

# Métricas de comportamiento del modelo
model_refusal_rate = Gauge(
    "ai_model_refusal_rate",
    "Tasa de rechazo de peticiones sensibles (media móvil 1h)",
    ["system", "model"]
)

model_response_length = Histogram(
    "ai_model_response_length_tokens",
    "Distribución de longitud de respuestas en tokens",
    ["system", "model"],
    buckets=[50, 100, 250, 500, 1000, 2000, 4000]
)

# Métricas de anomalía
anomaly_detections = Counter(
    "ai_anomaly_detections_total",
    "Anomalías detectadas en patrones de uso",
    ["system", "anomaly_type"]
)

# Métricas de compliance
compliance_status = Gauge(
    "ai_compliance_status",
    "Estado de cumplimiento (1=compliant, 0=non-compliant)",
    ["system", "policy_rule"]
)

eval_days_remaining = Gauge(
    "ai_eval_days_remaining",
    "Días hasta que la evaluación de seguridad expire",
    ["system"]
)
