# Extraído de: LibroAIGateway/cap-06-deployment-fallback.md
fresh_cutoff = now - timedelta(seconds=cls._health_stale_s())  # 180s
for d in rows:
    hs = d.health_state or {}
    if hs.get("success") is False and d.last_health_check_at >= fresh_cutoff:
        continue  # degradado reciente → descartar
    survivors.append(d)
