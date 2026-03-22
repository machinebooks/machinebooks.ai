# Source: The FinOps Engineer and the Machine -- Chapter 20
# Pattern: FinOps policy enforcement middleware

# middleware/finops_policy.py
from fastapi import Request, HTTPException
from services.policy_reconciler import PolicyReconciler
from services.spend_tracker import get_current_spend

reconciler = PolicyReconciler()


async def enforce_finops_policy(
    tenant_id: str,
    task_type: str,
    estimated_tokens: int,
    user_id: int,
) -> dict:
    """
    Executes the FinOps policy before each LLM call.
    Returns the approved model and applicable limits.
    Raises HTTPException if the request is blocked.
    """
    current_spend = await get_current_spend(tenant_id, task_type)

    decision = reconciler.check_request(
        tenant_id=tenant_id,
        task_type=task_type,
        estimated_tokens=estimated_tokens,
        current_spend_eur=current_spend,
    )

    if not decision["allowed"]:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "finops_policy_violation",
                "reason": decision["reason"],
                "action": decision["action"],
                "contact": "Contact administration to "
                           "review the budget.",
            },
        )

    # Model and limits determined by the policy, not by the client
    return {
        "approved_model": decision["model"],
        "max_output_tokens": decision.get("max_output_tokens", 2000),
        "budget_remaining_eur": decision.get("budget_remaining_eur"),
    }
