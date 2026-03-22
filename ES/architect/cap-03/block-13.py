# Extraído de: LibroTecnico/cap-03-ecosistema-claude.md
# Planificador: identifica tareas listas para ejecución
# Fichero: ai_service/services/team_executor.py

def _find_ready_tasks(self, tasks, completed, failed, task_states):
    """Encuentra tareas cuyas dependencias están todas completadas."""
    ready = []
    for task in tasks:
        if task.task_id in completed or task.task_id in failed:
            continue
        if task_states[task.task_id].status == "running":
            continue

        deps_met = all(dep in completed for dep in task.depends_on)
        deps_failed = any(dep in failed for dep in task.depends_on)

        if deps_failed:
            # Propagar fallo: si una dependencia falló, esta tarea no puede ejecutarse
            task_states[task.task_id].status = "failed"
            task_states[task.task_id].error = "Dependency task failed"
            failed.add(task.task_id)
            continue

        if deps_met:
            ready.append(task)

    return ready
