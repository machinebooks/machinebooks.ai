# Extraído de: LibroConsultor/cap-22-unit-economics.md
def generate_comparison_report(economics: AugmentedEconomics) -> dict:
    """Genera informe comparativo antes/después de IA."""
    baseline = economics.baseline
    report = {
        "consultant": baseline.name,
        "baseline": {
            "annual_revenue": round(baseline.annual_revenue, 2),
            "loaded_cost": baseline.loaded_cost,
            "gross_margin": round(baseline.gross_margin, 2),
            "gross_margin_pct": f"{baseline.gross_margin_pct:.1%}",
            "billable_hours": baseline.billable_hours,
            "estimated_projects": round(economics._baseline_projects, 1),
        },
        "augmented": {
            "annual_revenue": round(economics.augmented_annual_revenue, 2),
            "total_cost": round(economics.augmented_total_cost, 2),
            "ai_stack_cost": round(
                economics.ai_cost.total_year(economics.year), 2
            ),
            "gross_margin": round(economics.augmented_gross_margin, 2),
            "gross_margin_pct": f"{economics.augmented_margin_pct:.1%}",
            "estimated_projects": round(economics.augmented_projects, 1),
            "hours_per_project": round(
                economics.augmented_hours_per_project, 1
            ),
        },
        "delta": {
            "revenue_change": f"{(economics.augmented_annual_revenue / baseline.annual_revenue - 1):.1%}",
            "margin_change_pp": round(
                (economics.augmented_margin_pct - baseline.gross_margin_pct) * 100, 1
            ),
            "roi_on_ai": f"{economics.roi_on_ai_investment:.1f}x",
            "breakeven_days": round(economics.breakeven_days, 0),
        },
    }
    return report

# Ejemplo de uso con datos escalados
consultant = ConsultantProfile(
    name="Consultor Senior A",
    annual_salary=52_000,
    loaded_cost=68_000,
    avg_bill_rate=105.0,
    actual_utilization=0.67,
)

ai_costs = AIStackCost(
    api_licenses_monthly=100,
    rag_infra_monthly=30,
    tools_monthly=20,
    first_year_training=3_200,
    first_year_setup=2_800,
)

econ = AugmentedEconomics(
    baseline=consultant,
    ai_cost=ai_costs,
    compression_factor=0.52,
    price_retention=0.80,
    year=1,
)

report = generate_comparison_report(econ)
print(json.dumps(report, indent=2, ensure_ascii=False))
