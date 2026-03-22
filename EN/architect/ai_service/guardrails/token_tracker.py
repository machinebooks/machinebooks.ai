"""
Chapter 11: Token tracking and cost management.

Three-level cost tracking:
  1. LLMUsageLog — per-call (tokens, cost, latency)
  2. LLMModelPricing — editable prices with cache
  3. BudgetConfig — monthly/daily/per-user limits with actions: alert -> throttle -> block

ROI calculation with human baseline:
  HumanBaselineConfig defines human time per task:
    - Document analysis: 8 hours
    - Proposal generation: 40 hours
    - CV analysis: 45 minutes
  TaskCompletionLog calculates time_saved_minutes and money_saved_eur.
"""

import time
from dataclasses import dataclass
from typing import Optional, Dict


# =============================================================================
# Budget enforcement (Chapter 11)
# =============================================================================

@dataclass
class BudgetConfig:
    """
    Budget limits with graduated enforcement actions.

    When spending hits a threshold:
      alert    (80%) — notify admin, continue operating
      throttle (90%) — reduce to essential services only
      block    (100%) — reject non-critical AI requests
    """
    provider: str
    monthly_limit_eur: float
    daily_limit_eur: float = 0.0         # 0 = no daily limit
    per_user_limit_eur: float = 0.0      # 0 = no per-user limit
    alert_threshold: float = 0.80        # 80% -> alert
    throttle_threshold: float = 0.90     # 90% -> throttle
    block_threshold: float = 1.00        # 100% -> block


class BudgetService:
    """
    Enforce spending limits before every LLM call.

    Chapter 11: The LLM Factory calls check_or_raise() before building
    any client. This ensures budget limits are respected even if a new
    service is added that bypasses the normal flow.
    """

    def __init__(self, redis_client, config: Optional[Dict[str, BudgetConfig]] = None):
        self.redis = redis_client
        self.configs = config or {}

    def check_or_raise(
        self, user_id: Optional[int], service_type: str
    ) -> str:
        """
        Check budget and return the enforcement action.

        Returns: 'allow', 'alert', 'throttle'
        Raises: BudgetExceededError if blocked.
        """
        # In production: sum today's spending from Redis counter
        # daily_key = f"budget:daily:{datetime.now().strftime('%Y-%m-%d')}"
        # daily_spent = float(self.redis.get(daily_key) or 0)
        #
        # config = self.configs.get("anthropic", BudgetConfig("anthropic", 1000))
        # ratio = daily_spent / config.daily_limit_eur if config.daily_limit_eur else 0
        #
        # if ratio >= config.block_threshold:
        #     raise BudgetExceededError(f"Daily budget exceeded: {daily_spent:.2f} EUR")
        # elif ratio >= config.throttle_threshold:
        #     return "throttle"
        # elif ratio >= config.alert_threshold:
        #     return "alert"

        return "allow"

    def record_cost(self, provider: str, cost_eur: float) -> None:
        """
        Increment the spending counter after a successful LLM call.
        Uses Redis INCRBYFLOAT for atomic updates across workers.
        """
        # daily_key = f"budget:daily:{datetime.now().strftime('%Y-%m-%d')}"
        # self.redis.incrbyfloat(daily_key, cost_eur)
        # self.redis.expire(daily_key, 86400 * 2)  # Auto-cleanup after 2 days
        pass


# =============================================================================
# ROI calculation with human baseline (Chapter 11)
# =============================================================================

# Human time per task (calibrated with real project data)
HUMAN_BASELINES = {
    "document_analysis":      {"hours": 8.0,  "cost_eur_per_hour": 85.0},
    "proposal_generation":    {"hours": 40.0, "cost_eur_per_hour": 95.0},
    "cv_analysis":            {"hours": 0.75, "cost_eur_per_hour": 75.0},
    "opportunity_scoring":    {"hours": 2.0,  "cost_eur_per_hour": 85.0},
    "executive_summary":      {"hours": 4.0,  "cost_eur_per_hour": 95.0},
}


@dataclass
class ROIResult:
    """ROI calculation for a completed AI task."""
    task_type: str
    ai_time_seconds: float
    ai_cost_eur: float
    human_time_hours: float
    human_cost_eur: float
    time_saved_minutes: float
    money_saved_eur: float
    roi_multiplier: float


def calculate_roi(
    task_type: str,
    ai_time_seconds: float,
    ai_cost_eur: float,
) -> Optional[ROIResult]:
    """
    Calculate ROI comparing AI execution vs human baseline.

    Chapter 11: The Platform tracks ROI per task to answer the
    executive question "Is the AI investment paying off?" with
    actual data instead of estimates.

    Example: Proposal generation
      Human: 40 hours * 95 EUR/h = 3,800 EUR
      AI: 102 seconds * ~0.45 EUR = 0.45 EUR
      ROI: 8,444x (time), 3,799.55 EUR saved per proposal
    """
    baseline = HUMAN_BASELINES.get(task_type)
    if not baseline:
        return None

    human_time_hours = baseline["hours"]
    human_cost = human_time_hours * baseline["cost_eur_per_hour"]
    ai_time_hours = ai_time_seconds / 3600

    time_saved_minutes = (human_time_hours - ai_time_hours) * 60
    money_saved = human_cost - ai_cost_eur
    roi_multiplier = human_cost / max(ai_cost_eur, 0.01)

    return ROIResult(
        task_type=task_type,
        ai_time_seconds=ai_time_seconds,
        ai_cost_eur=ai_cost_eur,
        human_time_hours=human_time_hours,
        human_cost_eur=human_cost,
        time_saved_minutes=time_saved_minutes,
        money_saved_eur=money_saved,
        roi_multiplier=roi_multiplier,
    )


# =============================================================================
# Pricing cache (Chapter 11)
# =============================================================================

# Default pricing (EUR per 1K tokens) — updated from Admin panel
DEFAULT_PRICING = {
    ("anthropic", "claude-opus-4-6"):   {"input": 0.015, "output": 0.075},
    ("anthropic", "claude-sonnet-4-6"): {"input": 0.003, "output": 0.015},
    ("anthropic", "claude-haiku-4-5"):  {"input": 0.0008, "output": 0.004},
    ("openai", "gpt-4o"):              {"input": 0.005, "output": 0.015},
}


def estimate_cost(
    provider: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> float:
    """
    Estimate cost in EUR using cached pricing.

    In production, prices are loaded from LLMModelPricing table
    with effective_from dates for price history.
    """
    pricing = DEFAULT_PRICING.get((provider, model))
    if not pricing:
        return 0.0

    cost = (
        input_tokens / 1000 * pricing["input"]
        + output_tokens / 1000 * pricing["output"]
    )
    return round(cost, 6)


class BudgetExceededError(Exception):
    pass
