# Extraído de: LibroAIGateway/cap-10-embeddings-imagenes-audio.md
# gateway/app/api/v1/images.py:100-139 (sintetizado)
async def _resolve_image_config(db, model_row):
    # 1. upstream_config_id explícito del modelo
    if model_row.upstream_config_id:
        config = await db.get(LLMConfig, model_row.upstream_config_id)
        if config: return config
    # 2. por purpose
    for purpose in ("image_generation", "images_generation", "image"):
        config = await db.query(LLMConfig).where(purpose==purpose).first()
        if config: return config
    # 3. default Azure
    return await db.query(LLMConfig).where(is_default==True).first()
