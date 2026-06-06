# Extracted from: LibroAIGateway/cap-34-celery-deployment-config.md
# celery_app.py — native Celery + Redis priority (range 0-9)
celery_app.conf.update(
    task_queue_max_priority=9,   # per-message priority range
    task_default_priority=5,     # default priority
    task_default_queue="default",
)
