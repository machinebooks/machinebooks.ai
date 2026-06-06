# Extraído de: LibroAIGateway/cap-13-tenants-cuotas.md
# IMPORTANTE: fail-closed — si el commit falla, DENEGAR.
# Permitir aquí abriría un bypass de quota: 100 requests paralelos
# durante latencia de BD consumirían presupuesto ilimitado.
try:
    await db.commit()
except Exception as exc:
    logger.exception("llm_quota:commit_failed device=%s err=%s", device_id, exc)
    await db.rollback()
    return {"allowed": False, "bucket_hit": "db_error", ...}
