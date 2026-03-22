# Source: The FinOps Engineer and the Machine -- Chapter 8
# Pattern: Quality monitoring for routed requests

# tasks/routing_quality_monitor.py
from celery import shared_task
from dataclasses import dataclass
from datetime import datetime, timedelta
from sqlalchemy import func
from models.llm_usage_log import LLMUsageLog
from models.llm_config import LLMServiceConfig
import logging

logger = logging.getLogger(__name__)

# In celeryconfig.py:
# CELERYBEAT_SCHEDULE = {
#   "routing-quality-daily": {
#     "task": "tasks.routing_quality_monitor.compute_routing_metrics",
#     "schedule": crontab(hour=6, minute=0),  # 6:00 AM every day
#   },
# }

@dataclass
class RoutingMetrics:
    """Daily routing quality metrics by service."""
    service_name: str
    date: str
    total_calls: int
    tier_distribution: dict[str, int]   # {"fast": 120, "balanced": 45}
    avg_cost_per_call: float
    avg_latency_ms: float
    downgrade_count: int        # times the heuristic lowered the tier
    upgrade_count: int          # times the heuristic raised the tier
    # Indirect quality metrics
    retry_rate: float           # % of calls that needed a retry
    user_edit_rate: float       # % of outputs manually edited by the user

@shared_task
def compute_routing_metrics():
    """
    Computes daily routing metrics for each service.
    Detects quality degradations and optimization opportunities.
    """
    from database import get_db
    db = next(get_db())

    yesterday = datetime.utcnow().date() - timedelta(days=1)

    # Get all services with routing config
    services = db.query(LLMServiceConfig).all()

    alerts = []
    for svc in services:
        metrics = _compute_service_metrics(db, svc.service_name, yesterday)

        # Alert 1: high retry rate → possible excessive downgrade
        if metrics.retry_rate > 0.15:
            alerts.append({
                "service": svc.service_name,
                "type": "high_retry_rate",
                "value": f"{metrics.retry_rate*100:.1f}%",
                "suggestion": "Consider upgrading the default tier",
            })

        # Alert 2: high manual edit rate → insufficient quality
        if metrics.user_edit_rate > 0.40:
            alerts.append({
                "service": svc.service_name,
                "type": "high_edit_rate",
                "value": f"{metrics.user_edit_rate*100:.1f}%",
                "suggestion": "Output requires frequent human revision",
            })

        # Alert 3: average cost per call exceeds expected threshold
        expected_cost = _expected_cost_for_tier(svc.default_tier)
        if metrics.avg_cost_per_call > expected_cost * 2.0:
            alerts.append({
                "service": svc.service_name,
                "type": "cost_above_expected",
                "value": f"${metrics.avg_cost_per_call:.4f} vs ${expected_cost:.4f}",
                "suggestion": "Review whether frequent upgrades are justified",
            })

        # Persist metrics for historical dashboards
        save_routing_metrics(metrics)

    if alerts:
        publish_routing_alerts(alerts)

    return {"services_analyzed": len(services), "alerts": len(alerts)}


def _compute_service_metrics(db, service_name: str, date) -> RoutingMetrics:
    """Aggregates metrics for a service on a given day."""
    logs = db.query(LLMUsageLog).filter(
        LLMUsageLog.service_name == service_name,
        func.date(LLMUsageLog.created_at) == date,
    ).all()

    if not logs:
        return RoutingMetrics(
            service_name=service_name, date=str(date),
            total_calls=0, tier_distribution={},
            avg_cost_per_call=0, avg_latency_ms=0,
            downgrade_count=0, upgrade_count=0,
            retry_rate=0, user_edit_rate=0,
        )

    tier_dist = {}
    for log in logs:
        tier_dist[log.model_tier] = tier_dist.get(log.model_tier, 0) + 1

    total_cost = sum(log.cost_usd for log in logs)
    total_latency = sum(log.latency_ms for log in logs if log.latency_ms)
    retries = sum(1 for log in logs if log.is_retry)
    edits = sum(1 for log in logs if log.user_edited)

    return RoutingMetrics(
        service_name=service_name,
        date=str(date),
        total_calls=len(logs),
        tier_distribution=tier_dist,
        avg_cost_per_call=total_cost / len(logs),
        avg_latency_ms=total_latency / len(logs) if logs else 0,
        downgrade_count=sum(1 for l in logs if l.routing_action == "downgrade"),
        upgrade_count=sum(1 for l in logs if l.routing_action == "upgrade"),
        retry_rate=retries / len(logs),
        user_edit_rate=edits / len(logs),
    )
