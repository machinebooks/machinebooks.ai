# Source: The FinOps Engineer and the Machine -- Chapter 22
# Pattern: Committed use discount optimizer

# services/committed_use_optimizer.py
import statistics


class CommittedUseOptimizer:
    """
    Calculates the optimal committed use level
    based on consumption history.
    """

    def optimize(
        self,
        historical_monthly_usd: list,   # consumption for the last N months
        commitment_horizon_months: int = 1,
        risk_tolerance: float = 0.10,
    ) -> dict:
        if not historical_monthly_usd or len(historical_monthly_usd) < 3:
            return {"recommendation": "insufficient_data", "committed_usd": 0}

        mean = statistics.mean(historical_monthly_usd)
        std = statistics.stdev(historical_monthly_usd)
        cv = std / mean if mean > 0 else 999

        sorted_consumption = sorted(historical_monthly_usd)
        p10 = sorted_consumption[max(0, int(len(sorted_consumption) * 0.10))]
        p60 = sorted_consumption[int(len(sorted_consumption) * 0.60)]

        return {
            "historical_mean_usd": round(mean, 2),
            "historical_cv": round(cv, 3),
            "conservative_committed_usd": round(p10, 2),  # minimum risk
            "aggressive_committed_usd": round(p60, 2),     # higher savings
            "rationale": (
                "High variance: conservative recommendation."
                if cv > 0.20 else
                "Low variance: aggressive level can be considered."
            ),
        }
