# Source: The FinOps Engineer and the Machine -- Chapter 8
# Pattern: Statistical sampling for routing quality

# tasks/routing_quality_sampling.py
import random
from celery import shared_task
import anthropic
from models.llm_usage_log import LLMUsageLog
import logging

logger = logging.getLogger(__name__)

QUALITY_JUDGE_PROMPT = """You are an AI response quality evaluator.

You are provided with:
1. An original PROMPT sent to an LLM model.
2. The RESPONSE produced by a lower-capability model.

Evaluate whether the RESPONSE is adequate for the PROMPT.

Criteria:
- Is the response factually correct?
- Does it cover all requested aspects?
- Is the level of detail sufficient for the task?
- Is the format as expected?

Respond with a JSON:
{{
  "quality": "acceptable" | "improvable" | "unacceptable",
  "reason": "brief explanation",
  "would_opus_differ": true | false
}}"""

SAMPLE_RATE = 0.05  # 5% of calls

@shared_task
def sample_and_evaluate():
    """
    Collects calls marked for quality audit
    and re-evaluates them with opus as judge.
    Estimated cost: $0.15-0.40 per daily execution.
    """
    client = anthropic.Anthropic()
    from database import get_db
    db = next(get_db())

    # Get calls marked for audit in the last 24h
    marked_logs = db.query(LLMUsageLog).filter(
        LLMUsageLog.quality_audit_pending == True,
        LLMUsageLog.model_tier.in_(["fast", "balanced"]),
    ).limit(30).all()  # maximum 30 evaluations per day

    results = {"acceptable": 0, "improvable": 0, "unacceptable": 0}
    problematic_services = []

    for log in marked_logs:
        try:
            response = client.messages.create(
                model="claude-opus-4-6",
                max_tokens=256,
                messages=[{"role": "user", "content": (
                    QUALITY_JUDGE_PROMPT
                    + f"\n\nPROMPT:\n{log.prompt_preview}\n\n"
                    + f"RESPONSE:\n{log.response_preview}"
                )}],
            )

            import json
            judgment = json.loads(response.content[0].text)
            quality = judgment.get("quality", "improvable")
            results[quality] = results.get(quality, 0) + 1

            # Record audit result
            log.quality_audit_result = quality
            log.quality_audit_pending = False

            if quality == "unacceptable":
                problematic_services.append({
                    "service": log.service_name,
                    "tier_used": log.model_tier,
                    "reason": judgment.get("reason", "no detail"),
                    "log_id": log.id,
                })

        except Exception as exc:
            logger.warning("Error evaluating log %d: %s", log.id, exc)
            log.quality_audit_pending = False

    db.commit()

    # If more than 20% of samples are unacceptable, alert
    total = sum(results.values())
    if total > 0 and results["unacceptable"] / total > 0.20:
        publish_quality_alert(
            message=(
                f"Routing quality alert: {results['unacceptable']} of "
                f"{total} samples evaluated as unacceptable."
            ),
            details=problematic_services,
        )

    return {
        "evaluated": total,
        "results": results,
        "problematic_services": len(problematic_services),
    }


def mark_for_quality_audit(log_id: int, db):
    """
    Marks a call for quality audit.
    Invoked from LLMService.complete() with probability SAMPLE_RATE.
    """
    if random.random() < SAMPLE_RATE:
        db.query(LLMUsageLog).filter(
            LLMUsageLog.id == log_id
        ).update({"quality_audit_pending": True})
