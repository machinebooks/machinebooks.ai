# Extraído de: LibroConsultor/cap-25-confianza-cliente.md
from anthropic import Anthropic
from dataclasses import dataclass

@dataclass
class ClientEducationSession:
    """Estructura una sesión de educación sobre IA
    adaptada al sector y nivel del interlocutor."""
    client_sector: str
    audience_level: str  # "executive", "technical", "mixed"
    concerns: list[str]  # Preocupaciones expresadas por el cliente

def generate_education_agenda(
    session: ClientEducationSession
) -> dict:
    """Genera agenda personalizada para sesión de
    desmitificación de IA según contexto del cliente."""

    client = Anthropic()

    prompt = f"""Genera una agenda de 90 minutos para una sesión
    de 'Desmitificación de IA para decisores' con estas
    características:

    Sector del cliente: {session.client_sector}
    Audiencia: {session.audience_level}
    Preocupaciones expresadas: {', '.join(session.concerns)}

    La agenda debe incluir:
    1. Qué puede y qué no puede hacer un LLM (15 min)
    2. Demostración práctica adaptada al sector (20 min)
    3. Cómo se protegen los datos del cliente (15 min)
    4. Supervisión humana: qué significa en la práctica (15 min)
    5. Oportunidades de IA para la organización (15 min)
    6. Preguntas abiertas (10 min)

    Adapta los ejemplos al sector {session.client_sector}.
    Si la audiencia es 'executive', evita jerga técnica.
    Aborda directamente las preocupaciones listadas.

    Devuelve la agenda en formato JSON con campos:
    titulo, bloques (lista de objetos con titulo, duracion,
    puntos_clave, ejemplo_sector).
    """

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    import json
    try:
        return json.loads(response.content[0].text)
    except json.JSONDecodeError:
        return {"error": "Formato no estructurado",
                "raw": response.content[0].text}
