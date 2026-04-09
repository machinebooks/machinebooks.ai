# Extracted from: LibroAISafety/ch-08-transparency.md
# transparency_report.py — Transparency report generation
from datetime import datetime, timedelta

def generate_transparency_report(
    systems: list[AISystemCard],
    period_start: datetime,
    period_end: datetime
) -> dict:
    """
    Generates an aggregated transparency report
    for all AI systems in production.
    """
    report = {
        "period": {
            "start": period_start.isoformat(),
            "end": period_end.isoformat()
        },
        "generated_at": datetime.utcnow().isoformat(),
        "summary": {
            "total_systems": len(systems),
            "by_tier": _count_by_tier(systems),
            "by_provider": _count_by_provider(systems),
            "total_daily_interactions": sum(
                s.daily_interactions for s in systems
            ),
            "systems_with_pii": sum(
                1 for s in systems if s.pii_processed
            ),
        },
        "compliance": {
            "cards_complete": sum(
                1 for s in systems 
                if s.compliance_status()["complete"]
            ),
            "security_evals_current": sum(
                1 for s in systems
                if _eval_is_current(s)
            ),
            "overdue_reviews": [
                s.system_name for s in systems
                if _review_is_overdue(s)
            ],
        },
        "incidents": {
            "total_30d": sum(
                s.incident_count_30d for s in systems
            ),
            "systems_with_incidents": [
                s.system_name for s in systems
                if s.incident_count_30d > 0
            ],
        },
        "limitations_acknowledged": {
            s.system_name: s.known_limitations
            for s in systems
            if s.known_limitations
        }
    }
    return report

def _count_by_tier(systems: list) -> dict:
    tiers = {}
    for s in systems:
        tiers[s.risk_tier] = tiers.get(s.risk_tier, 0) + 1
    return tiers

def _count_by_provider(systems: list) -> dict:
    providers = {}
    for s in systems:
        providers[s.model_provider] = (
            providers.get(s.model_provider, 0) + 1
        )
    return providers

def _eval_is_current(system: AISystemCard) -> bool:
    if not system.last_security_eval:
        return False
    max_age = {
        "tier_1": 90, "tier_2": 30, "tier_3": 7
    }.get(system.risk_tier, 90)
    age = (datetime.utcnow() - system.last_security_eval).days
    return age <= max_age

def _review_is_overdue(system: AISystemCard) -> bool:
    if not system.last_review_date:
        return True
    return not _eval_is_current(system)
