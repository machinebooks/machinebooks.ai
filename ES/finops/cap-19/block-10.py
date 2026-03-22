# Extraído de: LibroFinOps/cap-19-unit-economics.md
# Coste de la prueba gratuita como componente del CAC
def trial_cost_analysis(
    avg_users: float, cost_per_user_month: float,
    trial_days: int, conversion_rate: float,
    max_tokens: int = 50_000,
    price_per_token: float = 0.000003,
) -> dict:
    uncapped = avg_users * cost_per_user_month * (trial_days / 30)
    capped = max_tokens * price_per_token
    effective = min(uncapped, capped)
    return {
        "cost_per_trial_usd": round(effective, 2),
        "cac_from_trial_usd": round(effective / conversion_rate, 2),
        "savings_from_cap": round(uncapped - effective, 2),
    }
