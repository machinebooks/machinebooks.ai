# Extracted from: LibroAIGateway/cap-05-router-smart-select.md
# 1. Match by purpose. UNIQUE on the column, so there is only one.
result = await db.execute(
    select(LLMConfig).where(
        LLMConfig.purpose == purpose,
        LLMConfig.is_active,
    )
)
cfg = result.scalar_one_or_none()
