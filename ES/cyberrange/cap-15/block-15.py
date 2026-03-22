# Extraído de: LibroCyberrange/cap-15-ataques-defensa.md
# Ejemplo didáctico: agente de planificación de ataques con Claude
import anthropic

client = anthropic.Anthropic()

async def plan_attack_sequence(
    scenario_topology: dict,
    available_templates: list[dict],
    exercise_objective: str,
    difficulty: str = "medium"
) -> list[dict]:
    """
    Genera una secuencia de ataques coherente usando Claude.
    """
    # Construir contexto con templates disponibles
    templates_ctx = "\n".join([
        f"- {t['name']} (T{t['mitre_technique_id']}, "
        f"tactic={t['mitre_tactic']}, severity={t['severity']}, "
        f"kill_chain={t['kill_chain_phase']})"
        for t in available_templates
    ])

    topology_ctx = json.dumps(scenario_topology, indent=2)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system="""Eres un experto en red teaming y MITRE ATT&CK.
        Tu tarea es planificar secuencias de ataque realistas
        para ejercicios de entrenamiento en un Cyber Range.

        Reglas:
        - Seguir la progresión natural de la Cyber Kill Chain
        - Usar SOLO templates del catálogo proporcionado
        - Incluir tiempos de espera realistas entre fases
        - Adaptar la dificultad al nivel solicitado
        - Explicar la lógica de cada paso para el instructor
        """,
        messages=[{
            "role": "user",
            "content": f"""Planifica una secuencia de ataque para este
            ejercicio:

            **Objetivo:** {exercise_objective}
            **Dificultad:** {difficulty}

            **Topología:**
            {topology_ctx}

            **Templates disponibles:**
            {templates_ctx}

            Responde en JSON con la secuencia ordenada, incluyendo
            para cada paso: template_name, target_hosts, delay_minutes,
            rationale (por qué este paso en este momento).
            """
        }]
    )

    return json.loads(response.content[0].text)
