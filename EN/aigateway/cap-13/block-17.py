# Extracted from: LibroAIGateway/cap-13-tenants-quotas.md
# If the bucket allows overage, the call is allowed.
# But it is recorded for audit.
if (q.used + amount) > q.entitlement:
    if q.overage_permitted:
        continue  # Allows the request
# After commit:
if q.used > q.entitlement:
    q.overage_count = (q.overage_count or 0) + 1
