# Extracted from: LibroAIGateway/cap-06-deployment-fallback.md
async def pick(cls, db, redis, *, model_key, strategy="weighted",
               required_tags=None, prompt_cache_key=None,
               estimated_tokens=0) -> Optional[LLMModelDeployment]:
    """Returns a deployment from the model_key pool or None."""
    # Initial pool: active and with status='up'
    rows = (await db.execute(
        select(LLMModelDeployment).where(
            LLMModelDeployment.model_key == model_key,
            LLMModelDeployment.is_active.is_(True),
            LLMModelDeployment.status == "up",
        )
    )).scalars().all()
    if not rows:
        return None
