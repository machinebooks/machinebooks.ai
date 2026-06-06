# Extracted from: LibroAIGateway/cap-05-router-smart-select.md
# Cooldown check — if the provider is saturated, fall through to the fallback
if not await deployment_cooldown_service.is_cooldowned(db, cfg.id):
    return _detach(cfg, db), f"purpose:{purpose}"
