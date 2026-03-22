# Source: The FinOps Engineer and the Machine -- Chapter 19
# Pattern: LTV with non-uniform churn (survival model)

# LTV calculation with non-uniform churn (survival model)
def calculate_adjusted_ltv(
    monthly_revenue: float,
    gross_margin: float,
    churn_by_month: list,  # [0.12, 0.08, 0.05, 0.03, 0.03, ...]
) -> dict:
    """LTV that considers variable churn by client age."""
    survival = 1.0
    total_ltv = 0.0
    for month, churn in enumerate(churn_by_month, start=1):
        monthly_value = monthly_revenue * gross_margin * survival
        total_ltv += monthly_value
        survival *= (1 - churn)

    avg_churn = sum(churn_by_month) / len(churn_by_month)
    simple_ltv = monthly_revenue * gross_margin / avg_churn
    return {
        "adjusted_ltv": round(total_ltv, 2),
        "simple_ltv": round(simple_ltv, 2),
        "delta_pct": round((total_ltv - simple_ltv) / simple_ltv * 100, 1),
    }

# Result with our data:
# churn_by_month = [0.12, 0.08, 0.05, 0.03, 0.03, 0.03, ...]
# Simple LTV (average 4% churn): EUR862
# Adjusted LTV: ~EUR1,380 (+60% vs. simple)
