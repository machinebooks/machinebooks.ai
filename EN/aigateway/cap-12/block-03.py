# Extracted from: LibroAIGateway/cap-12-queue-rag.md
# gateway/app/api/v1/llm_queued.py:118-149 (synthesized)
async def _verify_task_ownership(db, task_id, jwt_payload):
    is_super = bool(jwt_payload.get("super"))
    role = jwt_payload.get("role") or "viewer"
    user_id = int(jwt_payload.get("sub") or 0)
    org_id = int(jwt_payload.get("org_id") or 0)

    log = await db.get(CeleryTaskLog, task_id=task_id)
    if log is None:
        raise HTTPException(404, "task not found")  # no 403

    if is_super:
        return True
    if role == "admin" and log.organization_id == org_id:
        return True
    if log.user_id == user_id:
        return True
    raise HTTPException(404, "task not found")  # no 403
