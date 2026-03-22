# Extraído de: LibroDevSecOps/cap-21-policy-as-code.md
# scripts/explain_policy.py
import anthropic

client = anthropic.Anthropic()

def explain_policy_violation(
    policy_code: str,
    violation_message: str,
    input_data: dict
) -> str:
    """Explica una violación de política en lenguaje natural."""
    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": (
                f"Política Rego:\n