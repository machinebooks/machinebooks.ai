# Extraído de: LibroDevSecOps/cap-10-code-review-seguridad.md
def analyze_pr(context: dict) -> list[dict]:
    """Envía el diff a Claude y obtiene hallazgos de seguridad."""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=REVIEW_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": build_review_prompt(context),
            }
        ],
    )

    response_text = message.content[0].text

    try:
        result = json.loads(response_text)
        return result.get("findings", [])
    except json.JSONDecodeError:
        # Si Claude no devuelve JSON válido, intentar extraerlo
        # buscando el primer { y el último }
        start = response_text.find("{")
        end = response_text.rfind("}") + 1
        if start >= 0 and end > start:
            result = json.loads(response_text[start:end])
            return result.get("findings", [])
        return []
