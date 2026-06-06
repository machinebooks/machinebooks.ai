# Extraído de: LibroAIGateway/cap-06-deployment-fallback.md
strategy = (strategy or "weighted").lower()
if strategy == "latency":
    chosen = await cls._pick_lowest_latency(redis, rows)
elif strategy == "least_busy":
    chosen = await cls._pick_least_busy(redis, rows)
else:
    chosen = cls._pick_weighted(rows)
