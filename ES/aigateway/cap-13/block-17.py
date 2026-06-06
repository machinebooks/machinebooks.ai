# Extraído de: LibroAIGateway/cap-13-tenants-cuotas.md
# Si el bucket permite overage, la llamada pasa.
# Pero se registra para auditoría.
if (q.used + amount) > q.entitlement:
    if q.overage_permitted:
        continue  # Permite el request
# Después del commit:
if q.used > q.entitlement:
    q.overage_count = (q.overage_count or 0) + 1
