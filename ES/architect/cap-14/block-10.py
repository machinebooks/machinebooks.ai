# Extraído de: LibroTecnico/cap-14-agentes-orchestrator.md
def _resolve_input(self, task: TaskConfig, task_states: Dict[str, TaskState]):
    """Resuelve input_mappings desde resultados de tareas previas."""
    resolved = {}
    for target_key, mapping_path in task.input_mappings.items():
        parts = mapping_path.split(".")
        # Formato: "task.analyze_requirements.output.requirements_summary"
        source_task_id = parts[1]
        source_state = task_states.get(source_task_id)
        if source_state and source_state.status == "completed":
            value = source_state.output
            for key in parts[3:]:  # Navegar dentro del output
                value = value.get(key) if isinstance(value, dict) else None
            if value is not None:
                resolved[target_key] = value
    return resolved
