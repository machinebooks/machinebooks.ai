# Source: The FinOps Engineer and the Machine -- Chapter 19
# Pattern: Periodic unit economics monitoring task

# tasks/unit_economics_monitor.py
@shared_task(name="monitor_unit_economics")
def monitor_unit_economics():
    """Verifies daily that unit economics are in range."""
    db = SessionLocal()
    try:
        calc = UnitEconomicsCalculator(db)
        today = calc.calculate(period_days=1)
        baseline = calc.calculate(period_days=30)

        if baseline.avg_cost_per_active_user_usd > 0:
            ratio = (today.avg_cost_per_active_user_usd
                     / baseline.avg_cost_per_active_user_usd)
            if ratio > 1.50:
                notify_finops_team(
                    level="critical",
                    message=f"Cost per MAU today: "
                            f"${today.avg_cost_per_active_user_usd:.2f} "
                            f"({ratio:.0%} of average). Investigate.",
                )
            elif ratio > 1.20:
                notify_finops_team(level="warning",
                    message=f"Elevated cost per MAU: "
                            f"${today.avg_cost_per_active_user_usd:.2f}.")
    finally:
        db.close()
