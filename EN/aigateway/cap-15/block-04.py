# Extracted from: LibroAIGateway/cap-15-rate-limiting.md
# Rollback the previously acquired ones before raising.
await _release_acquired(redis, acquired)
raise RateLimitExceeded(scope, "rpm", int(count), rl.rpm_limit)
