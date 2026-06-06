# Extraído de: LibroAIGateway/cap-05-router-smart-select.md
# Cooldown check — si el proveedor está saturado, saltar al fallback
if not await deployment_cooldown_service.is_cooldowned(db, cfg.id):
    return _detach(cfg, db), f"purpose:{purpose}"
