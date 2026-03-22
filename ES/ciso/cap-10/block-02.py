# Extraído de: LibroCISO/cap-10-arquitectura-llm.md
from celery import shared_task
from datetime import datetime
import time
import logging

from app.extensions import db
from app.models.ai import AIProvider, ProviderType
logger = logging.getLogger(__name__)

# Prompt mínimo para verificar que el proveedor responde
HEALTH_CHECK_PROMPT = "Responde solo con la palabra OK."


@shared_task(name="ai.health_check_providers", queue="maintenance")
def health_check_all_providers():
    """
    Verifica la disponibilidad y latencia de todos los proveedores activos.
    Se ejecuta cada 5 minutos vía Celery Beat.
    """
    providers = db.session.query(AIProvider).filter(
        AIProvider.is_active == True
    ).all()

    results = []
    for provider in providers:
        try:
            start = time.time()
            _ping_provider(provider)
            latency_ms = int((time.time() - start) * 1000)

            provider.last_health_check = datetime.now(timezone.utc)()
            provider.last_latency_ms = latency_ms
            results.append({
                "provider": provider.name,
                "status": "healthy",
                "latency_ms": latency_ms
            })
            logger.info(f"Health check OK: {provider.name} ({latency_ms}ms)")

        except Exception as e:
            provider.last_health_check = datetime.now(timezone.utc)()
            provider.last_latency_ms = -1  # -1 indica fallo
            results.append({
                "provider": provider.name,
                "status": "unhealthy",
                "error": str(e)
            })
            logger.warning(f"Health check FAIL: {provider.name}: {e}")

    db.session.commit()
    return results


def _ping_provider(provider: AIProvider):
    """Envía un prompt mínimo para verificar respuesta."""
    import anthropic
    import openai

    api_key = LLMFactory._get_api_key(provider.api_key_ref) if provider.api_key_ref else None

    if provider.provider_type == ProviderType.ANTHROPIC:
        client = anthropic.Anthropic(api_key=api_key)
        # Usamos el modelo más barato disponible para el health check
        client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=10,
            messages=[{"role": "user", "content": HEALTH_CHECK_PROMPT}]
        )
    else:
        # Todos los demás usan API compatible OpenAI
        base_url = provider.api_base_url
        client = openai.OpenAI(
            api_key=api_key or "local",
            base_url=base_url
        )
        models = provider.available_models or []
        model_name = models[0]["name"] if models else "default"
        client.chat.completions.create(
            model=model_name,
            max_tokens=10,
            messages=[{"role": "user", "content": HEALTH_CHECK_PROMPT}]
        )
