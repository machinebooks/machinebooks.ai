# Source: The FinOps Engineer and the Machine -- Chapter 9
# Pattern: Batch processing with Anthropic Message Batches API

# tasks/batch_processing.py
import anthropic
from celery import shared_task
from celery.schedules import crontab

# In celeryconfig.py:
# from celery.schedules import crontab
# CELERYBEAT_SCHEDULE = {
#   "process-nightly-batch": {
#     "task": "tasks.batch_processing.process_nightly_batch",
#     "schedule": crontab(hour=2, minute=0),  # 2:00 AM every night
#   },
#   "poll-batch-results": {
#     "task": "tasks.batch_processing.poll_all_pending_batches",
#     "schedule": crontab(minute="*/30"),     # every 30 minutes
#   },
#   "weekly-summary-batch": {
#     "task": "tasks.batch_processing.generate_weekly_summaries",
#     "schedule": crontab(hour=3, minute=0, day_of_week=1),  # Monday 3:00 AM
#   },
#   "monthly-index-update": {
#     "task": "tasks.batch_processing.update_semantic_index",
#     "schedule": crontab(hour=4, minute=0, day_of_month=1),  # 1st of month, 4:00 AM
#   },
# }

client = anthropic.Anthropic()

@shared_task
def process_nightly_batch():
    """
    Sends deferrable tasks accumulated during the day to the Batch API.
    Runs at 2:00 AM. The discount is 50% off the standard price.
    """
    pending_tasks = get_pending_batch_tasks()
    if not pending_tasks:
        return {"processed": 0}

    # Build requests for the Batch API
    requests = []
    for task in pending_tasks:
        requests.append({
            "custom_id": str(task.id),   # for correlating responses
            "params": {
                "model": "claude-sonnet-4-6",
                "max_tokens": 2048,
                "system": task.system_prompt,
                "messages": [{"role": "user", "content": task.user_message}],
            },
        })

    batch = client.messages.batches.create(requests=requests)

    # Save the batch_id for subsequent polling
    register_batch_submission(
        batch_id=batch.id,
        task_ids=[t.id for t in pending_tasks],
    )

    return {"batch_id": batch.id, "count": len(requests)}


@shared_task(bind=True, max_retries=48)  # 48 retries x 30 min = 24 hours max
def poll_all_pending_batches(self):
    """Checks the status of all in-progress batches."""
    pending_batches = get_pending_batch_ids()

    for batch_id in pending_batches:
        batch = client.messages.batches.retrieve(batch_id)

        if batch.processing_status != "ended":
            continue  # still processing, check in the next cycle

        # Batch completed: process results
        for result in client.messages.batches.results(batch_id):
            if result.result.type == "succeeded":
                msg = result.result.message
                save_batch_result(
                    task_id=result.custom_id,
                    content=msg.content[0].text,
                    usage=msg.usage,
                    is_batch=True,  # for cost calculation with discount
                )
            else:
                # Re-queue failed tasks for synchronous processing
                requeue_failed_task(result.custom_id)

        mark_batch_completed(batch_id)


@shared_task
def generate_weekly_summaries():
    """
    Generates weekly activity summaries for all active projects.
    Runs Mondays at 3:00 AM via the Batch API.
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
                "system": "Generate an executive summary of the weekly activity.",
                "messages": [{"role": "user", "content": (
                    f"Project: {project.name}\n"
                    f"Activity for the week:\n{activity}\n\n"
                    "Summarize in 3-5 key points for the executive team."
                )}],
            },
        })

    batch = client.messages.batches.create(requests=requests)
    register_batch_submission(batch_id=batch.id, task_ids=[r["custom_id"] for r in requests])
    return {"batch_id": batch.id, "projects": len(requests)}
