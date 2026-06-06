# Extracted from: LibroAIGateway/cap-05-router-smart-select.md
default_result = await db.execute(
    select(LLMConfig).where(LLMConfig.is_default, LLMConfig.is_active)
)
default_config = default_result.scalar_one_or_none()
