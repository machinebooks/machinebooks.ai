# Extraído de: LibroTecnico/cap-03-ecosistema-claude.md
# Motor de ejecución: bucle principal del DAG
# Fichero: ai_service/services/team_executor.py

class TeamExecutor:
    """Ejecuta un DAG de tareas en orden topológico, lanzando
    tareas independientes en paralelo con asyncio.gather."""

    async def execute_team(self, config, team_db_id=None):
        """Ejecuta todas las tareas respetando dependencias.
        Genera eventos SSE para progreso en tiempo real."""
        task_states = {t.task_id: TaskState(config=t) for t in config.tasks}
        completed, failed = set(), set()
        total = len(config.tasks)

        yield _sse("team_start", team_name=config.team_name, total_tasks=total)

        while len(completed) + len(failed) < total:
            # Encontrar tareas cuyas dependencias están resueltas
            ready = self._find_ready_tasks(
                config.tasks, completed, failed, task_states
            )

            if not ready:
                # Deadlock: dependencias irresolubles o circulares
                for tid in self._remaining(config.tasks, completed, failed):
                    task_states[tid].status = "failed"
                    failed.add(tid)
                break

            # Lanzar todas las tareas listas en paralelo
            for t in ready:
                task_states[t.task_id].status = "running"
                yield _sse("task_start", task_id=t.task_id, title=t.title)

            results = await asyncio.gather(
                *[self._execute_task_safe(t, task_states, config)
                  for t in ready],
                return_exceptions=True,
            )

            for task_cfg, result in zip(ready, results):
                # Clasificar resultado y actualizar estado
                if isinstance(result, Exception) or not result.get("success"):
                    task_states[task_cfg.task_id].status = "failed"
                    failed.add(task_cfg.task_id)
                else:
                    task_states[task_cfg.task_id].status = "completed"
                    task_states[task_cfg.task_id].output = result["output"]
                    completed.add(task_cfg.task_id)

                yield _sse("team_progress", completed=len(completed),
                           failed=len(failed), total=total)

        yield _sse("team_complete", summary=self._build_summary(task_states))
