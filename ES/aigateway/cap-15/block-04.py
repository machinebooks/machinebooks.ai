# Extraído de: LibroAIGateway/cap-15-rate-limiting.md
# Rollback de los acquired anteriores antes de lanzar.
await _release_acquired(redis, acquired)
raise RateLimitExceeded(scope, "rpm", int(count), rl.rpm_limit)
