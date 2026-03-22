# Source: The FinOps Engineer and the Machine -- Chapter 20
# Pattern: OPA Rego policy for budget enforcement

# policies/rego/budget.rego
package finops.budget

import future.keywords.if
import future.keywords.contains

# Allow the request if spending is below 80%
allow if {
    tenant_budget := data.tenants[input.tenant_id].monthly_budget_eur
    current_spend := input.current_spend_eur
    current_spend < tenant_budget * 0.80
}

# Apply throttling between 80% and 100%
throttle if {
    tenant_budget := data.tenants[input.tenant_id].monthly_budget_eur
    current_spend := input.current_spend_eur
    current_spend >= tenant_budget * 0.80
    current_spend < tenant_budget
}

# Block when the budget is exhausted
block if {
    tenant_budget := data.tenants[input.tenant_id].monthly_budget_eur
    current_spend := input.current_spend_eur
    current_spend >= tenant_budget
}

# The model is determined by the task type
model_for_task := model if {
    rules := data.routing_rules
    some rule in rules
    rule.task_type == input.task_type
    model := rule.model
}
