# Extracted from: LibroAISafety/ch-13-prompt-injection.md
# Calculation of the operational cost of a prompt injection classifier
# Didactic code to illustrate the trade-off

def calculate_classifier_impact(
    daily_requests: int,
    attack_percentage: float,      # % of requests that are attacks
    detection_rate: float,          # True positive rate
    false_positive_rate: float,     # False positive rate
) -> dict:
    """
    Calculates the operational impact of a prompt injection classifier.
    """
    attacks = int(daily_requests * attack_percentage)
    legitimate = daily_requests - attacks

    attacks_blocked = int(attacks * detection_rate)
    attacks_missed = attacks - attacks_blocked
    legitimate_blocked = int(legitimate * false_positive_rate)

    return {
        "attacks_blocked_per_day": attacks_blocked,
        "attacks_that_pass_per_day": attacks_missed,
        "legitimate_requests_blocked_per_day": legitimate_blocked,
        "collateral_damage_ratio": round(
            legitimate_blocked / max(attacks_blocked, 1), 2
        ),
    }

# Example: 10,000 requests/day, 0.5% are attacks
# Classifier: 95% detection, 2% false positives
result = calculate_classifier_impact(10000, 0.005, 0.95, 0.02)
# attacks_that_pass_per_day: 2-3
# legitimate_requests_blocked_per_day: ~199
# For each attack blocked, ~4 legitimate requests blocked
