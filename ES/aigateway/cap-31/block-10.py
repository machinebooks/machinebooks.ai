# Extraído de: LibroAIGateway/cap-31-adopcion-compliance-portal.md
# Rate limit con hash anti-PII en logs — gateway/app/api/v1/compliance_portal.py:64-69
user_hash = hashlib.sha256(str(user_id).encode()).hexdigest()[:8]
logger.warning(
    "compliance:rate_limit_exceeded user=%s count=%s", user_hash, count
)
