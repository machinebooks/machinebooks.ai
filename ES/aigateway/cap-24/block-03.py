# Extraído de: LibroAIGateway/cap-24-telemetria-realtime-webhooks.md
# metrics_service.py (sintético, dentro del adapter callback)
def record_usage(model: str, provider: str, prompt_tokens: int,
                 completion_tokens: int, cached_tokens: int, cache_kind: str):
    n7x_tokens_total.labels(direction="input", model=model).inc(prompt_tokens)
    n7x_tokens_total.labels(direction="output", model=model).inc(completion_tokens)
    if cached_tokens > 0:
        n7x_llm_cached_tokens_total.labels(
            provider=provider, model=model, kind=cache_kind
        ).inc(cached_tokens)
