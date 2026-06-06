# Extraído de: LibroAIGateway/cap-06-deployment-fallback.md
async def purge_expired(db: AsyncSession) -> int:
    res = await db.execute(
        delete(LlmDeploymentCooldown).where(
            LlmDeploymentCooldown.until_ts <= datetime.utcnow(),
        )
    )
    await db.commit()
    return res.rowcount or 0
