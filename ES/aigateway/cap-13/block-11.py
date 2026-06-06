# Extraído de: LibroAIGateway/cap-13-tenants-cuotas.md
# Fracciones automáticas: si el usuario tiene allocation mensual,
# se derivan los buckets pequeños como fracción del monthly.
USER_ALLOCATION_SESSION_FRACTION = Decimal("0.10")  # 10% del monthly
USER_ALLOCATION_DAILY_FRACTION   = Decimal("0.20")  # 20% del monthly
