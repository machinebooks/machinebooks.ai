# Source: The FinOps Engineer and the Machine -- Chapter 18
# Pattern: NPV calculation for business case

# NPV calculation for the business case
def calculate_npv(
    monthly_net_flows: list,    # monthly net flow
    initial_investment: float,  # initial investment
    discount_rate_annual: float = 0.12,
) -> float:
    """
    Calculates the Net Present Value of the AI project.
    Positive NPV confirms the project creates value.
    """
    monthly_rate = (1 + discount_rate_annual) ** (1/12) - 1
    npv = -initial_investment

    for month, flow in enumerate(monthly_net_flows, start=1):
        # Discount each flow to present value
        present_value = flow / (1 + monthly_rate) ** month
        npv += present_value

    return round(npv, 2)

# Presales Platform with real data:
# Investment: EUR47,500 | Monthly net flow: EUR12,000-EUR18,000
# NPV at 12 months (12% rate): ~EUR85,000
# IRR (internal rate of return): >400%
