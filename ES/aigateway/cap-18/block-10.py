# Extraído de: LibroAIGateway/cap-18-keys-cifrado-master.md
# Co-firma con guard de identidad (gateway/app/api/v1/admin/break_glass.py)
async def cosign(event_id: int, body: CosignRequest, user: dict):
    user_id = user["user_id"]
    if not await _verify_admin_password(db, user_id, body.admin2_password):
        raise HTTPException(403, "Password admin invalida")
    # La BD impide que admin2 = admin1 (WHERE admin1_id <> :a2)
    await db.execute(text(
        "UPDATE break_glass_events SET admin2_id=:a2, admin2_ip=:ip, "
        "  admin2_signed_at=:now, status='active' "
        "WHERE id=:id AND status='pending_cosign' AND admin1_id <> :a2"
    ), {"a2": user_id, "ip": request.client.host, "id": event_id})
