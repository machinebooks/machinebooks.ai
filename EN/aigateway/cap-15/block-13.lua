# Extracted from: LibroAIGateway/cap-15-rate-limiting.md
-- Atomic INCR with EXPIRE only on creation
local key = KEYS[1]
local ttl = tonumber(ARGV[1])
local current = redis.call('INCR', key)
if current == 1 then
    redis.call('EXPIRE', key, ttl)
end
return current
