# Extraído de: LibroFinOps/cap-18-business-case-cfo.md
# Generación de tabla TCO para el equipo financiero
def generate_tco_table(
    base_monthly_llm_cost: float,      # €312 en nuestro caso
    base_monthly_value: float,          # €42.800 ajustado
    engineering_year1: float,           # €47.500
    engineering_recurring: float,       # €8.000/año (mantenimiento)
    infra_annual: float,                # €18.000/año
    growth_rates: list,                 # [0.15, 0.08, 0.06, 0.05, 0.04]
) -> list:
    """Genera tabla TCO a 5 años con costes y beneficios."""
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
        # Crecimiento compuesto para el siguiente año
        monthly_cost *= (1 + growth) ** 12
        monthly_value *= (1 + growth) ** 12
    return rows
