# Extraído de: LibroAIGateway/cap-20-clasificacion-guardrails-firewall.md
# gateway/app/services/firewall_service.py:97-121

async def _load_policy(db: AsyncSession) -> dict:
    now = time.monotonic()
    if _policy_cache["value"] is not None and _policy_cache["expires_at"] > now:
        return _policy_cache["value"]
    raw: dict = {}
    try:
        rs = await db.execute(text(
            "SELECT config FROM orchestrator_configs "
            "WHERE orchestrator_key='firewall_policy' AND is_active=1"
        ))
        row = rs.fetchone()
        if row and row[0]:
            cfg = row[0]
            if isinstance(cfg, str):
                import json; cfg = json.loads(cfg)
            if isinstance(cfg, dict):
                raw = cfg
    except Exception:
        logger.debug("firewall:policy_load_failed", exc_info=True)
    merged = {**_DEFAULT_POLICY, **{k: v for k, v in raw.items() if v in _VALID_ACTIONS}}
    _policy_cache["value"] = merged
    _policy_cache["expires_at"] = now + _CACHE_TTL_SECONDS
    return merged
