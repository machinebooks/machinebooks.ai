# Extraído de: LibroConsultor/cap-21-productizacion.md
from claude_agent_sdk import Agent, tool
from datetime import datetime

@tool
def verify_control_evidence(
    control_id: str,
    framework: str,
    evidence_sources: list[str]
) -> dict:
    """Verifica si la evidencia de un control sigue siendo válida."""
    # Recopilar evidencias (APIs, documentos, configuraciones)
    evidence_data = collect_evidence(evidence_sources)

    message = client.messages.create(
        model="claude-haiku-4-5",  # Haiku para verificaciones frecuentes
        max_tokens=512,
        system=(
            f"Eres un auditor de {framework}. Evalúa si la evidencia "
            "presentada demuestra cumplimiento del control. "
            "Responde con: CUMPLE, CUMPLE_PARCIAL o NO_CUMPLE, "
            "seguido de una justificación en una frase."
        ),
        messages=[{
            "role": "user",
            "content": (
                f"Control: {control_id}\n"
                f"Evidencia recopilada:\n{evidence_data}\n"
                f"Fecha de verificación: {datetime.now().isoformat()}\n"
                "Evaluación:"
            )
        }]
    )

    response = message.content[0].text.strip()
    status = response.split(",")[0].strip() if "," in response else response.split()[0]

    return {
        "control_id": control_id,
        "framework": framework,
        "status": status,
        "justification": response,
        "verified_at": datetime.now().isoformat(),
        "cost_usd": 0.003,  # Coste estimado por verificación con Haiku
    }
