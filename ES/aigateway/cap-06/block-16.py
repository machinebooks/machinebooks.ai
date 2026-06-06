# Extraído de: LibroAIGateway/cap-06-deployment-fallback.md
def record_failure_in_memory(llm_config_id: int) -> int:
    """Suma un fallo en la ventana sliding. Devuelve el count actual."""
    now = time.monotonic()
    bucket = _failure_buckets.setdefault(llm_config_id, [])
    # Drop entradas viejas fuera de la ventana de 60s
    cutoff = now - _FAILURES_WINDOW_S
    while bucket and bucket[0] < cutoff:
        bucket.pop(0)
    bucket.append(now)
    return len(bucket)
