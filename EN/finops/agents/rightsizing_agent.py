# Source: The FinOps Engineer and the Machine -- Chapter 14
# Pattern: Claude agent for rightsizing recommendations

# rightsizing_agent/agent.py
import anthropic
import json

client = anthropic.Anthropic()

RIGHTSIZING_SYSTEM_PROMPT = """You are a cloud FinOps expert specialized in instance
rightsizing. Your function is to analyze technical recommendations from AWS Compute
Optimizer and enrich them with business context to produce recommendations that an
engineering team can approve with confidence.

For each rightsizing candidate, you must:
1. Evaluate the real risk of the change (not just technical: consider the service context)
2. Verify if the proposed timing is adequate (are there nearby planned deployments?)
3. Estimate savings with precision (per month and annualized)
4. Recommend the optimal timing for the change
5. Identify the owner/responsible team that should approve

IMPORTANT:
- Be direct: "We recommend changing to X because Y. Risk: Z."
- Savings always in dollars, not percentage
- If risk is high or information is insufficient, recommend "do not act now"
- Distinguish between recommendations for production vs dev/staging environments

Respond with a JSON array where each element has:
{
  "instance_id": "...",
  "current_type": "...",
  "recommended_type": "...",
  "monthly_savings_usd": ...,
  "annual_savings_usd": ...,
  "risk_level": "low|medium|high",
  "risk_explanation": "...",
  "recommendation": "2-3 sentence text for the approver",
  "optimal_timing": "When to make the change",
  "owner_team": "Owner team if in tags"
}"""


async def generate_rightsizing_recommendations(
    business_context: str
) -> list[dict]:
    """
    Generates context-enriched rightsizing recommendations.
    Combines technical AWS data with Claude reasoning.
    """
    # Step 1: get candidates from Compute Optimizer
    candidates = get_ec2_rightsizing_candidates()

    if not candidates['candidates']:
        return []

    # Step 2: enrich with detailed metrics for top candidates
    # (limited to top 10 by savings to control token cost)
    top_candidates = sorted(
        candidates['candidates'],
        key=lambda x: x['monthly_savings_usd'],
        reverse=True
    )[:10]

    enriched = []
    for candidate in top_candidates:
        detail = get_instance_utilization_detail(candidate['instance_id'])
        enriched.append({**candidate, 'detail': detail})

    # Step 3: Claude analyzes and enriches with business context
    user_message = f"""Analyze these EC2 rightsizing candidates:

{json.dumps(enriched, indent=2, default=str)}

Current business context:
{business_context}

Generate actionable recommendations for the approval workflow.
Prioritize by descending annual savings."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=RIGHTSIZING_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}]
    )

    try:
        return json.loads(response.content[0].text)
    except json.JSONDecodeError:
        return []
