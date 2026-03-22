# Extraído de: LibroFinOps/cap-20-policy-as-code.md
# services/budget_alert_service.py
import os
from celery import shared_task
from services.policy_reconciler import PolicyReconciler
from services.notification import NotificationService

@shared_task(name="check_budget_alerts", bind=True)
def check_budget_alerts(self):
    """
    Verifica todos los tenants activos contra sus umbrales.
    Envía alertas y ejecuta acciones según la política.
    Ejecutado cada 5 minutos por Celery Beat.

    Usa un lock distribuido en Redis para evitar ejecución
    concurrente por múltiples workers de Celery.
    """
    from redis import Redis
    redis = Redis.from_url(os.environ.get("REDIS_URL", "redis://redis:6379/0"))
    lock = redis.lock("check_budget_alerts_lock", timeout=240, blocking=False)

    if not lock.acquire(blocking=False):
        return {"status": "skipped", "reason": "Otro worker ya ejecuta esta tarea"}

    db = SessionLocal()
    try:
        reconciler = PolicyReconciler()
        notifier = NotificationService()

        tenants = db.query(Tenant).filter(
            Tenant.active == True
        ).all()

        for tenant in tenants:
            policy = reconciler.get_effective_policy(str(tenant.id))
            alert_config = policy.get("alerts", {})
            current_spend = get_current_month_spend(db, tenant.id)
            monthly_limit = (
                policy.get("budgets", {})
                .get("monthly_total_eur", 999999)
            )

            if monthly_limit <= 0:
                continue

            usage_ratio = current_spend / monthly_limit
            level = _get_alert_level(usage_ratio, alert_config)

            if level:
                _execute_alert_action(
                    tenant, level, usage_ratio, notifier, db
                )
    finally:
        db.close()
        try:
            lock.release()
        except Exception:
            pass  # El lock puede haber expirado


def _get_alert_level(
    usage_ratio: float, alert_config: dict
) -> str | None:
    """Determina el nivel de alerta según el ratio de uso."""
    if usage_ratio >= 1.00 and "budget_exhausted" in alert_config:
        return "budget_exhausted"
    elif usage_ratio >= 0.95 and "budget_critical" in alert_config:
        return "budget_critical"
    elif usage_ratio >= 0.85 and "budget_alert" in alert_config:
        return "budget_alert"
    elif usage_ratio >= 0.70 and "budget_warning" in alert_config:
        return "budget_warning"
    return None
