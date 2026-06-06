# Extracted from: LibroAIGateway/cap-16-jwt-device-binding.md
# Login lockout (gateway/app/api/v1/auth.py:117-138)
@router.post("/login")
@limiter.limit("10/minute")
async def login(request: Request, body: LoginRequest, ...):
    ip = _client_ip(request)
    lock_key = f"login_failures:{email_hash}:{ip}"
    try:
        redis = await get_redis()
        fails = await redis.get(lock_key)
        if fails and int(fails) >= 5:
            raise HTTPException(status_code=429, detail="Demasiados intentos")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=503, detail="Servicio no disponible")
    # ... verify credentials ...
