# Extraído de: LibroAIGateway/cap-34-celery-deployment-config.md
@celery_app.task(
    name="app.tasks.llm_tasks.run_llm_task",
    queue="llm",
    max_retries=3,
    default_retry_delay=60,
    retry_backoff=True,
    retry_backoff_max=300,
)
def run_llm_task(deployment_id: str, prompt_hash: str) -> dict:
    ...
