# Extraído de: LibroFinOps/cap-11-presupuestos-circuit-breakers.md
# tasks/budget_renewal.py
from celery import shared_task
from celery.schedules import crontab
from datetime import datetime
from models.budget_config import BudgetConfig, BudgetPeriod
import logging

logger = logging.getLogger(__name__)

# CELERYBEAT_SCHEDULE añade:
# "renew-daily-budgets":   crontab(hour=0, minute=1)
# "renew-weekly-budgets":  crontab(day_of_week=1, hour=0, minute=3)
# "renew-monthly-budgets": crontab(day_of_month=1, hour=0, minute=5)

@shared_task
def renew_budgets(period: str):
    """
    Reinicia el gasto acumulado de los presupuestos del periodo indicado.
    Preserva el historial: archiva el gasto del periodo anterior antes de reiniciar.
    """
    from database import get_db
    db = next(get_db())

    configs = db.query(BudgetConfig).filter(
        BudgetConfig.period == period,
        BudgetConfig.is_active == True,
    ).all()

    now = datetime.utcnow()
    renewed = 0

    for config in configs:
        # Archivar el periodo anterior (para histórico y auditoría)
        archive_budget_period(
            config_id=     config.id,
            period_start=  config.period_start,
            period_end=    now,
            total_spend=   config.current_spend_usd,
            limit_usd=     config.limit_usd,
        )

        # Registrar utilización antes de reiniciar
        utilization = config.current_spend_usd / config.limit_usd
        logger.info(
            "Renovación presupuesto '%s': gastado $%.2f de $%.2f (%.1f%%)",
            config.name, config.current_spend_usd,
            config.limit_usd, utilization * 100,
        )

        # Reiniciar el contador
        config.current_spend_usd = 0.0
        config.period_start      = now
        renewed += 1

    db.commit()

    # Generar informe de renovación para el dashboard
    generate_renewal_report(configs, now)

    return {"renewed": renewed, "period": period}


def generate_renewal_report(configs: list, timestamp: datetime):
    """
    Genera un informe de fin de periodo con las métricas clave.
    Se publica en el dashboard y se envía por correo al responsable.
    """
    report = {
        "timestamp": timestamp.isoformat(),
        "budgets": [],
    }
    over_budget = []

    for config in configs:
        utilization = config.current_spend_usd / config.limit_usd
        entry = {
            "name": config.name,
            "limit_usd": config.limit_usd,
            "spent_usd": config.current_spend_usd,
            "utilization_pct": round(utilization * 100, 1),
            "status": "over" if utilization > 1.0 else (
                "warning" if utilization > 0.80 else "ok"
            ),
        }
        report["budgets"].append(entry)

        if utilization > 1.0:
            over_budget.append(entry)

    if over_budget:
        # Notificar servicios que superaron el presupuesto
        notify_over_budget_report(over_budget)

    save_budget_report(report)
