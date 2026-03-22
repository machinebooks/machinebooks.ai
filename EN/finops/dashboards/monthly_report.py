# Source: The FinOps Engineer and the Machine -- Chapter 7
# Pattern: AI-generated monthly cost report

# services/monthly_report.py
import anthropic
import json
from .dashboard import get_cfo_metrics, get_pm_metrics

async def generate_monthly_narrative():
    """
    Generates a narrative monthly summary for leadership.
    Uses claude-haiku-4-5 for its low cost ($0.80/1M input tokens).
    """
    cfo_data = await get_cfo_metrics(months=3)
    pm_data = await get_pm_metrics(days=30)

    client = anthropic.Anthropic(api_key="<YOUR_API_KEY>")
    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": (
                "Generate a 3-paragraph executive summary "
                "about this month's AI spend. "
                "CFO data: "
                f"{json.dumps(cfo_data, ensure_ascii=False)}. "
                "Per-service data: "
                f"{json.dumps(pm_data, ensure_ascii=False)}. "
                "Business vocabulary, euros, no "
                "technical terms. Mention whether we are "
                "within budget and the trend."
            ),
        }],
    )
    return message.content[0].text
