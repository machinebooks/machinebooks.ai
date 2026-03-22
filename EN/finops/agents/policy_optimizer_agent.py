# Source: The FinOps Engineer and the Machine -- Chapter 20
# Pattern: AI agent for policy optimization

# agents/policy_optimizer_agent.py
import anthropic
from services.policy_reconciler import PolicyReconciler

client = anthropic.Anthropic()

def generate_policy_optimization_proposals(db) -> list:
    """
    Analyzes the last 30 days of usage and proposes adjustments.
    Proposals are presented as draft PRs.
    """
    usage_summary = get_usage_summary(db, days=30)
    current_policies = PolicyReconciler().get_all_policies()

    prompt = f"""
You are an expert in AI cost governance. Analyze the usage data
and current policies, and propose specific adjustments that
optimize cost without degrading service quality.

**Usage data (last 30 days):**
{usage_summary}

**Current policies (summary):**
{current_policies}

**Generate at most 3 proposals with:**
1. What to change (specific YAML field)
2. Current value vs. proposed value
3. Estimated savings
4. Proposal risk (low/medium/high)

Format: JSON list of proposals.
"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )

    # Proposals are created as draft PRs
    return parse_proposals(response.content[0].text)
