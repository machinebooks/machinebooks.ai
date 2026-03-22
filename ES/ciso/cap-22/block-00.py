# Extraído de: LibroCISO/cap-22-observabilidad-siem.md
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram, Gauge

app = FastAPI(title="GRC Platform API")

# Instrumentación automática: latencia, throughput, status codes
instrumentator = Instrumentator(
    should_group_status_codes=True,     # Agrupa 2xx, 4xx, 5xx
    should_ignore_untemplated=True,     # Ignora rutas no declaradas
    excluded_handlers=["/health", "/metrics"],  # Excluye endpoints internos
)
instrumentator.instrument(app).expose(app, endpoint="/metrics")

# Métricas personalizadas para IA (requisito AI Act Art. 12)
llm_requests_total = Counter(
    "grc_llm_requests_total",
    "Total de llamadas a LLMs",
    ["provider", "model", "service_type"]
)
llm_latency_seconds = Histogram(
    "grc_llm_latency_seconds",
    "Latencia de llamadas a LLMs en segundos",
    ["provider", "model"],
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)
llm_tokens_total = Counter(
    "grc_llm_tokens_total",
    "Tokens consumidos por LLMs",
    ["provider", "model", "direction"]  # direction: input/output
)
celery_tasks_active = Gauge(
    "grc_celery_tasks_active",
    "Tareas Celery activas por cola",
    ["queue"]
)
