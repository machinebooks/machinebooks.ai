# Extraído de: LibroFinOps/apendice-b-apis-coste-cloud.md
from google.cloud import billing_budgets_v1

budget_client = billing_budgets_v1.BudgetServiceClient()

budget = billing_budgets_v1.Budget(
    display_name="presupuesto-produccion",
    budget_filter=billing_budgets_v1.Filter(
        projects=[f"projects/<TU_PROJECT_NUMBER>"]
    ),
    amount=billing_budgets_v1.BudgetAmount(
        specified_amount={"currency_code": "USD", "units": 5000}
    ),
    threshold_rules=[
        billing_budgets_v1.ThresholdRule(
            threshold_percent=0.8,
            spend_basis="CURRENT_SPEND"
        ),
        billing_budgets_v1.ThresholdRule(
            threshold_percent=1.0,
            spend_basis="CURRENT_SPEND"
        )
    ]
)

parent = "billingAccounts/<TU_BILLING_ACCOUNT_ID>"
created = budget_client.create_budget(parent=parent, budget=budget)
print(f"Presupuesto creado: {created.name}")
