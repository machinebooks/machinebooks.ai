# Extraído de: LibroFinOps/cap-22-multiproveedor.md
# services/provider_health.py
import time
from datetime import datetime
import anthropic
from sqlalchemy.orm import Session
from models.llm_pricing import LLMModelPricing
import logging

logger = logging.getLogger(__name__)

HEALTH_CHECK_PROMPT = "Responde 'OK' en una sola palabra."


async def check_provider(model: LLMModelPricing) -> dict:
    """Realiza una llamada de prueba mínima al proveedor."""
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

        # Adapters para otros proveedores (Azure OpenAI, etc.)
        return {"status": "unknown", "error": "Provider check not implemented"}

    except Exception as e:
        logger.warning(f"Health check falló para {model.model_id}: {e}")
        return {"status": "down", "error": str(e)}
