# Extraído de: LibroCyberrange/cap-21-entrenar-soc.md
# Ejemplo didáctico: orquestador de roles múltiples
# patrones/soc/orchestrator/multi_agent_exercise.py

import anthropic
from dataclasses import dataclass

client = anthropic.Anthropic()


@dataclass
class AgentRole:
    """Define un rol de Claude en el ejercicio."""
    name: str
    model: str
    system_prompt: str
    tools: list[dict]
    # Cada rol tiene su propio historial de mensajes
    messages: list[dict] = None

    def __post_init__(self):
        self.messages = self.messages or []


def create_exercise_roles(scenario_config: dict) -> dict:
    """
    Crea las tres instancias de Claude con roles separados
    para un ejercicio SOC completo.
    """
    roles = {}

    # Rol 1: Agente SOC Tier 0
    roles["tier0"] = AgentRole(
        name="SOC Triage Agent",
        model="claude-sonnet-4-6",
        system_prompt=load_prompt("soc-triage-agent.md"),
        tools=load_tools("siem", "edr", "threat_intel",
                         "classify_alert")
    )

    # Rol 2: Adversario Red Team
    roles["adversary"] = AgentRole(
        name="Red Team Adversary",
        model="claude-sonnet-4-6",
        system_prompt=load_prompt("red-team-adversary.md"),
        tools=load_tools("network_attack", "lateral_move",
                         "evasion", "exfiltrate")
    )

    # Rol 3: Coach pedagógico
    roles["coach"] = AgentRole(
        name="Training Coach",
        model="claude-haiku-4-5",
        system_prompt=load_prompt("soc-training-coach.md"),
        tools=load_tools("observe_analyst", "provide_hint",
                         "evaluate_action")
    )

    return roles


def run_exercise_tick(
    roles: dict,
    scenario_state: dict,
    analyst_action: dict | None
) -> dict:
    """
    Ejecuta un tick del ejercicio. Cada tick:
    1. El adversario decide su siguiente acción
    2. El agente Tier 0 procesa alertas nuevas
    3. El coach evalúa la acción del analista (si hay)
    4. Se actualiza el estado del escenario
    """
    results = {}

    # El adversario actúa primero (genera la amenaza)
    if scenario_state["adversary_active"]:
        adv_response = client.messages.create(
            model=roles["adversary"].model,
            max_tokens=1024,
            system=roles["adversary"].system_prompt,
            tools=roles["adversary"].tools,
            messages=roles["adversary"].messages + [{
                "role": "user",
                "content": (
                    f"Estado actual: {json.dumps(scenario_state)}\n"
                    f"Ejecuta tu siguiente acción de ataque."
                )
            }]
        )
        results["adversary_action"] = adv_response

    # El agente Tier 0 procesa alertas resultantes
    new_alerts = scenario_state.get("pending_alerts", [])
    for alert in new_alerts:
        tier0_response = client.messages.create(
            model=roles["tier0"].model,
            max_tokens=2048,
            system=roles["tier0"].system_prompt,
            tools=roles["tier0"].tools,
            messages=roles["tier0"].messages + [{
                "role": "user",
                "content": f"Nueva alerta: {json.dumps(alert)}"
            }]
        )
        results[f"tier0_alert_{alert['id']}"] = tier0_response

    # El coach evalúa la acción del analista
    if analyst_action:
        coach_response = client.messages.create(
            model=roles["coach"].model,
            max_tokens=512,
            system=roles["coach"].system_prompt,
            tools=roles["coach"].tools,
            messages=roles["coach"].messages + [{
                "role": "user",
                "content": (
                    f"El analista ha realizado: "
                    f"{json.dumps(analyst_action)}\n"
                    f"Estado del escenario: "
                    f"{json.dumps(scenario_state)}\n"
                    f"¿Hay orientación pedagógica relevante?"
                )
            }]
        )
        results["coach_feedback"] = coach_response

    return results
