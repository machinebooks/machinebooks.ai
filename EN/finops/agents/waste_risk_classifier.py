# Source: The FinOps Engineer and the Machine -- Chapter 15
# Pattern: Risk classifier for waste cleanup actions

# waste_scanner/risk_classifier.py
import anthropic
import json

client = anthropic.Anthropic()

WASTE_CLASSIFIER_PROMPT = """You are an expert in operational security and cloud FinOps.
Your function is to classify the risk of deleting potentially orphaned cloud resources.

For each resource, evaluate the deletion risk considering:
- Age: older resources are safer to delete
- Tags: 'prod' or 'production' tags increase risk
- Name: names suggesting criticality increase risk
- Last access: recent access increases risk
- Resource type: empty load balancers are almost always safe to delete

Precautionary principle: when in doubt, classify as HIGH risk.
The savings from deleting a resource never justifies losing critical data.

For each resource, respond with:
{
  "resource_id": "...",
  "risk_level": "low|medium|high",
  "risk_reasons": ["reason 1", "reason 2"],
  "recommendation": "One sentence: delete|investigate|keep",
  "notes": "Additional context if applicable"
}"""


def classify_waste_risk(resources: list[dict]) -> list[dict]:
    """
    Classifies the risk of deleting each orphaned resource.
    Groups in a single prompt to minimize token cost.
    """
    user_message = f"""Classify the deletion risk of these orphaned resources:

{json.dumps(resources, indent=2, default=str)}

Return a JSON array with one classification object per resource."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=WASTE_CLASSIFIER_PROMPT,
        messages=[{"role": "user", "content": user_message}]
    )

    try:
        classifications = json.loads(response.content[0].text)
        if isinstance(classifications, dict):
            classifications = [classifications]
        return classifications
    except json.JSONDecodeError:
        # If parsing fails, all resources go to high risk for safety
        return [
            {'resource_id': r['resource_id'], 'risk_level': 'high',
             'risk_reasons': ['Error in automatic classification'],
             'recommendation': 'investigate'}
            for r in resources
        ]
