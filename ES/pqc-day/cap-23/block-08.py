# Extraído de: LibroPQC/cap-23-observabilidad.md
import time
import hashlib
from models.ai_admin import AIUsageLog


def call_llm_with_tracking(provider, service, user_id,
                           messages, client_id=None):
    """Ejecuta una llamada al LLM y registra métricas.
    Patrón: medir antes y después, registrar siempre
    (tanto éxito como error)."""
    start_time = time.time()
    prompt_text = messages[-1]['content'] if messages else ''
    request_hash = hashlib.sha256(
        prompt_text.encode('utf-8')
    ).hexdigest()

    try:
        # Llamada al modelo (Claude API como ejemplo)
        response = anthropic_client.messages.create(
            model=service.model,
            max_tokens=service.max_tokens,
            temperature=service.temperature,
            messages=messages
        )

        latency_ms = int((time.time() - start_time) * 1000)

        # Registrar uso exitoso
        usage_log = AIUsageLog(
            service_id=service.id,
            provider_id=provider.id,
            user_id=user_id,
            model=service.model,
            operation=service.slug,
            tokens_in=response.usage.input_tokens,
            tokens_out=response.usage.output_tokens,
            tokens_total=(
                response.usage.input_tokens
                + response.usage.output_tokens
            ),
            cost_usd=calculate_cost(
                provider, response.usage
            ),
            latency_ms=latency_ms,
            status='success',
            request_hash=request_hash,
            client_id=client_id
        )
        db.session.add(usage_log)

        # Actualizar métricas agregadas del proveedor
        provider.total_tokens_used += usage_log.tokens_total
        provider.total_cost_usd += usage_log.cost_usd
        db.session.commit()

        return response

    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        status = 'timeout' if 'timeout' in str(e).lower() \
                 else 'error'

        # Registrar el fallo (igual de importante)
        usage_log = AIUsageLog(
            service_id=service.id,
            provider_id=provider.id,
            user_id=user_id,
            model=service.model,
            operation=service.slug,
            tokens_in=0, tokens_out=0, tokens_total=0,
            cost_usd=0.0,
            latency_ms=latency_ms,
            status=status,
            error_message=str(e)[:500],
            request_hash=request_hash,
            client_id=client_id
        )
        db.session.add(usage_log)
        db.session.commit()
        raise
