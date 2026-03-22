# Extraído de: LibroTecnico/cap-10-automatizacion-rpa.md
# Ejemplo didáctico: patrones/automation/tasks.py

from celery import shared_task
from celery.utils.log import get_task_logger
import redis
import json
import os

logger = get_task_logger(__name__)

def _get_redis_client() -> redis.Redis:
    """Conexión Redis reutilizable — URL con autenticación desde variable de entorno."""
    return redis.Redis.from_url(os.environ["REDIS_URL"])

@shared_task(
    bind=True,
    queue="automation",
    max_retries=3,
    default_retry_delay=60,   # 1 minuto entre reintentos
    acks_late=True,           # Confirmar solo cuando la tarea termina
    soft_time_limit=1800,     # 30 minutos de límite suave
    time_limit=2100           # 35 minutos de límite duro
)
def run_portal_sync(self, task_config: dict):
    """Tarea Celery para sincronización con el portal corporativo.

    task_config incluye: user_id, credential_id, sync_type, options
    """
    task_id = self.request.id
    user_id = task_config["user_id"]

    # Actualizar estado de la tarea en Redis para la UI
    _update_task_status(task_id, "running", "Iniciando conexión al Grid...")

    # Recuperar credenciales del vault (nunca del config directo)
    try:
        credentials = _get_credentials_from_vault(task_config["credential_id"])
    except Exception as e:
        _update_task_status(task_id, "failed", f"Error recuperando credenciales: {e}")
        raise

    redis_client = _get_redis_client()

