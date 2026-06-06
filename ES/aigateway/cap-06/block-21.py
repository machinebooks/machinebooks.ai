# Extraído de: LibroAIGateway/cap-06-deployment-fallback.md
async def get_fallback_chain(model_key, db) -> list[str]:
    """Devuelve todos los fallback_keys activos del model_key."""
    row = await db.execute(
        select(LlmModel).where(
            LlmModel.model_key == model_key,
            LlmModel.is_active == True,
        )
    ).scalar_one_or_none()
    if not row or not row.fallback_chain:
        return []
    # Filtrar solo candidatos activos en BD
    for candidate in row.fallback_chain:
        if await db.execute(
            select(LlmModel).where(
                LlmModel.model_key == candidate.strip(),
                LlmModel.is_active == True,
            )
        ).scalar_one_or_none():
            active.append(candidate.strip())
    return active
