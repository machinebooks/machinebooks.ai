# Extraído de: LibroAIGateway/cap-06-deployment-fallback.md
# Consulta ZSET con latencias en ventana reciente
samples = await redis.zrangebyscore(
    cls._LATENCY_KEY.format(deployment_id=d.id), floor, now,
)
vals = [float(s) for s in samples]
avg = sum(vals) / len(vals)
