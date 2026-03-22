# Extraído de: LibroCyberrange/cap-12-sistema-ctf.md
import anthropic
from typing import Dict, Any


def generate_challenge_with_ai(
    technique_id: str,
    difficulty: str,
    challenge_type: str,
    skills: list[str],
) -> Dict[str, Any]:
    """
    Genera la descripción, pistas y configuración de un challenge
    usando Claude para acelerar la creación de contenido.
    """
    client = anthropic.Anthropic()

    system_prompt = """Eres un diseñador de challenges de ciberseguridad
    para un Cyber Range profesional. Genera challenges realistas, técnicamente
    precisos y con objetivos de aprendizaje claros.

    Formato de respuesta JSON:
    {
        "title": "Título del challenge",
        "description": "Descripción detallada con contexto narrativo",
        "flags": [
            {
                "clue": "Pista inicial visible",
                "points": 100,
                "location_hint": "Dónde colocar la flag en la VM"
            }
        ],
        "hints": [
            {
                "text": "Texto de la pista",
                "penalty_pct": 10,
                "order": 1
            }
        ],
        "setup_instructions": "Instrucciones para configurar el entorno",
        "learning_objectives": ["Objetivo 1", "Objetivo 2"]
    }"""

    user_prompt = f"""Genera un challenge de tipo '{challenge_type}' con las
    siguientes características:
    - Técnica MITRE ATT&CK: {technique_id}
    - Dificultad: {difficulty}
    - Habilidades evaluadas: {', '.join(skills)}

    El challenge debe ser realista, basado en escenarios que un profesional
    de ciberseguridad encontraría en un entorno corporativo real. Las pistas
    deben ser progresivas: la primera da una dirección general, la segunda
    reduce el espacio de búsqueda, la tercera es casi la solución."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )

    # Parsear respuesta JSON de Claude
    import json
    response_text = message.content[0].text
    challenge_data = json.loads(response_text)

    return challenge_data


def generate_adaptive_hint(
    challenge_description: str,
    user_attempts: int,
    elapsed_minutes: int,
    previous_hints: list[str],
) -> str:
    """
    Genera una pista adaptativa basada en el progreso del usuario.
    Cuantos más intentos y más tiempo, más específica es la pista.
    """
    client = anthropic.Anthropic()

    context = f"""El participante lleva {user_attempts} intentos fallidos
    y {elapsed_minutes} minutos trabajando en este challenge.

    Pistas anteriores mostradas:
    {chr(10).join(f'- {h}' for h in previous_hints) if previous_hints else 'Ninguna'}

    Challenge: {challenge_description}"""

    specificity = "general"
    if user_attempts > 5 or elapsed_minutes > 30:
        specificity = "específica"
    if user_attempts > 10 or elapsed_minutes > 60:
        specificity = "muy específica, casi revelando la técnica"

    message = client.messages.create(
        model="claude-haiku-4-5",  # Haiku para baja latencia
        max_tokens=256,
        messages=[{
            "role": "user",
            "content": f"""Genera una pista {specificity} para un participante
            atascado en un challenge de ciberseguridad. La pista debe orientar
            sin dar la respuesta directa.

            {context}

            Responde SOLO con el texto de la pista, sin explicaciones."""
        }]
    )

    return message.content[0].text
