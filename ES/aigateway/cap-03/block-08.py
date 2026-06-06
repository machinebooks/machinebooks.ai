# Extraído de: LibroAIGateway/cap-03-pipeline-stages.md
# reduce: triple gate antes de leer cache
cache_disabled = (
    ctx.query_hash is None                # sin user_id
    or not purpose_cacheable              # purpose no whitelisteado
    or (cfg_ttl is not None and cfg_ttl <= 0)  # admin lo apago en BD
    or no_cache_request                   # header no-cache
)
if not cache_disabled:
    cached = await cache_service.get_cached(ctx.redis, ctx.query_hash)
    if cached:
        ctx.cache_hit = True
        ctx.cached_response = cached
        return  # cortocircuito
