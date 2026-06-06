# Extraído de: LibroAIGateway/cap-34-celery-deployment-config.md
@celery_app.task(name="app.tasks.health_tasks.audit_chain_seal_batch", queue="default")
def audit_chain_seal_batch() -> dict:
    async def _run() -> dict:
        from app.core.database import AsyncSessionLocal
        from app.services.audit_chain_service import seal_batch, get_chain_status
        async with AsyncSessionLocal() as db:
            sealed = await seal_batch(db, limit=10000)
            await db.commit()
            status = await get_chain_status(db)
            return {"sealed": int(sealed), "pending": int(status.get("unsealed", 0))}
    try:
        return asyncio.run(_run())
    except Exception as exc:
        logger.exception("audit_chain_seal_batch:failed err=%s", exc)
        return {"error": str(exc)[:200]}
