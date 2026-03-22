# Extraído de: LibroConsultor/cap-15-madurez-ia.md
client = anthropic.Anthropic()

def conduct_interview_turn(
    question: AssessmentQuestion,
    stakeholder_role: str,
    previous_responses: list[dict],
    contradictions: list[str]
) -> dict:
    """Gestiona un turno de entrevista con contexto acumulado."""

    # Construir contexto de respuestas previas para triangulación
    context_summary = "\n".join(
        f"- {r['stakeholder']} ({r['role']}): {r['summary']}"
        for r in previous_responses
        if r["question_id"] == question.id
    )

    contradiction_note = ""
    if contradictions:
        contradiction_note = (
            "\n\nSe han detectado inconsistencias en respuestas "
            "previas sobre este tema:\n"
            + "\n".join(f"- {c}" for c in contradictions)
            + "\nFormula preguntas de clarificación sin confrontar."
        )

    system_prompt = f"""Eres un consultor de IA senior realizando un
assessment de madurez. Estás entrevistando a un {stakeholder_role}.

Pregunta actual: {question.text}

Respuestas previas de otros stakeholders sobre esta pregunta:
{context_summary or "Ninguna aún — primera entrevista sobre este tema."}
{contradiction_note}

Preguntas de seguimiento disponibles:
{chr(10).join(f"- {fq}" for fq in question.follow_ups)}

Instrucciones:
- Adapta el lenguaje al perfil del entrevistado
- Si la respuesta es vaga, profundiza con las preguntas de seguimiento
- Si detectas inconsistencia con respuestas previas, clarifica sin acusar
- Registra si el entrevistado ofrece evidencia o solo declaraciones
- Al final del turno, genera un resumen estructurado"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": "Inicia el turno de entrevista."}]
    )

    return {
        "question_id": question.id,
        "dimension": question.dimension.value,
        "stakeholder_role": stakeholder_role,
        "raw_response": response.content[0].text,
        "evidence_provided": False,  # Se actualiza tras la entrevista
    }
