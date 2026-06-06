# Extraído de: LibroAIGateway/cap-09-compresion-tokens.md
# gateway/app/services/compression/smart_compression.py:160-168 (sintetizado)
if cache_map and request_id:
    ttl = int(get_system_infra_value("smart_compression_cache_ttl_seconds", 900))
    cache_key = f"compress:{request_id}"
    await cache.set(cache_key, json.dumps(cache_map, default=str), redis_ttl=ttl)
