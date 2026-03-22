# Extraído de: LibroFinOps/cap-10-selfhosted-vs-api.md
# tools/tco_analysis.py
from dataclasses import dataclass

@dataclass
class SelfHostedTCO:
    """Costes anuales de una configuración self-hosted."""
    gpu_capex_annual:      float  # amortización GPU/año
    electricity_annual:    float  # coste eléctrico/año
    hardware_other_annual: float  # servidor, red, rack/año
    ops_engineering_annual: float  # tiempo de ingeniería/año

@dataclass
class APIUsageProfile:
    """Perfil de uso de la API para un servicio."""
    monthly_operations:  int    # operaciones/mes
    avg_input_tokens:    int    # tokens de entrada por operación
    avg_output_tokens:   int    # tokens de salida por operación
    api_input_price:     float  # precio entrada por millón de tokens
    api_output_price:    float  # precio salida por millón de tokens

def calculate_breakeven(
    tco: SelfHostedTCO,
    profile: APIUsageProfile,
) -> dict:
    """
    Calcula el punto de cruce entre self-hosted y API.
    Devuelve el volumen mensual de operaciones donde se igualan los costes.
    """
    # Coste total anual del self-hosted (fijo, independiente del volumen)
    tco_annual = (
        tco.gpu_capex_annual
        + tco.electricity_annual
        + tco.hardware_other_annual
        + tco.ops_engineering_annual
    )

    # Coste por operación en la API
    cost_per_op = (
        profile.avg_input_tokens  / 1_000_000 * profile.api_input_price
        + profile.avg_output_tokens / 1_000_000 * profile.api_output_price
    )

    # Coste API anual al volumen actual
    current_annual_api_cost = (
        profile.monthly_operations * 12 * cost_per_op
    )

    # Volumen mensual de equilibrio
    breakeven_monthly = (tco_annual / 12) / cost_per_op

    # Factor de crecimiento necesario para alcanzar el breakeven
    growth_factor = breakeven_monthly / profile.monthly_operations

    return {
        "tco_annual":               tco_annual,
        "current_api_annual_cost":  current_annual_api_cost,
        "cost_per_operation_api":   cost_per_op,
        "breakeven_monthly_ops":    int(breakeven_monthly),
        "current_monthly_ops":      profile.monthly_operations,
        "growth_factor_needed":     round(growth_factor, 1),
        "self_hosted_cheaper_now":  current_annual_api_cost > tco_annual,
    }


# Ejemplo de uso con los datos de la Plataforma de Preventa
if __name__ == "__main__":
    tco = SelfHostedTCO(
        gpu_capex_annual=       4_000,   # A100, amortización 3 años
        electricity_annual=       735,   # GPU (420) + servidor (315)
        hardware_other_annual=  2_387,   # servidor (1.667) + refrigeración (480) + red (240)
        ops_engineering_annual= 4_020,   # 4h/mes × $80/h × 12 + downtime (180)
    )

    profile = APIUsageProfile(
        monthly_operations= 40_000,
        avg_input_tokens=      500,
        avg_output_tokens=      50,
        api_input_price=      0.80,  # claude-haiku-4-5
        api_output_price=     4.00,
    )

    result = calculate_breakeven(tco, profile)
    print(f"TCO anual self-hosted: ${result['tco_annual']:,.0f}")
    print(f"Coste API anual actual: ${result['current_api_annual_cost']:,.0f}")
    print(f"Breakeven en: {result['breakeven_monthly_ops']:,} ops/mes")
    print(f"Factor de crecimiento necesario: {result['growth_factor_needed']}x")
    print(f"¿Self-hosted más barato ahora? {result['self_hosted_cheaper_now']}")
