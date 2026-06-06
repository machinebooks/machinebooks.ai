# Extraído de: LibroAIGateway/cap-09-compresion-tokens.md
# gateway/app/services/semantic_dedup_service.py:65-94 (sintetizado)
async def _load_whitelist(db) -> frozenset[str]:
    """Lee enabled_purposes desde orchestrator_configs.semantic_cache."""
    # Consulta: SELECT config FROM orchestrator_configs
    # WHERE orchestrator_key = 'semantic_cache' AND is_active = 1
    purposes = frozenset(cfg.get("enabled_purposes") or [])
    _WHITELIST_CACHE["purposes"] = purposes
    return purposes
