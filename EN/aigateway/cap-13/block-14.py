# Extracted from: LibroAIGateway/cap-13-tenants-quotas.md
# IMPORTANT: fail-closed — if commit fails, DENY.
# Allowing here would open a quota bypass: 100 parallel requests
# during DB latency would consume unlimited budget.
try:
    await db.commit()
except Exception as exc:
    logger.exception("llm_quota:commit_failed device=%s err=%s", device_id, exc)
    await db.rollback()
    return {"allowed": False, "bucket_hit": "db_error", ...}
