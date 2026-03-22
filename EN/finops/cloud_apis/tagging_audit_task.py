# Source: The FinOps Engineer and the Machine -- Chapter 5
# Pattern: Celery task for periodic tag audit

# tasks/tagging_audit_task.py
from celery import shared_task
from .agents.tag_audit_agent import run_tag_audit_agent
import logging

logger = logging.getLogger(__name__)

@shared_task(name="weekly_tag_audit")
def weekly_tag_audit():
    """
    Weekly tag audit. Runs the Claude agent to identify
    untagged resources and propose corrections.
    Runs every Monday at 08:00 via Celery Beat.
    """
    regions = ["eu-west-1", "us-east-1"]  # Active project regions

    for region in regions:
        try:
            logger.info(f"Starting tag audit in {region}")
            report = run_tag_audit_agent(region=region)
            logger.info(f"Audit completed for {region}: {report[:200]}...")
            # In production: send the report to the FinOps team's Slack channel
            # notify_finops_channel(f"Tag audit {region}:\n{report}")
        except Exception as exc:
            logger.error(f"Error in tag audit ({region}): {exc}")
