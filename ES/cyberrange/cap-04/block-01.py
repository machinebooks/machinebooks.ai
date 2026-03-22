# Extraído de: LibroCyberrange/cap-04-claude-ecosistema.md
# Agente generador de escenarios con Claude API
# Ejemplo didáctico: patrones/agentes/scenario_generator.py

import anthropic
import json

client = anthropic.Anthropic()

SCENARIO_SYSTEM_PROMPT = """Eres un experto en diseño de escenarios de ciberejercicio.
Tu trabajo es generar escenarios de entrenamiento para un Cyber Range.

REGLAS ESTRICTAS:
- Solo usa técnicas del framework MITRE ATT&CK v14.
- Los CVEs referenciados deben existir realmente (no inventar).
- Las máquinas vulnerables deben tener configuraciones realistas.
- NUNCA expongas ficheros del sistema real (/etc/shadow, /etc/passwd del host).
- Los flags deben generarse con hash SHA256 + componente aleatorio por equipo.
- Las rutas de explotación deben ser verificables paso a paso.
- Si no conoces un CVE con certeza, indica "VERIFICAR: [CVE-XXXX-XXXX]".

OUTPUT: JSON con la estructura del escenario (topología, VMs, vulnerabilidades,
flags, playbooks, guía del organizador).
"""

def generate_scenario(
    learning_objectives: list[str],
    difficulty: str,
    duration_hours: int,
    max_teams: int,
    available_templates: list[dict]
) -> dict:
    """Genera un escenario completo a partir de objetivos de aprendizaje.

    El resultado requiere revisión humana antes de desplegarse.
    El campo 'verification_notes' lista los elementos que el
    organizador DEBE verificar manualmente.
    """
    prompt = f"""Diseña un escenario de ciberejercicio con estos parámetros:

OBJETIVOS DE APRENDIZAJE:
{json.dumps(learning_objectives, indent=2, ensure_ascii=False)}

DIFICULTAD: {difficulty} (junior/intermedio/avanzado/experto)
DURACIÓN: {duration_hours} horas
EQUIPOS MÁXIMOS: {max_teams}

TEMPLATES DE VM DISPONIBLES:
{json.dumps(available_templates, indent=2, ensure_ascii=False)}

Genera el escenario completo en formato JSON."""

    response = client.messages.create(
        model="claude-opus-4-6",  # Opus para escenarios complejos
        max_tokens=8192,
        system=SCENARIO_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )

    scenario = json.loads(response.content[0].text)

    # Añadir metadatos de verificación obligatoria
    scenario["verification_notes"] = [
        "VERIFICAR: Todos los CVE referenciados existen en NVD",
        "VERIFICAR: Las rutas de explotación son técnicamente viables",
        "VERIFICAR: Ningún playbook expone ficheros reales del host",
        "VERIFICAR: Los flags generados son únicos por equipo",
        "VERIFICAR: Las reglas de firewall aíslan correctamente las workzones",
    ]
    scenario["status"] = "pending_review"  # NUNCA 'ready' automáticamente

    return scenario
