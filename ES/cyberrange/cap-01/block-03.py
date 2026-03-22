# Extraído de: LibroCyberrange/cap-01-que-es-cyber-range.md
# Arquitectura de integración de IA en el Cyber Range
# Ejemplo didáctico: patrones/ia/architecture.py

import anthropic

client = anthropic.Anthropic()

# Nivel 1: Generación de escenarios
# Claude genera topologías, retos y playbooks a partir de una descripción
def generate_scenario(description: str, difficulty: str) -> dict:
    """Genera un escenario completo de ciberejercicio."""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system="""Eres un diseñador de ciberejercicios con experiencia
        en entornos militares y corporativos. Genera escenarios que
        incluyan: topología de red, VMs necesarias, vulnerabilidades
        a explotar, flags con dificultad progresiva, y playbooks
        de Ansible para el despliegue automático.""",
        messages=[{
            "role": "user",
            "content": f"Genera un escenario de {difficulty} para: {description}"
        }]
    )
    return parse_scenario(response.content[0].text)

# Nivel 2: Coaching adaptativo
# Claude analiza las acciones del jugador y ofrece guía sin respuestas
def get_coaching_hint(player_actions: list, challenge: dict) -> str:
    """Genera una pista adaptativa basada en el progreso del jugador."""
    response = client.messages.create(
        model="claude-haiku-4-5",  # Velocidad para feedback inmediato
        max_tokens=256,
        system="""Eres un instructor de ciberseguridad. Guía al
        participante hacia la solución sin darla directamente.
        Analiza sus acciones y sugiere la siguiente dirección
        de investigación.""",
        messages=[{
            "role": "user",
            "content": f"Acciones del jugador: {player_actions}\n"
                       f"Reto: {challenge['description']}\n"
                       f"Objetivo: {challenge['objective']}"
        }]
    )
    return response.content[0].text

# Nivel 3: Red team automatizado
# Agentes IA que ejecutan cadenas de ataque coherentes
# (Capítulo 19 profundiza en esta arquitectura)
