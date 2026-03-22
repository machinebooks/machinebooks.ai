# Extraído de: LibroTecnico/cap-14-agentes-orchestrator.md
class TeamExecutor:
    """Ejecuta un DAG de tareas con paralelismo en tareas independientes."""

    async def execute_team(self, config: TeamConfig) -> AsyncGenerator[str, None]:
        task_states: Dict[str, TaskState] = {
            t.task_id: TaskState(config=t) for t in config.tasks
        }
        completed: Set[str] = set()
        failed: Set[str] = set()

        while len(completed) + len(failed) < len(config.tasks):
            # Encontrar tareas cuyas dependencias están completas
            ready = self._find_ready_tasks(config.tasks, completed, failed)

            if not ready:
                # Deadlock: dependencias fallidas o circulares
                break

            # Lanzar todas las tareas listas en paralelo
            results = await asyncio.gather(
                *[self._execute_task_safe(t, task_states, config) for t in ready],
                return_exceptions=True
            )

            for task_cfg, result in zip(ready, results):
                if isinstance(result, Exception) or not result.get("success"):
                    failed.add(task_cfg.task_id)
                else:
                    completed.add(task_cfg.task_id)
                    task_states[task_cfg.task_id].output = result.get("output", {})

                yield _sse("task_complete", task_id=task_cfg.task_id)
