# Extraído de: LibroFinOps/cap-06-atribucion.md
# Estructura conceptual del BudgetConfig
BudgetConfig(
    scope="global",            # o "service" o "user"
    scope_id=None,             # None para global, nombre del servicio o user_id
    period="monthly",          # daily / weekly / monthly
    budget_usd=500.00,         # límite de presupuesto en USD
    alert_threshold=0.80,      # alerta al 80% del presupuesto
    block_threshold=1.00,      # bloqueo al 100%
)
