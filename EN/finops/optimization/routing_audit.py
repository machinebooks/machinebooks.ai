# Source: The FinOps Engineer and the Machine -- Chapter 8
# Pattern: Routing audit task -- validate quality per model

# tasks/routing_audit.py
import random
from celery import shared_task
import anthropic
from models.llm_usage_log import LLMUsageLog

AUDIT_SAMPLE_SIZE = 50  # calls per week

JUDGE_PROMPT = """Classify the following LLM task into one of these levels:
- FAST: classification, extraction, validation, binary response
- BALANCED: guided generation, summary, analysis with defined criteria
- POWERFUL: complex reasoning, unprecedented decisions, open-ended analysis

Prompt analyzed:
{prompt}

Respond only with: FAST, BALANCED, or POWERFUL."""

@shared_task
def audit_routing_sample():
    """
    Evaluates a sample of calls to detect suboptimal routing.
    Uses claude-haiku-4-5 as judge (low audit cost).
    """
    client = anthropic.Anthropic()
    # Get random sample from the last week
    recent_logs = get_recent_llm_logs(days=7, limit=500)
    sample = random.sample(recent_logs, min(AUDIT_SAMPLE_SIZE, len(recent_logs)))

    mismatches = []
    for log in sample:
        response = client.messages.create(
            model="claude-haiku-4-5",  # economical judge
            max_tokens=10,
            messages=[{"role": "user", "content": JUDGE_PROMPT.format(
                prompt=log.prompt_preview  # first 500 chars
            )}],
        )
        judge_tier = response.content[0].text.strip()
        actual_tier = log.model_tier  # tier used in production

        if judge_tier != actual_tier:
            mismatches.append({
                "log_id": log.id,
                "service": log.service_name,
                "actual": actual_tier,
                "suggested": judge_tier,
            })

    # Publish result to the audit dashboard
    publish_routing_audit(mismatches, sample_size=len(sample))
    return len(mismatches)
