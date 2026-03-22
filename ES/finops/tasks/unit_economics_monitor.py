# Extraído de: LibroFinOps/cap-19-unit-economics.md
# tasks/unit_economics_monitor.py
@shared_task(name="monitor_unit_economics")
def monitor_unit_economics():
    """Verifica diariamente que los unit economics están en rango."""
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
                    message=f"Coste por MAU hoy: "
                            f"${today.avg_cost_per_active_user_usd:.2f} "
                            f"({ratio:.0%} del promedio). Investigar.",
                )
            elif ratio > 1.20:
                notify_finops_team(level="warning",
                    message=f"Coste por MAU elevado: "
                            f"${today.avg_cost_per_active_user_usd:.2f}.")
    finally:
        db.close()
