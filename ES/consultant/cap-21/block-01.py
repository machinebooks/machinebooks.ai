# Extraído de: LibroConsultor/cap-21-productizacion.md
client = anthropic.Anthropic()

def detect_inconsistencies(
    dimension: str,
    responses: list[dict]
) -> list[str]:
    """Detecta contradicciones en respuestas de una dimensión."""
    responses_text = "\n".join(
        f"- Pregunta: {r['question']}\n  Respuesta: {r['answer']}"
        for r in responses
    )

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=(
            "Eres un auditor experto en madurez de IA. "
            "Analiza las respuestas de un cliente y detecta "
            "inconsistencias internas. Una inconsistencia es cuando "
            "dos respuestas se contradicen o son incompatibles. "
            "Devuelve SOLO las inconsistencias encontradas, "
            "una por línea. Si no hay inconsistencias, responde NINGUNA."
        ),
        messages=[{
            "role": "user",
            "content": (
                f"Dimensión: {dimension}\n\n"
                f"Respuestas del cliente:\n{responses_text}\n\n"
                "Lista de inconsistencias detectadas:"
            )
        }]
    )

    result = message.content[0].text.strip()
    if result == "NINGUNA":
        return []
    return [line.strip("- ") for line in result.split("\n") if line.strip()]
