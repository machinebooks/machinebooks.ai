# Extracted from: LibroAIGateway/cap-28-admin-operations-ai.md
# gateway/app/api/v1/admin/debug.py (synthetic: diagnostic view)
@router.get("/requests/{request_id}")
async def get_request_debug(
    request_id: int,
    current_user=Depends(require_viewer),
):
    """Returns complete trace of a request without exposing prompts."""
    audit = await db.get(AuditLog, request_id)
    if audit is None:
        raise HTTPException(404, "Request no encontrada")

    # IMPORTANT: never expose full prompt, only hash
    return {
        "id": audit.id,
        "prompt_hash": audit.prompt_sha256,  # not the prompt in text
        "model": audit.model,
        "provider": audit.provider,
        "latency_ms": audit.latency_ms,
        "prompt_tokens": audit.prompt_tokens,
        "completion_tokens": audit.completion_tokens,
        "cost_usd": audit.cost_usd,
        "status": audit.status,
        "route_chain": audit.route_chain,  # routing sequence
        "error_message": audit.error_message,
    }
