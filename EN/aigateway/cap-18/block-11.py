# Extracted from: LibroAIGateway/cap-18-keys-encryption-master.md
# Decrypt: reconstruct MEK private key in RAM (gateway/app/api/v1/admin/break_glass.py)
async def decrypt(event_id: int, body: DecryptRequest, ...):
    # 1. Verify that the actor is admin1 or admin2
    if user_id not in {event.admin1_id, event.admin2_id}:
        raise HTTPException(403, "You are not a signer of this event")

    # 2. Validate both passwords
    if not await _verify_admin_password(db, event.admin1_id, body.admin1_password):
        raise HTTPException(403, "admin1 password invalid")
    if not await _verify_admin_password(db, event.admin2_id, body.admin2_password):
        raise HTTPException(403, "admin2 password invalid")

    # 3. Reconstruct private key in RAM
    priv_pem = await svc.reconstruct_private_key(
        kid=mek_kid,
        admin_passwords={event.admin1_id: body.admin1_password,
                         event.admin2_id: body.admin2_password},
    )
    try:
        dek = KeyEscrowService.unwrap_user_dek_with_mek(priv_pem=priv_pem, ...)
    finally:
        priv_pem = b"\\x00" * len(priv_pem)  # zero-fill best-effort
        del priv_pem

    # 4. Store DEK in Redis with TTL + session token
    session_token = f"bgsess_{secrets.token_urlsafe(32)}"
    await r.setex(f"breakglass:dek:{session_token}", 1800, base64.b64encode(dek))
