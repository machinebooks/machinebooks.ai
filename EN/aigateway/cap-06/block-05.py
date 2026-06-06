# Extracted from: LibroAIGateway/cap-06-deployment-fallback.md
# Cooldown filter — deployments with recent 429
ids = [d.id for d in rows]
cooldowned = await cls._cooldowned_ids(db, ids)
rows = [d for d in rows if d.id not in cooldowned]
