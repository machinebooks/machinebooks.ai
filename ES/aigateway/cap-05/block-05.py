# Extraído de: LibroAIGateway/cap-05-router-smart-select.md
# 2. Routing rules (legacy admin rules con condiciones role/team/etc.)
rules = result.scalars().all()
for rule in rules:
    if cls._matches_condition(rule.condition, context or {}):
        cfg = ... # resolver target_config_id
        if cfg and not await cooldown(db, cfg.id):
            return _detach(cfg, db), f"rule:{rule.name}"
