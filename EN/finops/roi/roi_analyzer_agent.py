# Source: The FinOps Engineer and the Machine -- Chapter 17
# Pattern: Agent for diagnosing ROI drops

# agents/roi_analyzer_agent.py — Automatic ROI drop diagnosis
import anthropic

client = anthropic.Anthropic()

def analyze_roi_anomaly(
    db, task_type: str, expected_roi: float,
    actual_roi: float, period_days: int = 7,
) -> str:
    """Uses Claude to analyze why ROI fell below the threshold."""
    from services.roi_tracker import ROITracker
    tracker = ROITracker(db)
    summary = tracker.get_summary(days=period_days)
    task_data = summary.get("by_task_type", {}).get(task_type, {})

    prompt = f"""Analyze the ROI drop in the '{task_type}' task.
Expected ROI: {expected_roi}:1 | Actual ROI: {actual_roi}:1
Completed tasks: {task_data.get('count', 0)}
LLM cost: EUR{task_data.get('llm_cost', 0):.2f}
Freed value: EUR{task_data.get('value', 0):.2f}

Possible causes: change in acceptance rate, increased supervision overhead,
LLM model change via routing, change in client complexity mix,
model quality degradation.

Provide diagnosis (maximum 200 words) with probable causes
and action recommendation for the FinOps team."""

    response = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text
