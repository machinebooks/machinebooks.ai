# Source: The FinOps Engineer and the Machine -- Chapter 21
# Pattern: LLM output quality scorer

# services/quality_scorer.py
import anthropic

client = anthropic.Anthropic()


def auto_evaluate_compliance_report(
    report_text: str,
    normative_references: list,
) -> float:
    """
    Automatically evaluates a compliance report.
    Verifies correctness of referenced regulatory citations.
    Estimated cost: ~$0.002 per evaluation with claude-haiku-4-5.
    """
    references_str = "\n".join(f"- {ref}" for ref in normative_references)
    prompt = f"""Evaluate this AI response on a 0.0-1.0 scale.

Criteria:
1. Correctly cites: {references_str}
2. No incorrect factual claims
3. Complete and well-structured

Response to evaluate:
{report_text[:2000]}

Reply ONLY with a number between 0.0 and 1.0."""

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=10,
        messages=[{"role": "user", "content": prompt}],
    )
    try:
        return float(response.content[0].text.strip())
    except ValueError:
        return 0.5  # neutral value if evaluation fails
