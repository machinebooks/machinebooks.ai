# Source: The FinOps Engineer and the Machine -- Chapter 4
# Pattern: LLM pricing lookup service

# services/llm_pricing.py
from typing import TypedDict

class CostBreakdown(TypedDict):
    input: float
    output: float
    cache: float
    total: float

# Prices in USD per million tokens (update when they change)
MODEL_PRICING = {
    "claude-opus-4-6": {
        "input": 15.00,
        "output": 75.00,
        "cache_creation": 18.75,   # 125% of input price
        "cache_read": 1.50,        # 10% of input price
    },
    "claude-sonnet-4-6": {
        "input": 3.00,
        "output": 15.00,
        "cache_creation": 3.75,
        "cache_read": 0.30,
    },
    "claude-haiku-4-5": {
        "input": 0.80,
        "output": 4.00,
        "cache_creation": 1.00,
        "cache_read": 0.08,
    },
}

def calculate_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
    cache_creation_tokens: int = 0,
    cache_read_tokens: int = 0,
) -> CostBreakdown:
    """
    Calculates the USD cost of an LLM call.
    Cached tokens are charged at a reduced rate.
    cache_read tokens have the highest savings (10% of normal price).
    """
    pricing = MODEL_PRICING.get(model)
    if not pricing:
        # Unknown model: use a conservative reference price
        pricing = MODEL_PRICING["claude-sonnet-4-6"]

    M = 1_000_000  # tokens per million

    # Input tokens charged at normal price
    # are those NOT in cache or cache_creation
    billable_input = max(0, input_tokens - cache_creation_tokens - cache_read_tokens)

    input_cost = (billable_input / M) * pricing["input"]
    output_cost = (output_tokens / M) * pricing["output"]
    cache_cost = (
        (cache_creation_tokens / M) * pricing["cache_creation"]
        + (cache_read_tokens / M) * pricing["cache_read"]
    )

    total = input_cost + output_cost + cache_cost

    return CostBreakdown(
        input=round(input_cost, 8),
        output=round(output_cost, 8),
        cache=round(cache_cost, 8),
        total=round(total, 8),
    )
