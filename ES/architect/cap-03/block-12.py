# Extraído de: LibroTecnico/cap-03-ecosistema-claude.md
# Resolución de mappings entre tareas
# Fichero: ai_service/services/team_executor.py

def _resolve_input(self, task, task_states):
    """Resuelve input_mappings desde los outputs de tareas completadas.

    Formato: "task.<task_id>.output.<key>[.<nested_key>...]"
    Ejemplo: "task.analyze_requirements.output.requirements_summary"
             → task_states["analyze_requirements"].output["requirements_summary"]
    """
    resolved = {}
    for target_key, mapping_path in task.input_mappings.items():
        parts = mapping_path.split(".")
        if len(parts) < 4 or parts[0] != "task" or parts[2] != "output":
            continue  # Mapping con formato inválido

        source_task_id = parts[1]
        source_state = task_states.get(source_task_id)
        if not source_state or source_state.status != "completed":
            continue  # La tarea origen no ha terminado

        # Navegar por claves anidadas del output
        value = source_state.output
        for key in parts[3:]:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                value = None
                break

        if value is not None:
            resolved[target_key] = value

    return resolved
