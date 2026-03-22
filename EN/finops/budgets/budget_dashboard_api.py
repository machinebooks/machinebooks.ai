# Source: The FinOps Engineer and the Machine -- Chapter 11
# Pattern: Budget dashboard API

# api/budget_dashboard.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.budget_config import BudgetConfig

router = APIRouter(prefix="/api/budgets", tags=["budgets"])

@router.get("/status")
def get_all_budget_status(db: Session = Depends(get_db)):
    """
    Dashboard endpoint: current status of all budgets.
    The frontend displays each budget as a progress bar
    with green/yellow/red colors based on utilization level.
    """
    configs = db.query(BudgetConfig).filter(
        BudgetConfig.is_active == True
    ).all()

    return [
        {
            "name":           c.name,
            "scope":          c.scope.value,
            "scope_id":       c.scope_id,
            "period":         c.period.value,
            "limit_usd":      c.limit_usd,
            "current_usd":    c.current_spend_usd,
            "utilization":    round(c.current_spend_usd / c.limit_usd, 3),
            "status":         _budget_status(c),
            "period_start":   c.period_start.isoformat() if c.period_start else None,
            "alert_at":       c.alert_threshold,
            "throttle_at":    c.throttle_threshold,
            "block_at":       c.block_threshold,
        }
        for c in configs
    ]

def _budget_status(config: BudgetConfig) -> str:
    """Determines the visual status of the budget."""
    util = config.current_spend_usd / config.limit_usd
    if util >= config.block_threshold:
        return "blocked"
    elif util >= config.throttle_threshold:
        return "throttled"
    elif util >= config.alert_threshold:
        return "warning"
    return "ok"
