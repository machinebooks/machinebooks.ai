# Extraído de: LibroAIGateway/cap-34-celery-deployment-config.md
# celery_app.py — prioridad nativa Celery + Redis (rango 0-9)
celery_app.conf.update(
    task_queue_max_priority=9,   # rango de prioridad por mensaje
    task_default_priority=5,     # prioridad por defecto
    task_default_queue="default",
)
