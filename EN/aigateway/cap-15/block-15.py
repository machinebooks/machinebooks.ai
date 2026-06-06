# Extracted from: LibroAIGateway/cap-15-rate-limiting.md
# Pre-call: only reads the snapshot, does not increment
async def check_session_budget(session_id: str | None) -> float:
    if not session_id:
        return 0.0
    cap = float(get_system_infra_value("max_budget_per_session_usd", 5.0) or 5.0)
    if cap <= 0:
        return 0.0  # disabled
    try:
        redis = await get_redis()
        raw = await redis.get(f"sess_budget:{session_id}")
        current = float(raw or 0)
    except Exception as exc:
        return 0.0  # fail-open
    if current >= cap:
        raise HTTPException(
            status_code=429,
            detail=f"Session budget exceeded (${current:.4f} / ${cap:.4f})."
        )
    return current
