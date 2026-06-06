# Extraído de: LibroAIGateway/cap-08-caching.md
# gateway/app/services/cache_service.py:253-377 (sintetizado)
async def get_cached(redis, query_hash: str) -> dict | None:
    raw = await redis.get(f"chat:cache:{query_hash}")
    if not raw:
        return None
    if raw.startswith("enc_cache:"):
        # Cache cifrado: descifra con AES-256-GCM antes de parsear
        decrypted = decrypt_field(raw[len("enc_cache:"):])
        return json.loads(decrypted) if decrypted else None
    return json.loads(raw)

async def set_cached(redis, query_hash: str, response: dict,
                     ttl: int = 300, encrypt: bool = False) -> None:
    payload = json.dumps(response, default=str)
    if encrypt:
        encrypted = encrypt_field(payload)
        if not encrypted:  # IMPORTANTE: nunca guardar plaintext si cifra falló
            return
        payload = "enc_cache:" + encrypted
    await redis.setex(f"chat:cache:{query_hash}", ttl, payload)
