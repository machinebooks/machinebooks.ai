# Extraído de: LibroAIGateway/cap-18-keys-cifrado-master.md
# Anti-bruteforce en unwrap (gateway/app/api/v1/user_keys.py)
@router.get("/users/me/keys/wrap-b")
async def get_wrap_b(request, db: AsyncSession):
    user_id = await _user_id(request)
    window_min = await _cfg_int(db, "me.keys.unwrap.window_minutes")   # 15
    max_attempts = await _cfg_int(db, "me.keys.unwrap.max_attempts")   # 5
    fails = count_failures(db, user_id, ip, window_min)
    if fails >= max_attempts:
        raise HTTPException(429, f"Demasiados intentos. Espera {window_min} min.")
