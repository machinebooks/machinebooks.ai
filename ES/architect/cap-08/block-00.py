# Extraído de: LibroTecnico/cap-08-colas-trabajo.md
# Ejemplo didáctico: configuración central de Celery
# Patrón: workers/celery_config.py

from kombu import Queue, Exchange

# Intercambio directo para todos los tipos de cola
default_exchange = Exchange("default", type="direct")

# Definición explícita de todas las colas con su exchange
CELERY_QUEUES = (
    Queue("default",    default_exchange, routing_key="default"),
    Queue("priority",   default_exchange, routing_key="priority"),
    Queue("ai",         default_exchange, routing_key="ai"),
    Queue("documents",  default_exchange, routing_key="documents"),
    Queue("sync",       default_exchange, routing_key="sync"),
    Queue("crm",        default_exchange, routing_key="crm"),
    Queue("automation", default_exchange, routing_key="automation"),
)

CELERY_DEFAULT_QUEUE = "default"
CELERY_DEFAULT_EXCHANGE = "default"
CELERY_DEFAULT_ROUTING_KEY = "default"

# Rate limiting por tipo de tarea
CELERY_ANNOTATIONS = {
    # Tareas IA: máximo 30 llamadas por minuto al modelo
    "tasks.ai.*": {"rate_limit": "30/m"},
    # Tareas de automatización: máximo 5 sesiones concurrentes
    "tasks.automation.*": {"rate_limit": "5/m"},
    # Procesamiento de documentos: 10 por minuto
    "tasks.documents.*": {"rate_limit": "10/m"},
}

# Configuración de resultados en Redis
# En producción: URL con autenticación desde variable de entorno
CELERY_RESULT_BACKEND = os.environ["CELERY_RESULT_BACKEND"]
CELERY_BROKER_URL = os.environ["CELERY_BROKER_URL"]
CELERY_RESULT_EXPIRES = 3600  # Resultados disponibles 1 hora

# Serialización JSON (más segura que pickle)
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]

# Visibilidad de tareas: el broker retiene la tarea
# hasta que el worker confirma que la ha procesado
CELERY_ACKS_LATE = True
CELERY_REJECT_ON_WORKER_LOST = True
