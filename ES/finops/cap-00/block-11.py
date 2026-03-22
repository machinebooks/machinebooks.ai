# Extraído de: LibroFinOps/apendice-b-apis-coste-cloud.md
from azure.mgmt.costmanagement.models import Budget, BudgetTimePeriod

budget = Budget(
    category="Cost",
    amount=5000,
    time_grain="Monthly",
    time_period=BudgetTimePeriod(
        start_date="2026-04-01T00:00:00Z",
        end_date="2026-12-31T23:59:59Z"
    ),
    notifications={
        "alert80": {
            "enabled": True,
            "operator": "GreaterThan",
            "threshold": 80,
            "contact_emails": ["finops@ejemplo.com"]
        }
    }
)

scope = "/subscriptions/<TU_SUBSCRIPTION_ID>"
client.budgets.create_or_update(
    scope=scope,
    budget_name="presupuesto-produccion",
    parameters=budget
)
