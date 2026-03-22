# Extraído de: LibroFinOps/cap-11-presupuestos-circuit-breakers.md
# api/budget_dashboard.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.budget_config import BudgetConfig

router = APIRouter(prefix="/api/budgets", tags=["budgets"])

@router.get("/status")
def get_all_budget_status(db: Session = Depends(get_db)):
    """
    Endpoint para el dashboard: estado actual de todos los presupuestos.
    El frontend muestra cada presupuesto como una barra de progreso
    con colores verde/amarillo/rojo según el nivel de utilización.
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
    """Determina el estado visual del presupuesto."""
    util = config.current_spend_usd / config.limit_usd
    if util >= config.block_threshold:
        return "blocked"
    elif util >= config.throttle_threshold:
        return "throttled"
    elif util >= config.alert_threshold:
        return "warning"
    return "ok"
