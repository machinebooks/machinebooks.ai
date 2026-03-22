# Extraído de: LibroTecnico/cap-08-colas-trabajo.md
# Ejemplo didáctico: bloqueo distribuido para tareas no idempotentes
# Patrón: tasks/utils/locking.py

import redis
from contextlib import contextmanager

# URL con autenticación — nunca sin contraseña en producción
r = redis.from_url(os.environ["REDIS_URL"])

@contextmanager
def task_lock(lock_id: str, expire: int = 3600):
    """
    Bloqueo distribuido para garantizar ejecución única de tareas críticas.
    Si otro worker tiene el bloqueo, la tarea se descarta silenciosamente.
    """
    lock_key = f"celery_lock:{lock_id}"
    # SET NX EX: sólo asigna si no existe, con TTL de seguridad
    acquired = r.set(lock_key, "1", nx=True, ex=expire)

    if not acquired:
        # Otra instancia está ejecutando esta tarea
        raise TaskAlreadyRunningError(f"Task {lock_id} already running")

    try:
        yield
    finally:
        # Siempre liberar el bloqueo al terminar
        r.delete(lock_key)
