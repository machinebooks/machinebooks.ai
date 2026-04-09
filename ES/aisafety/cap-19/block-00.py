# Extraido de: LibroAISafety/cap-19-observabilidad.md
from prometheus_client import Counter, Histogram, Gauge, Info
from functools import wraps
import time

# --- Métricas de seguridad para IA ---

# Intentos de prompt injection detectados
injection_attempts = Counter(
    "ai_security_injection_attempts_total",
    "Intentos de prompt injection detectados",
    ["severity", "user_type", "detection_method"]
)

# Activaciones de guardrail
guardrail_activations = Counter(
    "ai_security_guardrail_activations_total",
    "Activaciones de guardrail por tipo",
    ["guardrail_type", "action"]  # action: blocked, warned, logged
)

# PII detectada en respuestas
pii_detections = Counter(
    "ai_security_pii_detections_total",
    "Detecciones de PII en respuestas del modelo",
    ["pii_type"]  # email, phone, name, id_number
)

# Integridad del system prompt
system_prompt_hash = Info(
    "ai_security_system_prompt",
    "Hash e información del system prompt activo"
)

# Latencia de generación (para detectar DoS)
generation_latency = Histogram(
    "ai_security_generation_seconds",
    "Latencia de generación de respuestas",
    buckets=[0.5, 1, 2, 5, 10, 30, 60]
)

# Longitud de respuesta (para detectar exfiltración)
response_length = Histogram(
    "ai_security_response_length_chars",
    "Longitud de respuestas generadas en caracteres",
    buckets=[100, 500, 1000, 2000, 5000, 10000]
)

# Uso de herramientas por el agente
tool_invocations = Counter(
    "ai_security_tool_invocations_total",
    "Invocaciones de herramientas por el agente",
    ["tool_name", "result"]  # result: success, blocked, error
)

# Documentos ingestados en RAG
rag_ingestion = Counter(
    "ai_security_rag_ingestion_total",
    "Documentos procesados en pipeline RAG",
    ["status", "classification"]  # status: indexed, blocked, error
)

# Estado de salud general de seguridad
security_health = Gauge(
    "ai_security_health_score",
    "Score de salud de seguridad (0-100)"
)
