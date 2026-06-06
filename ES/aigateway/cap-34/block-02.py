# Extraído de: LibroAIGateway/cap-34-celery-deployment-config.md
@task_prerun.connect
def _on_task_prerun(task_id=None, task=None, **kwargs):
    logger.info("celery:task_prerun task=%s id=%s", task.name, task_id)

@task_postrun.connect
def _on_task_postrun(task_id=None, task=None, retval=None, state=None, **kwargs):
    logger.info("celery:task_postrun task=%s id=%s state=%s", task.name, task_id, state)

@task_failure.connect
def _on_task_failure(task_id=None, exception=None, traceback=None, einfo=None, **kwargs):
    logger.error("celery:task_failure id=%s exc=%s", task_id, exception)
