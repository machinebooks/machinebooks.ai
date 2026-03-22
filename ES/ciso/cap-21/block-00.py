# Extraído de: LibroCISO/cap-21-celery-async.md
from celery import Celery
from kombu import Queue, Exchange

# Broker y backend de resultados
REDIS_URL = "redis://redis:6379/0"
DATABASE_URL = "mysql+pymysql://grc_user:***@mysql:3306/grc_db"

app = Celery("grc_platform")

app.conf.update(
    # Broker: Redis
    broker_url=REDIS_URL,
    # Result backend: MySQL para persistencia
    result_backend=f"db+{DATABASE_URL}",
    result_extended=True,  # Almacena metadata adicional (nombre, args)

    # Serialización segura: JSON, nunca pickle
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],

    # Definición de colas
    task_queues=(
        Queue("ai", Exchange("ai"), routing_key="ai",
              queue_arguments={"x-max-length": 100}),
        Queue("email", Exchange("email"), routing_key="email",
              queue_arguments={"x-max-length": 500}),
        Queue("reports", Exchange("reports"), routing_key="reports",
              queue_arguments={"x-max-length": 50}),
        Queue("maintenance", Exchange("maintenance"), routing_key="maintenance",
              queue_arguments={"x-max-length": 20}),
        Queue("notifications", Exchange("notifications"), routing_key="notifications",
              queue_arguments={"x-max-length": 500}),
    ),

    # Routing: cada tarea va a su cola por nombre de módulo
    task_routes={
        "app.tasks.ai.*": {"queue": "ai"},
        "app.tasks.email.*": {"queue": "email"},
        "app.tasks.reports.*": {"queue": "reports"},
        "app.tasks.maintenance.*": {"queue": "maintenance"},
        "app.tasks.notifications.*": {"queue": "notifications"},
    },

    # Timeouts por defecto (se pueden sobreescribir por tarea)
    task_soft_time_limit=120,
    task_time_limit=180,

    # Prefetch: un worker solo toma una tarea a la vez
    # Evita que un worker acapare tareas mientras otra está bloqueada
    worker_prefetch_multiplier=1,

    # Timezone para Beat
    timezone="Europe/Madrid",
    enable_utc=True,
)
