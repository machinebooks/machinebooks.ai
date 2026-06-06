# Extracted from: LibroAIGateway/cap-13-tenants-quotas.md
# Automatic fractions: if the user has a monthly allocation,
# smaller buckets are derived as a fraction of monthly.
USER_ALLOCATION_SESSION_FRACTION = Decimal("0.10")  # 10% of monthly
USER_ALLOCATION_DAILY_FRACTION   = Decimal("0.20")  # 20% of monthly
