# Extracted from: LibroAIGateway/cap-09-compression-tokens.md
# gateway/app/services/semantic_dedup_service.py:65-94 (synthesized)
async def _load_whitelist(db) -> frozenset[str]:
    """Reads enabled_purposes from orchestrator_configs.semantic_cache."""
    # Query: SELECT config FROM orchestrator_configs
    # WHERE orchestrator_key = 'semantic_cache' AND is_active = 1
    purposes = frozenset(cfg.get("enabled_purposes") or [])
    _WHITELIST_CACHE["purposes"] = purposes
    return purposes
