# Source: The FinOps Engineer and the Machine -- Chapter 9
# Pattern: LLMUsageLog extension with cache fields

# models/llm_usage_log.py (extension from Chapter 4)
from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean

class LLMUsageLog(Base):
    """Extended log with prompt caching and batch fields."""
    __tablename__ = "llm_usage_log"

    id                     = Column(Integer, primary_key=True)
    service_name           = Column(String(100))
    model                  = Column(String(100))
    input_tokens           = Column(Integer)
    output_tokens          = Column(Integer)
    # Caching fields (0 if caching was not used)
    cache_read_tokens      = Column(Integer, default=0)
    cache_creation_tokens  = Column(Integer, default=0)
    # Actual cost (with cache and/or batch discounts)
    cost_usd               = Column(Float)
    # Hypothetical cost without any optimization (for calculating cumulative savings)
    cost_without_cache_usd = Column(Float, nullable=True)
    created_at             = Column(DateTime)
    user_id                = Column(String(100), nullable=True)
    is_batch               = Column(Boolean, default=False)


def calculate_cost_with_cache(
    model: str,
    input_tokens: int,
    output_tokens: int,
    cache_read_tokens: int = 0,
    cache_creation_tokens: int = 0,
    is_batch: bool = False,
) -> tuple[float, float]:
    """
    Calculates the actual cost applying cache and batch discounts.
    Returns (actual_cost, cost_without_optimizations).
    """
    PRICES = {
        "claude-sonnet-4-6": {
            "input": 3.00, "output": 15.00,
            "cache_write": 3.75, "cache_read": 0.30,
        },
        "claude-haiku-4-5": {
            "input": 0.80, "output": 4.00,
            "cache_write": 1.00, "cache_read": 0.08,
        },
        "claude-opus-4-6": {
            "input": 15.00, "output": 75.00,
            "cache_write": 18.75, "cache_read": 1.50,
        },
    }

    p = PRICES.get(model, PRICES["claude-sonnet-4-6"])
    M = 1_000_000

    # Normal input tokens (neither cached reads nor cache writes)
    normal_input = input_tokens - cache_read_tokens - cache_creation_tokens
    batch_factor = 0.50 if is_batch else 1.00

    cost_actual = batch_factor * (
        normal_input            / M * p["input"]
        + cache_creation_tokens / M * p["cache_write"]
        + cache_read_tokens     / M * p["cache_read"]
        + output_tokens         / M * p["output"]
    )

    # Base cost without any optimization (for comparison only)
    cost_without = (
        input_tokens  / M * p["input"]
        + output_tokens / M * p["output"]
    )

    return cost_actual, cost_without
