# Extraído de: LibroCyberrange/cap-28-futuro-agentes-ia.md
# Pipeline de generación autónoma de escenarios
# Ejemplo didáctico: agents/scenario_generator.py

import anthropic
from agents import Agent, Runner, function_tool
from datetime import datetime

@function_tool
def fetch_threat_intelligence(sector: str, days: int = 7) -> dict:
    """Consulta feeds de inteligencia de amenazas recientes."""
    # Integración con MITRE ATT&CK, NVD y CISA KEV
    # Filtra por sector y ventana temporal
    return {
        "cves": [...],  # CVEs activamente explotados
        "ttps": [...],  # Técnicas ATT&CK más usadas esta semana
        "campaigns": [...],  # Campañas activas relevantes al sector
    }

@function_tool
def get_player_profile(player_id: str) -> dict:
    """Obtiene el perfil de competencias del participante."""
    # Consulta la base de datos del Cyber Range
    return {
        "mastered_techniques": ["T1566.001", "T1059.001"],
        "weak_areas": ["T1055", "T1070.004"],
        "difficulty_level": 3,  # 1-5
        "last_exercises": [...],
    }

@function_tool
def generate_ansible_playbook(scenario_spec: dict) -> str:
    """Genera el playbook de Ansible para desplegar el escenario."""
    # Traduce la especificación a infraestructura desplegable
    return "playbook_content_yaml"

@function_tool
def validate_scenario(scenario_id: str) -> dict:
    """Ejecuta la cadena de ataque en modo verificación."""
    # Lanza un agente atacante contra el escenario generado
    return {
        "solvable": True,
        "estimated_time_minutes": 45,
        "unintended_paths": [],
    }

# Agente orquestador que decide qué escenario generar
scenario_orchestrator = Agent(
    name="scenario_orchestrator",
    model="claude-sonnet-4-6",
    instructions="""Eres el orquestador de generación de escenarios de un
    Cyber Range profesional. Tu objetivo es crear escenarios que:
    1. Reflejen amenazas actuales y relevantes para el sector del participante
    2. Se adapten al nivel demostrado del participante
    3. Cubran técnicas que el participante aún no domina
    4. Sean verificablemente resolubles antes de presentarse al participante

    Nunca generes escenarios que el participante ya haya completado.
    Prioriza técnicas de la cadena kill-chain que el participante
    no ha practicado en los últimos 30 días.""",
    tools=[
        fetch_threat_intelligence,
        get_player_profile,
        generate_ansible_playbook,
        validate_scenario,
    ],
)
