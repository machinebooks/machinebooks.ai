# Extraído de: LibroTecnico/cap-14-agentes-orchestrator.md
# Ejemplo: estructura del registro de diagnóstico que genera el sistema
{
    "session_id": "sess_a3f2b1",
    "agent_slug": "propuesta-tecnica",
    "user_query": "Genera una propuesta para el proyecto ID-4821",
    "total_iterations": 7,
    "stop_reason": "max_iterations_reached",  # Señal de fallo
    "iterations": [
        {
            "iteration": 1,
            "tool_invoked": "get_project_status",
            "args": {"project_id": "ID-4821"},
            "result_status": "not_found",   # Herramienta no encontró el proyecto
            "claude_reasoning": "El proyecto no existe, intentaré buscarlo con otro método"
        },
        {
            "iteration": 2,
            "tool_invoked": "search_opportunities",
            # Claude intentó buscar el proyecto en oportunidades en lugar de proyectos
            "args": {"keywords": "ID-4821"},
            "result_status": "empty",
            "claude_reasoning": "Sin resultados, probaré búsqueda documental..."
        }
        # ... 5 iteraciones más de búsqueda infructuosa
    ],
    "diagnosis": "El proyecto ID-4821 existe en la BD como 'PRY-4821'. El agente no tenía
                  acceso a la herramienta get_project_by_code que resuelve esta búsqueda.
                  Causa: herramienta no asignada al agente."
}
