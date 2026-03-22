# Extraído de: LibroFinOps/cap-20-policy-as-code.md
# policies/rego/budget.rego
package finops.budget

import future.keywords.if
import future.keywords.contains

# Permite la solicitud si el gasto está por debajo del 80%
allow if {
    tenant_budget := data.tenants[input.tenant_id].monthly_budget_eur
    current_spend := input.current_spend_eur
    current_spend < tenant_budget * 0.80
}

# Aplica throttling entre el 80% y el 100%
throttle if {
    tenant_budget := data.tenants[input.tenant_id].monthly_budget_eur
    current_spend := input.current_spend_eur
    current_spend >= tenant_budget * 0.80
    current_spend < tenant_budget
}

# Bloquea cuando el presupuesto está agotado
block if {
    tenant_budget := data.tenants[input.tenant_id].monthly_budget_eur
    current_spend := input.current_spend_eur
    current_spend >= tenant_budget
}

# El modelo viene determinado por el tipo de tarea
model_for_task := model if {
    rules := data.routing_rules
    some rule in rules
    rule.task_type == input.task_type
    model := rule.model
}
