# Extracted from: LibroAIGateway/cap-24-telemetry-realtime-webhooks.md
# gateway/app/middleware/json_logging.py (synthetic)
@middleware
async def json_logging_middleware(request: Request, call_next):
    start = time.monotonic()
    request_id = generate_request_id()
    request.headers["X-N7x-Request-Id"] = request_id

    response = await call_next(request)
    duration = time.monotonic() - start

    # 1. Build the log without PII
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "duration_ms": round(duration * 1000, 1),
        "org_id": getattr(request.state, "org_id", None),
        "model_key": getattr(request.state, "model_key", None),
        "user_agent": _sanitize_user_agent(request.headers.get("user-agent", "")),
    }
    # 2. Never include prompts, responses, or auth headers
    logger.info(json.dumps(log_entry, default=str))
    return response
