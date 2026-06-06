# Extraído de: LibroAIGateway/cap-24-telemetria-realtime-webhooks.md
# metrics_service.py (sintético)
def record_request(ctx: PipelineContext, duration: float, status_code: int):
    # IMPORTANTE: org_id NO entra como label — se omite por cardinalidad.
    model = ctx.model_key or "unknown"
    bucket = f"{status_code // 100}xx"   # 2xx / 4xx / 5xx, baja cardinalidad

    n7x_request_duration_seconds.labels(endpoint=ctx.endpoint, model=model).observe(duration)
    n7x_requests_total.labels(
        endpoint=ctx.endpoint, model=model, status_bucket=bucket
    ).inc()
