# Extraído de: LibroTecnico/cap-08-colas-trabajo.md
# Ejemplo didáctico: envío a dead-letter queue
# Patrón: tasks/base.py

def _send_to_dead_letter_queue(
    task_id: str,
    task_name: str,
    exc: Exception,
    args: tuple
) -> None:
    """
    Persiste tareas fallidas en base de datos para análisis posterior.
    Redis no es suficiente: los datos deben sobrevivir reinicios.
    """
    from models.platform import FailedTask
    from database import db_session

    with db_session() as session:
        failed = FailedTask(
            task_id=task_id,
            task_name=task_name,
            error_type=type(exc).__name__,
            error_message=str(exc)[:2000],
            task_args=str(args)[:1000],
            failed_at=datetime.utcnow(),
            reviewed=False,
        )
        session.add(failed)
        session.commit()

    # Alerta al equipo de operaciones si el fallo es crítico
    if _is_critical_task(task_name):
        send_alert_email(
            subject=f"Tarea crítica fallida: {task_name}",
            body=f"La tarea {task_id} ha agotado todos sus reintentos.\n"
                 f"Error: {exc}\n"
                 f"Requiere intervención manual.",
        )
