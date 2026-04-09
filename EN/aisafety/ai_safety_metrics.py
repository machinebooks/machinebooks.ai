# Extracted from: LibroAISafety/ch-10-operational-governance.md
# ai_safety_metrics.py — Prometheus metrics for AI systems
from prometheus_client import Counter, Histogram, Gauge

# Guardrail metrics
guardrail_input_triggers = Counter(
    "ai_guardrail_input_triggers_total",
    "Requests blocked by input guardrails",
    ["system", "guardrail_type", "reason"]
)

guardrail_output_triggers = Counter(
    "ai_guardrail_output_triggers_total",
    "Responses filtered by output guardrails",
    ["system", "guardrail_type", "reason"]
)

guardrail_false_positives = Counter(
    "ai_guardrail_false_positives_total",
    "Legitimate requests incorrectly blocked",
    ["system", "guardrail_type"]
)

guardrail_latency = Histogram(
    "ai_guardrail_latency_seconds",
    "Latency added by guardrail evaluation",
    ["system", "guardrail_type"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0]
)

# Model behavior metrics
model_refusal_rate = Gauge(
    "ai_model_refusal_rate",
    "Sensitive request rejection rate (1h moving average)",
    ["system", "model"]
)

model_response_length = Histogram(
    "ai_model_response_length_tokens",
    "Response length distribution in tokens",
    ["system", "model"],
    buckets=[50, 100, 250, 500, 1000, 2000, 4000]
)

# Anomaly metrics
anomaly_detections = Counter(
    "ai_anomaly_detections_total",
    "Anomalies detected in usage patterns",
    ["system", "anomaly_type"]
)

# Compliance metrics
compliance_status = Gauge(
    "ai_compliance_status",
    "Compliance status (1=compliant, 0=non-compliant)",
    ["system", "policy_rule"]
)

eval_days_remaining = Gauge(
    "ai_eval_days_remaining",
    "Days until security evaluation expires",
    ["system"]
)
