# Extraído de: LibroCISO/cap-24-calidad-ia.md
from fastapi import APIRouter, Depends, Query
from datetime import datetime, timedelta
from sqlalchemy import func
from typing import Optional

router = APIRouter(prefix="/api/v1/admin/ai", tags=["ai-monitoring"])

@router.get("/monitoring/dashboard")
async def get_ai_monitoring_dashboard(
    period: str = Query('7d', regex='^(24h|7d|30d|90d)$'),
    service_type: Optional[str] = None,
    current_user = Depends(require_role('admin')),
    db = Depends(get_db),
):
    """Dashboard de monitorización de IA para el CISO/Admin.

    Devuelve:
    - Resumen de estado (métricas en warning/alert/critical)
    - Métricas agregadas del período seleccionado
    - Tendencias por servicio
    - Alertas activas
    - Coste acumulado vs presupuesto
    """
    period_map = {
        '24h': timedelta(hours=24),
        '7d': timedelta(days=7),
        '30d': timedelta(days=30),
        '90d': timedelta(days=90),
    }
    cutoff = datetime.utcnow() - period_map[period]

    # ── Estado general ──
    active_alerts = db.query(AIMonitoringMetric).filter(
        AIMonitoringMetric.created_at >= cutoff,
        AIMonitoringMetric.status.in_(['warning', 'alert', 'critical']),
    )
    if service_type:
        active_alerts = active_alerts.filter(
            AIMonitoringMetric.service_type == service_type
        )
    alerts = active_alerts.all()

    # ── Métricas más recientes por servicio ──
    # Subconsulta: última métrica de cada (metric_name, service_type)
    latest_metrics = db.query(
        AIMonitoringMetric.metric_name,
        AIMonitoringMetric.service_type,
        func.max(AIMonitoringMetric.created_at).label('max_date'),
    ).filter(
        AIMonitoringMetric.created_at >= cutoff,
    ).group_by(
        AIMonitoringMetric.metric_name,
        AIMonitoringMetric.service_type,
    ).all()

    metrics_detail = []
    for m_name, s_type, max_date in latest_metrics:
        metric = db.query(AIMonitoringMetric).filter(
            AIMonitoringMetric.metric_name == m_name,
            AIMonitoringMetric.service_type == s_type,
            AIMonitoringMetric.created_at == max_date,
        ).first()
        if metric:
            metrics_detail.append({
                'metric_name': metric.metric_name,
                'service_type': metric.service_type,
                'value': metric.value,
                'status': metric.status,
                'trend': metric.trend,
                'trend_delta_pct': metric.trend_delta_pct,
                'sample_size': metric.sample_size,
                'period': metric.period_type,
            })

    # ── Coste vs presupuesto ──
    month_start = datetime.utcnow().replace(
        day=1, hour=0, minute=0, second=0
    )
    monthly_cost = db.query(
        func.sum(LLMUsageLog.cost_total)
    ).filter(
        LLMUsageLog.created_at >= month_start,
    ).scalar() or 0.0

    budget = db.query(BudgetConfig).filter_by(is_active=True).first()
    budget_pct = (
        (monthly_cost / budget.monthly_budget_usd * 100)
        if budget and budget.monthly_budget_usd
        else None
    )

    return {
        'period': period,
        'summary': {
            'total_alerts': len(alerts),
            'critical': sum(1 for a in alerts if a.status == 'critical'),
            'alert': sum(1 for a in alerts if a.status == 'alert'),
            'warning': sum(1 for a in alerts if a.status == 'warning'),
        },
        'metrics': metrics_detail,
        'cost': {
            'monthly_total_usd': round(monthly_cost, 2),
            'monthly_budget_usd': budget.monthly_budget_usd if budget else None,
            'budget_used_pct': round(budget_pct, 1) if budget_pct else None,
            'action_on_limit': budget.action_on_limit if budget else None,
        },
        'alerts': [
            {
                'metric_name': a.metric_name,
                'service_type': a.service_type,
                'value': a.value,
                'status': a.status,
                'threshold_breached': (
                    a.threshold_critical if a.status == 'critical'
                    else a.threshold_alert if a.status == 'alert'
                    else a.threshold_warning
                ),
                'period_start': a.period_start.isoformat(),
            }
            for a in alerts
        ],
    }
