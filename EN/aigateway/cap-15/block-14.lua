# Extracted from: LibroAIGateway/cap-15-rate-limiting.md
-- Atomic INCRBYFLOAT with EXPIRE only on creation
local key = KEYS[1]
local amount = tonumber(ARGV[1])
local ttl = tonumber(ARGV[2])
local existed = redis.call('EXISTS', key)
local new_val = redis.call('INCRBYFLOAT', key, amount)
if existed == 0 then
    redis.call('EXPIRE', key, ttl)
end
return new_val
