# Extraído de: LibroFinOps/cap-19-unit-economics.md
# routers/unit_economics.py
@router.get("/")
def get_unit_economics(
    days: int = Query(30, ge=7, le=90),
    tenant_id: int = Query(None),
    db: Session = Depends(get_db),
    _=Depends(require_role(["admin", "finops", "cfo"])),
):
    """Calcula unit economics: coste por MAU, distribución, break-even."""
    calc = UnitEconomicsCalculator(db)
    report = calc.calculate(period_days=days, tenant_id=tenant_id)
    return {
        "period": {"start": report.period_start.isoformat(),
                    "end": report.period_end.isoformat(), "days": days},
        "users": {"total_active": report.total_active_users,
                  "distribution_by_profile": report.profile_distribution},
        "costs": {
            "total_llm_usd": report.total_llm_cost_usd,
            "avg_per_active_user_usd": report.avg_cost_per_active_user_usd,
            "by_profile_usd": report.cost_per_user_by_profile,
            "marginal_new_user_usd": report.marginal_cost_new_user_usd,
        },
        "saas_metrics": {
            "break_even_tenants": report.break_even_tenants,
            "infra_base_eur": calc.INFRA_BASE_COST_EUR,
        },
    }
