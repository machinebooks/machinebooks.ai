# Extracted from: LibroAIGateway/cap-18-keys-encryption-master.md
# CSE key registration (gateway/app/api/v1/user_keys.py)
@router.post("/users/me/keys")
async def register_key(body: RegisterKeyRequest, ...):
    user_id = await _user_id(request)
    if body.key_purpose not in {"conversation", "backup", "attachment"}:
        raise HTTPException(400, "Invalid key_purpose")

    # Upsert: INSERT ... ON DUPLICATE KEY UPDATE
    await db.execute(text(
        "INSERT INTO user_keys "
        "(id, user_id, key_purpose, algorithm, wrap_b_*, wrap_c_*) "
        "VALUES (...) "
        "ON DUPLICATE KEY UPDATE wrap_b_ct=VALUES(...), updated_at=VALUES(...)"
    ))
    # Detect overwrite → audit as security event
    if is_overwrite:
        await SecurityEventService.emit(db, "user_key_rewrapped", ...)
