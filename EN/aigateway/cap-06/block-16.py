# Extracted from: LibroAIGateway/cap-06-deployment-fallback.md
def record_failure_in_memory(llm_config_id: int) -> int:
    """Adds a failure to the sliding window. Returns the current count."""
    now = time.monotonic()
    bucket = _failure_buckets.setdefault(llm_config_id, [])
    # Drop old entries outside the 60s window
    cutoff = now - _FAILURES_WINDOW_S
    while bucket and bucket[0] < cutoff:
        bucket.pop(0)
    bucket.append(now)
    return len(bucket)
