# Source: The FinOps Engineer and the Machine -- Chapter 19
# Pattern: Usage engagement monitoring

# services/engagement_monitor.py
class EngagementMonitor:
    """Detects tenants at risk of silent churn due to low usage rate."""

    def get_engagement_report(self, db: Session, days: int = 30) -> list:
        cutoff = datetime.utcnow() - timedelta(days=days)
        results = []

        for tenant in db.query(Tenant).filter(Tenant.active == True).all():
            total = db.query(func.count(User.id)).filter(
                User.tenant_id == tenant.id, User.active == True
            ).scalar() or 0
            active = db.query(func.count(distinct(LLMUsageLog.user_id))).filter(
                LLMUsageLog.tenant_id == tenant.id,
                LLMUsageLog.created_at >= cutoff,
            ).scalar() or 0

            rate = active / total if total > 0 else 0
            results.append({
                "tenant_id": tenant.id,
                "total_users": total,
                "active_users_30d": active,
                "engagement_rate": round(rate, 3),
                "risk": "high" if rate < 0.20 else "medium" if rate < 0.40 else "low",
            })
        return sorted(results, key=lambda x: x["engagement_rate"])
