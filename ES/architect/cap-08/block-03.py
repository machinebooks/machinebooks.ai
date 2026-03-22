# Extraído de: LibroTecnico/cap-08-colas-trabajo.md
# Ejemplo didáctico: patrones de reintento por tipo de tarea
# Patrón: tasks/base.py

from celery import Task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


class AITask(Task):
    """
    Tarea base para operaciones de IA.
    Reintentos con backoff exponencial y logging de costes.
    """
    abstract = True
    max_retries = 5
    # Backoff: 1min, 2min, 4min, 8min, 16min
    default_retry_delay = 60

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Registrar fallo en auditoría y notificar si es persistente."""
        logger.error(
            "AI task failed",
            extra={
                "task_id": task_id,
                "task_name": self.name,
                "error": str(exc),
                "retries": self.request.retries,
            }
        )
        if self.request.retries >= self.max_retries:
            # Mover a dead-letter queue para análisis posterior
            _send_to_dead_letter_queue(task_id, self.name, exc, args)

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Log de reintento con contexto del error."""
        wait = 60 * (2 ** self.request.retries)
        logger.warning(
            f"AI task retry {self.request.retries}/{self.max_retries}",
            extra={"wait_seconds": wait, "error": str(exc)},
        )


class AutomationTask(Task):
    """
    Tarea base para bots RPA.
    Reintentos agresivos porque los portales web son inestables.
    """
    abstract = True
    max_retries = 180       # Hasta 180 intentos (caso real documentado)
    default_retry_delay = 60  # 1 minuto entre intentos → 3 horas máx.

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """El fallo definitivo de un bot dispara notificación al administrador."""
        logger.critical(
            "Automation bot exhausted all retries",
            extra={
                "task_id": task_id,
                "bot": self.name,
                "total_attempts": self.max_retries,
            }
        )
        # Notificar al equipo de operaciones para intervención manual
        _notify_operations_team(task_id, self.name, str(exc))
