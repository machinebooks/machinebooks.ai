# Extracted from: LibroAIGateway/cap-05-router-smart-select.md
if not default_config:
    any_result = await db.execute(
        select(LLMConfig).where(LLMConfig.is_active)
    )
    # filter_cooldowned returns IDs on cooldown
    for c in candidates:
        if c.id not in cooldowned:
            default_config = c
            break
