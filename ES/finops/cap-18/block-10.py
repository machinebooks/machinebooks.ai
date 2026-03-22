# Extraído de: LibroFinOps/cap-18-business-case-cfo.md
# Cálculo del NPV para el business case
def calculate_npv(
    monthly_net_flows: list,    # flujo neto mensual
    initial_investment: float,  # inversión inicial
    discount_rate_annual: float = 0.12,
) -> float:
    """
    Calcula el Valor Presente Neto del proyecto de IA.
    NPV positivo confirma que el proyecto crea valor.
    """
    monthly_rate = (1 + discount_rate_annual) ** (1/12) - 1
    npv = -initial_investment

    for month, flow in enumerate(monthly_net_flows, start=1):
        # Descontar cada flujo al valor presente
        present_value = flow / (1 + monthly_rate) ** month
        npv += present_value

    return round(npv, 2)

# Plataforma de Preventa con datos reales:
# Inversión: €47.500 | Flujo neto mensual: €12.000-€18.000
# NPV a 12 meses (tasa 12%): ~€85.000
# IRR (tasa interna de retorno): >400%
