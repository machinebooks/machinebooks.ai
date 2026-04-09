# Extracted from: LibroAISafety/ch-07-responsible-scaling.md
# compliance_audit.py — Control verification by level
from datetime import datetime, timedelta

def audit_system_compliance(
    system_name: str,
    tier: RiskTier,
    controls_implemented: list[str],
    last_review_date: datetime
) -> dict:
    """
    Verifies that a system meets the mandatory controls
    for its risk level.
    """
    required = REQUIRED_CONTROLS[tier]
    missing = [c for c in required if c not in controls_implemented]
    
    # Verify review frequency by tier
    review_intervals = {
        RiskTier.TIER_1: timedelta(days=90),   # Quarterly
        RiskTier.TIER_2: timedelta(days=30),   # Monthly
        RiskTier.TIER_3: timedelta(days=7),    # Weekly
    }
    
    days_since_review = (datetime.utcnow() - last_review_date).days
    review_overdue = (
        datetime.utcnow() - last_review_date 
        > review_intervals[tier]
    )
    
    return {
        "system": system_name,
        "tier": tier.name,
        "compliant": len(missing) == 0 and not review_overdue,
        "missing_controls": missing,
        "review_overdue": review_overdue,
        "days_since_review": days_since_review,
        "next_review_due": (
            last_review_date + review_intervals[tier]
        ).isoformat(),
        "audit_timestamp": datetime.utcnow().isoformat()
    }

REQUIRED_CONTROLS = {
    RiskTier.TIER_1: [
        "content_filter_provider",
        "interaction_logging",
        "quarterly_usage_review"
    ],
    RiskTier.TIER_2: [
        "content_filter_provider",
        "interaction_logging",
        "quarterly_usage_review",
        "dedicated_guardrails",
        "monthly_audit",
        "prompt_injection_eval",
        "rbac_enforcement",
        "pii_detection"
    ],
    RiskTier.TIER_3: [
        "content_filter_provider",
        "interaction_logging",
        "quarterly_usage_review",
        "dedicated_guardrails",
        "monthly_audit",
        "prompt_injection_eval",
        "rbac_enforcement",
        "pii_detection",
        "human_in_the_loop",
        "pre_deployment_redteam",
        "realtime_monitoring",
        "execution_sandbox",
        "annual_external_audit"
    ]
}
