# Extraído de: LibroFinOps/cap-20-policy-as-code.md
# En el pipeline CI/CD
def check_budget_increase(old_policy: dict, new_policy: dict) -> list:
    """
    Detecta aumentos de presupuesto superiores al 20%.
    Si los hay, exige aprobación del equipo FinOps.
    """
    alerts = []
    for tenant in new_policy.get("tenants", []):
        tenant_id = tenant["id"]
        old_budget = _find_budget(old_policy, tenant_id)
        new_budget = tenant.get("monthly_budget_eur", old_budget)

        if old_budget and new_budget > old_budget * 1.20:
            increase_pct = (new_budget - old_budget) / old_budget * 100
            alerts.append({
                "type": "budget_increase_requires_approval",
                "tenant_id": tenant_id,
                "old_budget": old_budget,
                "new_budget": new_budget,
                "increase_pct": round(increase_pct, 1),
                "required_approver": "finops_team",
            })
    return alerts
