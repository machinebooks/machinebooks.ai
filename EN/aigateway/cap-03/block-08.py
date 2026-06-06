# Extracted from: LibroAIGateway/cap-03-pipeline-stages.md
# reduce: triple gate before reading cache
cache_disabled = (
    ctx.query_hash is None                # no user_id
    or not purpose_cacheable              # purpose not whitelisted
    or (cfg_ttl is not None and cfg_ttl <= 0)  # admin turned it off in DB
    or no_cache_request                   # no-cache header
)
if not cache_disabled:
    cached = await cache_service.get_cached(ctx.redis, ctx.query_hash)
    if cached:
        ctx.cache_hit = True
        ctx.cached_response = cached
        return  # short-circuit
