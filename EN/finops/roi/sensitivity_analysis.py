# Source: The FinOps Engineer and the Machine -- Chapter 18
# Pattern: Automated sensitivity analysis

# Automated sensitivity analysis
def sensitivity_analysis(base_params: dict) -> list:
    """
    Calculates the impact of variations in each parameter
    on the business case's adjusted ROI.
    """
    variables = {
        "productivity_capture": [-0.20, -0.10, +0.10],
        "acceptance_rate": [-0.15, -0.10, +0.05],
        "llm_price_multiplier": [+0.40, +0.20, -0.20],
        "supervision_overhead": [+0.50, +0.25, -0.25],
        "human_minutes_reference": [-0.20, -0.10, +0.10],
    }
    results = []
    base_roi = calculate_roi_adjusted(base_params)

    for var_name, deltas in variables.items():
        for delta in deltas:
            modified = base_params.copy()
            modified[var_name] *= (1 + delta)
            modified_roi = calculate_roi_adjusted(modified)
            roi_change = (modified_roi - base_roi) / base_roi
            results.append({
                "variable": var_name,
                "delta_pct": round(delta * 100, 0),
                "roi_change_pct": round(roi_change * 100, 1),
            })
    return sorted(
        results, key=lambda x: abs(x["roi_change_pct"]),
        reverse=True,
    )
