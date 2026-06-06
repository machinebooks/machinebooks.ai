# Extracted from: LibroAIGateway/cap-06-deployment-fallback.md
# Audit logging — does not block if it fails
event = ModelEscalationEvent(
    request_id=request_id,
    from_model=from_model,
    to_model=to_model,
    trigger_reason=trigger_reason,
    error_code=type(error).__name__,
    error_message=_sanitize(str(error)),  # redacts keys
    succeeded=succeeded,
    cost_usd_after=cost_usd_after,
)
db.add(event)
