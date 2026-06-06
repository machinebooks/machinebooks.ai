# Extraído de: LibroAIGateway/cap-19-threat-jailbreak-dlp-pii.md
# Behavioral reconnaissance detection (leak_detection_service.py:108-145)
_RECON_KEYWORDS = [".env", "/etc/passwd", "credentials", "api_key",
                    "secret_key", "private_key", "system prompt", "dump database", ...]

async def check(cls, redis_conn, device_id, prompt):
    matched = [kw for kw, rx in zip(_RECON_KEYWORDS, _RECON_RE)
               if rx.search(prompt)]
    if not matched:
        return {"suspicious": False, "score": 0}

    key = f"leak:recon:{device_id}"
    now = time.time()
    pipe = redis_conn.pipeline()
    for kw in matched:
        pipe.zadd(key, {f"{kw}:{now}": now})
    pipe.zremrangebyscore(key, 0, now - window_sec)
    pipe.zcard(key)
    results = await pipe.execute()

    if results[-2] >= threshold:  # default: 5 en 300s
        return {"suspicious": True, "score": min(results[-2], 20)}
