# Extraído de: LibroAIGateway/cap-05-router-smart-select.md
# 1. Match por purpose. UNIQUE en la columna, así que solo hay una.
result = await db.execute(
    select(LLMConfig).where(
        LLMConfig.purpose == purpose,
        LLMConfig.is_active,
    )
)
cfg = result.scalar_one_or_none()
