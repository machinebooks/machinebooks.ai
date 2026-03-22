# Extraído de: LibroCyberrange/cap-17-generacion-escenarios-ia.md
# Ejemplo didáctico: cyber-range-builder/backend/services/ai/ctf_generator.py
from agents import Agent, Runner, function_tool

CTF_AGENT_SYSTEM = """Eres un creador experto de retos CTF para competiciones
de ciberseguridad. Generas challenges individuales con:

1. Título atractivo y descripción que motive sin revelar la solución
2. Categoría (web, crypto, forensics, pwn, reverse, misc, network)
3. Dificultad calibrada con puntos proporcionales
4. Flag en formato FLAG{...} con descriptor relevante
5. Hints progresivos (3 niveles: sutil, directo, casi-solución)
6. Mapping MITRE ATT&CK cuando aplique
7. Writeup de solución (visible solo para organizadores)
8. Playbook de Ansible o Dockerfile para desplegar el reto

CALIBRACIÓN DE DIFICULTAD:
- beginner (100pts): Vulnerabilidad obvia, herramienta estándar
- easy (200pts): Requiere conocer la técnica, ejecución directa
- medium (300pts): Requiere encadenar 2-3 pasos
- hard (500pts): Requiere investigación, técnica no trivial
- extreme (750pts): Técnica avanzada o cadena compleja de exploits

REGLA: La dificultad real debe coincidir con la declarada. Un reto
'easy' no debe requerir escribir exploits custom."""

ctf_agent = Agent(
    name="ctf-designer",
    model="claude-sonnet-4-6",
    instructions=CTF_AGENT_SYSTEM,
    tools=[list_vm_templates, list_available_playbooks],
)

async def generate_ctf_challenge(
    category: str,
    difficulty: str,
    topic: str = ""
) -> dict:
    """
    Genera un reto CTF individual.

    Ejemplo de uso:
        result = await generate_ctf_challenge(
            category="web",
            difficulty="medium",
            topic="SQL injection en API REST con filtro WAF"
        )
    """
    prompt = f"""Genera un reto CTF con estas características:

CATEGORÍA: {category}
DIFICULTAD: {difficulty}
TEMA (opcional): {topic or 'Libre, elige un tema interesante'}

Consulta los templates y playbooks disponibles.
Genera el JSON completo del challenge."""

    result = await Runner.run(ctf_agent, prompt)
    return result.final_output
