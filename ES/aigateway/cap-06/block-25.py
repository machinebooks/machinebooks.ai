# Extraído de: LibroAIGateway/cap-06-deployment-fallback.md
# Registro de auditoría — no bloquea si falla
event = ModelEscalationEvent(
    request_id=request_id,
    from_model=from_model,
    to_model=to_model,
    trigger_reason=trigger_reason,
    error_code=type(error).__name__,
    error_message=_sanitize(str(error)),  # redacta keys
    succeeded=succeeded,
    cost_usd_after=cost_usd_after,
)
db.add(event)
