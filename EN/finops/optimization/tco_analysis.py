# Source: The FinOps Engineer and the Machine -- Chapter 10
# Pattern: TCO calculator: self-hosted vs API deployment

# tools/tco_analysis.py
from dataclasses import dataclass

@dataclass
class SelfHostedTCO:
    """Annual costs of a self-hosted configuration."""
    gpu_capex_annual:      float  # GPU amortization/year
    electricity_annual:    float  # electricity cost/year
    hardware_other_annual: float  # server, network, rack/year
    ops_engineering_annual: float  # engineering time/year

@dataclass
class APIUsageProfile:
    """API usage profile for a service."""
    monthly_operations:  int    # operations/month
    avg_input_tokens:    int    # input tokens per operation
    avg_output_tokens:   int    # output tokens per operation
    api_input_price:     float  # input price per million tokens
    api_output_price:    float  # output price per million tokens

def calculate_breakeven(
    tco: SelfHostedTCO,
    profile: APIUsageProfile,
) -> dict:
    """
    Calculates the crossover point between self-hosted and API.
    Returns the monthly operation volume where costs equalize.
    """
    # Total annual self-hosted cost (fixed, independent of volume)
    tco_annual = (
        tco.gpu_capex_annual
        + tco.electricity_annual
        + tco.hardware_other_annual
        + tco.ops_engineering_annual
    )

    # Cost per operation on the API
    cost_per_op = (
        profile.avg_input_tokens  / 1_000_000 * profile.api_input_price
        + profile.avg_output_tokens / 1_000_000 * profile.api_output_price
    )

    # Annual API cost at current volume
    current_annual_api_cost = (
        profile.monthly_operations * 12 * cost_per_op
    )

    # Monthly breakeven volume
    breakeven_monthly = (tco_annual / 12) / cost_per_op

    # Growth factor needed to reach breakeven
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


# Example usage with the Presales Platform data
if __name__ == "__main__":
    tco = SelfHostedTCO(
        gpu_capex_annual=       4_000,   # A100, 3-year amortization
        electricity_annual=       735,   # GPU (420) + server (315)
        hardware_other_annual=  2_387,   # server (1,667) + cooling (480) + network (240)
        ops_engineering_annual= 4_020,   # 4h/month x $80/h x 12 + downtime (180)
    )

    profile = APIUsageProfile(
        monthly_operations= 40_000,
        avg_input_tokens=      500,
        avg_output_tokens=      50,
        api_input_price=      0.80,  # claude-haiku-4-5
        api_output_price=     4.00,
    )

    result = calculate_breakeven(tco, profile)
    print(f"Annual self-hosted TCO: ${result['tco_annual']:,.0f}")
    print(f"Current annual API cost: ${result['current_api_annual_cost']:,.0f}")
    print(f"Breakeven at: {result['breakeven_monthly_ops']:,} ops/month")
    print(f"Growth factor needed: {result['growth_factor_needed']}x")
    print(f"Self-hosted cheaper now? {result['self_hosted_cheaper_now']}")
