# Extraído de: LibroAIGateway/cap-28-admin-operaciones-ia.md
# gateway/app/api/v1/admin/debug.py (sintético: vista de diagnóstico)
@router.get("/requests/{request_id}")
async def get_request_debug(
    request_id: int,
    current_user=Depends(require_viewer),
):
    """Devuelve trace completo de una request sin exponer prompts."""
    audit = await db.get(AuditLog, request_id)
    if audit is None:
        raise HTTPException(404, "Request no encontrada")

    # IMPORTANTE: nunca exponer prompt completo, solo hash
    return {
        "id": audit.id,
        "prompt_hash": audit.prompt_sha256,  # no el prompt en texto
        "model": audit.model,
        "provider": audit.provider,
        "latency_ms": audit.latency_ms,
        "prompt_tokens": audit.prompt_tokens,
        "completion_tokens": audit.completion_tokens,
        "cost_usd": audit.cost_usd,
        "status": audit.status,
        "route_chain": audit.route_chain,  # secuencia de enrutamiento
        "error_message": audit.error_message,
    }
