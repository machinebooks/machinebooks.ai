# Extraído de: LibroFinOps/cap-09-cache-prompt-batch.md
# tasks/batch_processing.py
import anthropic
from celery import shared_task
from celery.schedules import crontab

# En celeryconfig.py:
# from celery.schedules import crontab
# CELERYBEAT_SCHEDULE = {
#   "process-nightly-batch": {
#     "task": "tasks.batch_processing.process_nightly_batch",
#     "schedule": crontab(hour=2, minute=0),  # 2:00 AM cada noche
#   },
#   "poll-batch-results": {
#     "task": "tasks.batch_processing.poll_all_pending_batches",
#     "schedule": crontab(minute="*/30"),     # cada 30 minutos
#   },
#   "weekly-summary-batch": {
#     "task": "tasks.batch_processing.generate_weekly_summaries",
#     "schedule": crontab(hour=3, minute=0, day_of_week=1),  # lunes 3:00 AM
#   },
#   "monthly-index-update": {
#     "task": "tasks.batch_processing.update_semantic_index",
#     "schedule": crontab(hour=4, minute=0, day_of_month=1),  # día 1, 4:00 AM
#   },
# }

client = anthropic.Anthropic()

@shared_task
def process_nightly_batch():
    """
    Envía al Batch API las tareas diferibles acumuladas durante el día.
    Se ejecuta a las 2:00 AM. El descuento es del 50 % sobre precio estándar.
    """
    pending_tasks = get_pending_batch_tasks()
    if not pending_tasks:
        return {"processed": 0}

    # Construir requests para el Batch API
    requests = []
    for task in pending_tasks:
        requests.append({
            "custom_id": str(task.id),   # para correlacionar respuestas
            "params": {
                "model": "claude-sonnet-4-6",
                "max_tokens": 2048,
                "system": task.system_prompt,
                "messages": [{"role": "user", "content": task.user_message}],
            },
        })

    batch = client.messages.batches.create(requests=requests)

    # Guardar el batch_id para el polling posterior
    register_batch_submission(
        batch_id=batch.id,
        task_ids=[t.id for t in pending_tasks],
    )

    return {"batch_id": batch.id, "count": len(requests)}


@shared_task(bind=True, max_retries=48)  # 48 reintentos x 30 min = 24 horas max
def poll_all_pending_batches(self):
    """Comprueba el estado de todos los batches en curso."""
    pending_batches = get_pending_batch_ids()

    for batch_id in pending_batches:
        batch = client.messages.batches.retrieve(batch_id)

        if batch.processing_status != "ended":
            continue  # aún procesando, comprobar en el próximo ciclo

        # Batch completado: procesar resultados
        for result in client.messages.batches.results(batch_id):
            if result.result.type == "succeeded":
                msg = result.result.message
                save_batch_result(
                    task_id=result.custom_id,
                    content=msg.content[0].text,
                    usage=msg.usage,
                    is_batch=True,  # para el cálculo de coste con descuento
                )
            else:
                # Reencolar tareas fallidas para procesamiento sincrono
                requeue_failed_task(result.custom_id)

        mark_batch_completed(batch_id)


@shared_task
def generate_weekly_summaries():
    """
    Genera resúmenes de actividad semanal para todos los proyectos activos.
    Se ejecuta los lunes a las 3:00 AM via Batch API.
    """
    active_projects = get_active_projects()
    if not active_projects:
        return {"processed": 0}

    requests = []
    for project in active_projects:
        activity = get_weekly_activity(project.id)
        requests.append({
            "custom_id": f"weekly-summary-{project.id}",
            "params": {
                "model": "claude-sonnet-4-6",
                "max_tokens": 1024,
                "system": "Genera un resumen ejecutivo de la actividad semanal.",
                "messages": [{"role": "user", "content": (
                    f"Proyecto: {project.name}\n"
                    f"Actividad de la semana:\n{activity}\n\n"
                    "Resume en 3-5 puntos clave para el equipo directivo."
                )}],
            },
        })

    batch = client.messages.batches.create(requests=requests)
    register_batch_submission(batch_id=batch.id, task_ids=[r["custom_id"] for r in requests])
    return {"batch_id": batch.id, "projects": len(requests)}
