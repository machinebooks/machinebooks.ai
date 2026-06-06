# Extracted from: LibroAIGateway/cap-03-pipeline-stages.md
# auth: device_id resolution order
# 1. request.state.device_id_override  (middleware upstream_context)
# 2. Header X-Device-ID               (standard official client)
# 3. Service JWT                      (service tokens of type "service")
def _resolve_device_id(request) -> str:
    override = getattr(request.state, "device_id_override", None)
    if override:
        return override
    device_id = request.headers.get("X-Device-ID", "")
    if device_id:
        return device_id
    # ... service JWT fallback ...
    raise HTTPException(400, detail="Header X-Device-ID or service token required")
