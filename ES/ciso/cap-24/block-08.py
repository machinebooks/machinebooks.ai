# Extraído de: LibroCISO/cap-24-calidad-ia.md
@shared_task(queue='maintenance', name='ai.check_budget_alerts')
def check_budget_alerts():
    """Verifica si el gasto IA ha superado los umbrales de presupuesto.

    Se ejecuta cada hora vía Celery Beat.
    Si el gasto supera el umbral de alerta (default 80%),
    genera una notificación. Si supera el 100%, aplica
    la acción configurada (alert/throttle/block).
    """
    from app.database import db_session
    from app.models import BudgetConfig, LLMUsageLog
    from app.notifications import send_admin_notification
    from sqlalchemy import func

    budget = db_session.query(BudgetConfig).filter_by(
        is_active=True
    ).first()

    if not budget or not budget.monthly_budget_usd:
        return {'status': 'no_budget_configured'}

    # Coste acumulado del mes actual
    month_start = datetime.utcnow().replace(
        day=1, hour=0, minute=0, second=0
    )
    monthly_cost = db_session.query(
        func.sum(LLMUsageLog.cost_total)
    ).filter(
        LLMUsageLog.created_at >= month_start,
    ).scalar() or 0.0

    budget_pct = (monthly_cost / budget.monthly_budget_usd) * 100

    if budget_pct >= 100:
        # Presupuesto superado: aplicar acción configurada
        if budget.action_on_limit == 'throttle':
            _activate_throttle_mode(db_session)
        elif budget.action_on_limit == 'block':
            _activate_block_mode(db_session)

        send_admin_notification(
            title='Presupuesto IA superado',
            message=f'El gasto mensual de IA ({monthly_cost:.2f} USD) '
                    f'ha superado el presupuesto '
                    f'({budget.monthly_budget_usd:.2f} USD). '
                    f'Acción aplicada: {budget.action_on_limit}.',
            severity='critical',
        )
    elif budget_pct >= budget.alert_threshold_pct:
        send_admin_notification(
            title='Alerta de presupuesto IA',
            message=f'El gasto mensual de IA alcanza el '
                    f'{budget_pct:.1f}% del presupuesto '
                    f'({monthly_cost:.2f} / '
                    f'{budget.monthly_budget_usd:.2f} USD).',
            severity='warning',
        )

    return {
        'monthly_cost_usd': round(monthly_cost, 2),
        'budget_usd': budget.monthly_budget_usd,
        'budget_pct': round(budget_pct, 1),
        'action': budget.action_on_limit,
    }
