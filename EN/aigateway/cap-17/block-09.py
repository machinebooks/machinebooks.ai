# Extracted from: LibroAIGateway/cap-17-sso-scim-mfa.md
# gateway/app/api/v1/scim.py — PATCH Groups for add/remove members
@router.patch("/Groups/{group_id}")
async def patch_group(group_id, payload, db, authorization):
    ops = payload.get("Operations") or []
    for op in ops:
        if (op.get("path") or "").lower() != "members":
            continue
        for v in op.get("value") or []:
            member_id = int(v.get("value"))
            if op.get("op") in {"add", "replace"}:
                await db.execute(sa_text(
                    "UPDATE users SET team_id = :tid WHERE id = :id"
                ), {"tid": group_id, "id": member_id})
            elif op.get("op") == "remove":
                await db.execute(sa_text(
                    "UPDATE users SET team_id = NULL WHERE id = :id AND team_id = :tid"
                ), {"tid": group_id, "id": member_id})
    await db.commit()
