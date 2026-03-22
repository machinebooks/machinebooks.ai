# Extraído de: LibroFinOps/cap-19-unit-economics.md
@router.get("/pricing-simulation")
def simulate_pricing(
    target_margin: float = Query(0.70, ge=0.30, le=0.95),
    avg_users_per_tenant: int = Query(5, ge=1, le=50),
    num_tenants: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
    _=Depends(require_role(["admin", "finops", "cfo"])),
):
    """Simula el precio por tenant para alcanzar el margen objetivo."""
    calc = UnitEconomicsCalculator(db)
    report = calc.calculate(period_days=30)

    avg_cost = report.avg_cost_per_active_user_usd * 1.10  # buffer 10%
    cost_per_tenant = (avg_cost * avg_users_per_tenant) + calc.TENANT_OVERHEAD_EUR
    total_cost = (cost_per_tenant * num_tenants) + calc.INFRA_BASE_COST_EUR
    revenue_needed = total_cost / (1 - target_margin)
    price_per_tenant = revenue_needed / num_tenants

    return {
        "cost_per_tenant_usd": round(cost_per_tenant, 2),
        "min_price_per_tenant_usd": round(price_per_tenant, 2),
        "recommended_with_buffer_usd": round(price_per_tenant * 1.15, 2),
        "break_even_tenants": report.break_even_tenants,
    }
