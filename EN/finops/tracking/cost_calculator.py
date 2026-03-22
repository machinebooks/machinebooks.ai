# Source: The FinOps Engineer and the Machine -- Chapter 2
# Pattern: Cost calculator with prompt caching support

# services/cost_calculator.py
# Calculates the USD cost of an LLM call with full support
# for asymmetric prompt caching (input price != cache price != output price).

from dataclasses import dataclass
from typing import Optional
from decimal import Decimal, ROUND_HALF_UP


@dataclass
class CallCostBreakdown:
    """Complete cost breakdown of a call, in USD."""
    input_tokens: int
    output_tokens: int
    cached_input_tokens: int       # Tokens served from cache (reduced price)
    cache_write_tokens: int        # Tokens written to cache (some providers charge)

    input_cost_usd: float          # Cost of non-cached input tokens
    output_cost_usd: float         # Cost of output tokens
    cached_input_cost_usd: float   # Cost of input tokens from cache
    cache_write_cost_usd: float    # Cost of cache writing

    total_cost_usd: float          # Sum of all components
    total_cost_eur: float          # Total in EUR (with daily exchange rate)

    model_id: str
    provider: str
    cache_savings_usd: float       # How much was saved by using cache vs. standard price


def calculate_call_cost(
    pricing: LLMModelPricing,
    input_tokens: int,
    output_tokens: int,
    cached_input_tokens: int = 0,
    cache_write_tokens: int = 0,
    eur_exchange_rate: float = 0.92  # USD -> EUR; update periodically
) -> CallCostBreakdown:
    """
    Calculates the complete cost of an LLM call with breakdown by token type.

    Input tokens are divided into:
    - input_tokens: processed at standard price (input_price_per_1m)
    - cached_input_tokens: served from cache (cached_input_price_per_1m)
    - cache_write_tokens: written to cache (cache_write_price_per_1m)

    The Anthropic API returns these three counters in usage.
    """
    MILLION = 1_000_000

    # Standard input tokens (those NOT from cache)
    standard_input_tokens = input_tokens - cached_input_tokens - cache_write_tokens
    standard_input_tokens = max(0, standard_input_tokens)

    # Calculation per component
    input_cost = (standard_input_tokens / MILLION) * pricing.input_price_per_1m
    output_cost = (output_tokens / MILLION) * pricing.output_price_per_1m

    cached_price = pricing.cached_input_price_per_1m or pricing.input_price_per_1m
    cached_cost = (cached_input_tokens / MILLION) * cached_price

    write_price = pricing.cache_write_price_per_1m or 0.0
    write_cost = (cache_write_tokens / MILLION) * write_price

    total_usd = input_cost + output_cost + cached_cost + write_cost
    total_eur = total_usd * eur_exchange_rate

    # Cache savings: difference between standard price and cached price
    cache_savings = (cached_input_tokens / MILLION) * (
        pricing.input_price_per_1m - cached_price
    )

    return CallCostBreakdown(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cached_input_tokens=cached_input_tokens,
        cache_write_tokens=cache_write_tokens,
        input_cost_usd=round(input_cost, 8),
        output_cost_usd=round(output_cost, 8),
        cached_input_cost_usd=round(cached_cost, 8),
        cache_write_cost_usd=round(write_cost, 8),
        total_cost_usd=round(total_usd, 8),
        total_cost_eur=round(total_eur, 8),
        model_id=pricing.model_id,
        provider=pricing.provider,
        cache_savings_usd=round(cache_savings, 8),
    )
