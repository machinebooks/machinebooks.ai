# Source: The FinOps Engineer and the Machine -- Chapter 22
# Pattern: Provider health monitoring

# services/provider_health.py
import time
from datetime import datetime
import anthropic
from sqlalchemy.orm import Session
from models.llm_pricing import LLMModelPricing
import logging

logger = logging.getLogger(__name__)

HEALTH_CHECK_PROMPT = "Reply 'OK' in a single word."


async def check_provider(model: LLMModelPricing) -> dict:
    """Performs a minimal test call to the provider."""
    start = time.time()
    try:
        if model.provider == "anthropic":
            client = anthropic.AsyncAnthropic()
            await client.messages.create(
                model=model.model_id,
                max_tokens=10,
                messages=[{"role": "user", "content": HEALTH_CHECK_PROMPT}],
            )
            latency_ms = (time.time() - start) * 1000
            return {"status": "healthy", "latency_ms": round(latency_ms, 1)}

        # Adapters for other providers (Azure OpenAI, etc.)
        return {"status": "unknown", "error": "Provider check not implemented"}

    except Exception as e:
        logger.warning(f"Health check failed for {model.model_id}: {e}")
        return {"status": "down", "error": str(e)}
