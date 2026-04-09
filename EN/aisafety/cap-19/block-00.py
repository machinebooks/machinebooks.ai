# Extracted from: LibroAISafety/ch-19-observability.md
from prometheus_client import Counter, Histogram, Gauge, Info
from functools import wraps
import time

# --- Security metrics for AI ---

# Detected prompt injection attempts
injection_attempts = Counter(
    "ai_security_injection_attempts_total",
    "Detected prompt injection attempts",
    ["severity", "user_type", "detection_method"]
)

# Guardrail activations
guardrail_activations = Counter(
    "ai_security_guardrail_activations_total",
    "Guardrail activations by type",
    ["guardrail_type", "action"]  # action: blocked, warned, logged
)

# PII detected in responses
pii_detections = Counter(
    "ai_security_pii_detections_total",
    "PII detections in model responses",
    ["pii_type"]  # email, phone, name, id_number
)

# System prompt integrity
system_prompt_hash = Info(
    "ai_security_system_prompt",
    "Hash and information of the active system prompt"
)

# Generation latency (to detect DoS)
generation_latency = Histogram(
    "ai_security_generation_seconds",
    "Response generation latency",
    buckets=[0.5, 1, 2, 5, 10, 30, 60]
)

# Response length (to detect exfiltration)
response_length = Histogram(
    "ai_security_response_length_chars",
    "Generated response length in characters",
    buckets=[100, 500, 1000, 2000, 5000, 10000]
)

# Tool usage by the agent
tool_invocations = Counter(
    "ai_security_tool_invocations_total",
    "Tool invocations by the agent",
    ["tool_name", "result"]  # result: success, blocked, error
)

# Documents ingested in RAG
rag_ingestion = Counter(
    "ai_security_rag_ingestion_total",
    "Documents processed in RAG pipeline",
    ["status", "classification"]  # status: indexed, blocked, error
)

# Overall security health status
security_health = Gauge(
    "ai_security_health_score",
    "Security health score (0-100)"
)
