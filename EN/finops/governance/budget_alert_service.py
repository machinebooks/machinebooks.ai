# Source: The FinOps Engineer and the Machine -- Chapter 20
# Pattern: Budget alert service with escalation

# services/budget_alert_service.py
from celery import shared_task
from services.policy_reconciler import PolicyReconciler
from services.notification import NotificationService

@shared_task(name="check_budget_alerts")
def check_budget_alerts():
    """
    Checks all active tenants against their thresholds.
    Sends alerts and executes actions according to the policy.
    Executed every 5 minutes by Celery Beat.
    """
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


def _get_alert_level(
    usage_ratio: float, alert_config: dict
) -> str | None:
    """Determines the alert level based on the usage ratio."""
    if usage_ratio >= 1.00 and "budget_exhausted" in alert_config:
        return "budget_exhausted"
    elif usage_ratio >= 0.95 and "budget_critical" in alert_config:
        return "budget_critical"
    elif usage_ratio >= 0.85 and "budget_alert" in alert_config:
        return "budget_alert"
    elif usage_ratio >= 0.70 and "budget_warning" in alert_config:
        return "budget_warning"
    return None
