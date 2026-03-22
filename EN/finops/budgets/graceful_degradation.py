# Source: The FinOps Engineer and the Machine -- Chapter 11
# Pattern: Graceful degradation when budget exceeded

# services/graceful_degradation.py
from enum import Enum
from middleware.budget_enforcement import BudgetAction, BudgetExceededException

class DegradationStrategy(str, Enum):
    """Degradation strategy by service type."""
    INFORM_USER    = "inform_user"      # show message to user
    QUEUE_DEFERRED = "queue_deferred"   # queue for later processing
    STOP_SILENTLY  = "stop_silently"    # stop without visible impact

# Map of service to degradation strategy
SERVICE_DEGRADATION = {
    "chat_assistant":     DegradationStrategy.INFORM_USER,
    "proposal_section":   DegradationStrategy.QUEUE_DEFERRED,
    "index_updater":      DegradationStrategy.STOP_SILENTLY,
    "document_classifier": DegradationStrategy.QUEUE_DEFERRED,
    "risk_evaluator":     DegradationStrategy.INFORM_USER,
}

DEGRADATION_MESSAGES = {
    DegradationStrategy.INFORM_USER: (
        "The AI service is operating with reduced capacity. "
        "Responses may take longer than usual."
    ),
    DegradationStrategy.QUEUE_DEFERRED: (
        "The request has been queued and will be processed when "
        "capacity is available (maximum 24 hours)."
    ),
}

def handle_budget_exceeded(
    service_name: str,
    exc: BudgetExceededException,
) -> dict:
    """
    Handles an exhausted budget with gradual degradation
    instead of a generic error.
    """
    strategy = SERVICE_DEGRADATION.get(
        service_name, DegradationStrategy.QUEUE_DEFERRED
    )

    if strategy == DegradationStrategy.INFORM_USER:
        return {
            "status": "degraded",
            "message": DEGRADATION_MESSAGES[strategy],
            "retry_after_seconds": 300,
        }
    elif strategy == DegradationStrategy.QUEUE_DEFERRED:
        # Queue the task for deferred processing
        queue_for_later(service_name, exc.request_data)
        return {
            "status": "queued",
            "message": DEGRADATION_MESSAGES[strategy],
        }
    else:
        # STOP_SILENTLY: no message, the service simply stops
        return {"status": "stopped"}
