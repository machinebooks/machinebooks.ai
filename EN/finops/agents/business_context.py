# Source: The FinOps Engineer and the Machine -- Chapter 13
# Pattern: Business context provider for anomaly analysis

# services/business_context.py
from datetime import datetime, date


def get_current_business_context() -> str:
    """
    Builds current business context to enrich the analysis.
    In production: connect with CI/CD system, CRM, and calendars.
    """
    context_parts = []
    today = date.today()

    # Recent deployments (integration with CI/CD system)
    recent_deployments = _get_recent_deployments()
    if recent_deployments:
        context_parts.append(
            f"Deployments in the last 24h: {', '.join(recent_deployments)}"
        )

    # Planned business events
    planned_events = _get_planned_events(today)
    if planned_events:
        context_parts.append(
            f"Planned events this week: {', '.join(planned_events)}"
        )

    # Monthly budget status
    budget_status = _get_budget_status()
    context_parts.append(
        f"Monthly budget: ${budget_status['total_budget']:.0f}, "
        f"consumed: {budget_status['pct_used']:.1f}% "
        f"(day {today.day} of the month)"
    )

    context_parts.append(
        f"Current day: {today.strftime('%A')} {today.strftime('%d/%m/%Y')}"
    )

    return "\n".join(context_parts) if context_parts else "No additional context"
