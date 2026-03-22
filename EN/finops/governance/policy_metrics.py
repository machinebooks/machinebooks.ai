# Source: The FinOps Engineer and the Machine -- Chapter 20
# Pattern: Policy effectiveness metrics

# services/policy_metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Requests blocked by policy
policy_blocks = Counter(
    "finops_policy_blocks_total",
    "Requests blocked by FinOps policy",
    ["tenant_id", "task_type", "reason"],
)

# Requests that triggered budget alert
policy_alerts = Counter(
    "finops_policy_budget_alerts_total",
    "Requests that exceeded the alert threshold",
    ["tenant_id", "task_type"],
)

# Policy evaluation latency
policy_eval_duration = Histogram(
    "finops_policy_eval_seconds",
    "Policy evaluation latency per request",
    ["task_type"],
)

# Budget consumed as a percentage of the limit
budget_usage_ratio = Gauge(
    "finops_budget_usage_ratio",
    "Percentage of budget consumed in the period",
    ["tenant_id", "task_type"],
)
