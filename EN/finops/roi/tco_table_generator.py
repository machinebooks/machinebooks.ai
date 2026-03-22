# Source: The FinOps Engineer and the Machine -- Chapter 18
# Pattern: TCO table generator for finance team

# 5-year TCO table generation for the finance team
def generate_tco_table(
    base_monthly_llm_cost: float,      # EUR312 in our case
    base_monthly_value: float,          # EUR42,800 adjusted
    engineering_year1: float,           # EUR47,500
    engineering_recurring: float,       # EUR8,000/year (maintenance)
    infra_annual: float,                # EUR18,000/year
    growth_rates: list,                 # [0.15, 0.08, 0.06, 0.05, 0.04]
) -> list:
    """Generates 5-year TCO table with costs and benefits."""
    rows = []
    monthly_cost = base_monthly_llm_cost
    monthly_value = base_monthly_value

    for year, growth in enumerate(growth_rates, start=1):
        annual_llm = monthly_cost * 12
        eng = engineering_year1 if year == 1 else engineering_recurring
        total_cost = annual_llm + eng + infra_annual
        annual_value = monthly_value * 12
        rows.append({
            "year": year,
            "llm_cost_eur": round(annual_llm, 0),
            "engineering_eur": round(eng, 0),
            "infra_eur": round(infra_annual, 0),
            "total_cost_eur": round(total_cost, 0),
            "value_eur": round(annual_value, 0),
            "net_value_eur": round(annual_value - total_cost, 0),
        })
        # Compound growth for the next year
        monthly_cost *= (1 + growth) ** 12
        monthly_value *= (1 + growth) ** 12
    return rows
