# Source: The FinOps Engineer and the Machine -- Chapter 2
# Pattern: Seed data for LLM pricing table

# migrations/seed_llm_pricing.py
# Reference pricing data for configured providers.
# IMPORTANT: verify and update against the provider's official documentation
# before using in production. Prices change.

from datetime import datetime

PRICING_SEED_DATA = [
    # --- Anthropic --------------------------------------------------------
    {
        "provider": "anthropic",
        "model_id": "claude-opus-4-6",
        "model_display_name": "Claude Opus 4.6",
        "model_type": "chat",
        "input_price_per_1m": 15.00,    # USD/1M input tokens
        "output_price_per_1m": 75.00,   # USD/1M output tokens
        "cached_input_price_per_1m": 1.50,   # 90% discount on input
        "cache_write_price_per_1m": 18.75,   # Cost of writing to cache
        "effective_date": datetime(2025, 1, 1),
        "is_active": True,
        "change_reason": "Initial prices in master table",
    },
    {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-6",
        "model_display_name": "Claude Sonnet 4.6",
        "model_type": "chat",
        "input_price_per_1m": 3.00,
        "output_price_per_1m": 15.00,
        "cached_input_price_per_1m": 0.30,
        "cache_write_price_per_1m": 3.75,
        "effective_date": datetime(2025, 1, 1),
        "is_active": True,
        "change_reason": "Initial prices in master table",
    },
    {
        "provider": "anthropic",
        "model_id": "claude-haiku-4-5",
        "model_display_name": "Claude Haiku 4.5",
        "model_type": "chat",
        "input_price_per_1m": 0.80,
        "output_price_per_1m": 4.00,
        "cached_input_price_per_1m": 0.08,
        "cache_write_price_per_1m": 1.00,
        "effective_date": datetime(2025, 1, 1),
        "is_active": True,
        "change_reason": "Initial prices in master table",
    },
    # --- OpenAI -----------------------------------------------------------
    {
        "provider": "openai",
        "model_id": "gpt-4o",
        "model_display_name": "GPT-4o",
        "model_type": "chat",
        "input_price_per_1m": 2.50,
        "output_price_per_1m": 10.00,
        "cached_input_price_per_1m": 1.25,
        "cache_write_price_per_1m": None,  # OpenAI does not charge for cache writes
        "effective_date": datetime(2025, 1, 1),
        "is_active": True,
        "change_reason": "Initial prices in master table",
    },
    {
        "provider": "openai",
        "model_id": "text-embedding-3-small",
        "model_display_name": "Text Embedding 3 Small",
        "model_type": "embedding",
        "input_price_per_1m": 0.02,
        "output_price_per_1m": 0.0,  # Embeddings do not generate output tokens
        "cached_input_price_per_1m": None,
        "cache_write_price_per_1m": None,
        "effective_date": datetime(2025, 1, 1),
        "is_active": True,
        "change_reason": "Initial prices in master table",
    },
    # --- Azure OpenAI -----------------------------------------------------
    {
        "provider": "azure_openai",
        "model_id": "gpt-4o",
        "model_display_name": "GPT-4o (Azure)",
        "model_type": "chat",
        "input_price_per_1m": 2.50,
        "output_price_per_1m": 10.00,
        "cached_input_price_per_1m": None,  # Cache price varies by Azure region
        "cache_write_price_per_1m": None,
        "effective_date": datetime(2025, 1, 1),
        "is_active": True,
        "change_reason": "Initial prices; verify by region",
    },
]
