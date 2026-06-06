# Extracted from: LibroAIGateway/cap-06-deployment-fallback.md
counts = await redis.hmget(cls._INFLIGHT_KEY, [str(d.id) for d in rows])
for d, n in zip(rows, counts):
    cap = d.max_concurrent_calls or 0
    if cap and n_i >= cap:
        continue  # already saturated
    if best is None or n_i < best_n:
        best = d; best_n = n_i
