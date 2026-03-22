# Extraído de: LibroCyberrange/cap-28-futuro-agentes-ia.md
# Agente de red team adaptativo con reinforcement learning + Claude
# Ejemplo didáctico: agents/adaptive_red_team.py

from agents import Agent, Runner, function_tool

@function_tool
def scan_target_network(target_subnet: str) -> dict:
    """Ejecuta reconocimiento contra la red objetivo."""
    # El agente RL decide qué tipo de scan ejecutar
    # basándose en las defensas detectadas previamente
    return {
        "open_ports": {"10.10.20.10": [80, 443, 3306]},
        "os_fingerprint": {"10.10.20.10": "Ubuntu 22.04"},
        "detected_defenses": ["waf_mod_security", "ids_suricata"],
    }

@function_tool
def execute_attack_technique(technique_id: str, target: str,
                              evasion_level: int = 1) -> dict:
    """Ejecuta una técnica ATT&CK contra el objetivo.

    evasion_level: 1=directo, 2=ofuscado, 3=living-off-the-land
    """
    return {
        "success": False,
        "detected": True,
        "detection_time_seconds": 12,
        "next_recommendation": "Intentar evasion_level 3"
    }

@function_tool
def adapt_strategy(current_state: dict,
                   failed_techniques: list) -> dict:
    """Consulta al modelo RL para adaptar la estrategia de ataque."""
    # El modelo RL, entrenado con miles de episodios,
    # sugiere la siguiente acción óptima dado el estado actual
    return {
        "recommended_technique": "T1055.012",  # Process Hollowing
        "reasoning": "Las técnicas directas son detectadas. "
                     "Recomendar inyección en proceso legítimo.",
        "estimated_success_probability": 0.72,
    }

adaptive_red_team = Agent(
    name="adaptive_red_team",
    model="claude-sonnet-4-6",
    instructions="""Eres un agente de red team autónomo en un Cyber Range.
    Tu objetivo es comprometer los objetivos del escenario usando técnicas
    realistas que se adapten a las defensas que encuentres.

    Reglas:
    1. Empieza siempre con reconocimiento antes de atacar
    2. Si una técnica es detectada, escala el nivel de evasión
    3. Documenta cada paso con la técnica ATT&CK correspondiente
    4. Nunca uses técnicas destructivas (solo simulación)
    5. Si todas las técnicas de un vector fallan, pivota a otro vector

    Tu objetivo es generar presión realista y usar técnicas coherentes
    que se aproximen al comportamiento de un atacante humano profesional.""",
    tools=[
        scan_target_network,
        execute_attack_technique,
        adapt_strategy,
    ],
)
