# Extraído de: LibroDevSecOps/cap-09-agente-triaje.md
def register_disagreement(
    finding_id: str,
    agent_priority: int,
    human_priority: int,
    human_reasoning: str
) -> None:
    """Registra una discrepancia entre agente y analista
    para alimentar el bucle de retroalimentación."""
    disagreement = {
        "finding_id": finding_id,
        "agent_priority": agent_priority,
        "human_priority": human_priority,
        "delta": abs(agent_priority - human_priority),
        "direction": "upgraded" if human_priority > agent_priority
                     else "downgraded",
        "human_reasoning": human_reasoning,
        "timestamp": datetime.utcnow().isoformat(),
    }

    # Persistir para análisis semanal
    with open("data/triage_disagreements.jsonl", "a") as f:
        f.write(json.dumps(disagreement) + "\n")

    # Alerta si hay más de 10 discrepancias en un día
    daily_count = count_daily_disagreements()
    if daily_count > 10:
        notify_security_lead(
            f"Alerta: {daily_count} discrepancias de triaje hoy. "
            f"Revisar calibración del agente."
        )
