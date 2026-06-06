# Extracted from: LibroAIGateway/cap-24-telemetry-realtime-webhooks.md
# metrics_service.py (synthetic)
def record_request(ctx: PipelineContext, duration: float, status_code: int):
    # IMPORTANT: org_id is NOT a label — it is omitted for cardinality.
    model = ctx.model_key or "unknown"
    bucket = f"{status_code // 100}xx"   # 2xx / 4xx / 5xx, low-cardinality

    n7x_request_duration_seconds.labels(endpoint=ctx.endpoint, model=model).observe(duration)
    n7x_requests_total.labels(
        endpoint=ctx.endpoint, model=model, status_bucket=bucket
    ).inc()
