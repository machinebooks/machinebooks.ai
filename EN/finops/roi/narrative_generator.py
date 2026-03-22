# Source: The FinOps Engineer and the Machine -- Chapter 18
# Pattern: AI-generated narrative for business case

import anthropic

def generate_executive_narrative(
    summary_json: dict,
) -> str:
    """
    Generates the executive report narrative text
    from the BusinessCaseGenerator JSON.
    """
    client = anthropic.Anthropic(api_key="<YOUR_API_KEY>")

    prompt = f"""Generate a 1-page executive report in English
for the CFO from this financial data:

{summary_json}

Requirements:
- Financial language (EBITDA, OPEX, payback, NPV)
- No technical jargon (tokens, models, prompts)
- Include limitations and assumptions
- Professional tone, data before adjectives
- Maximum 400 words"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text
