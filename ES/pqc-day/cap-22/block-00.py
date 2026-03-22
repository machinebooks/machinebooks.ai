# Extraído de: LibroPQC/cap-22-celery.md
from celery import Task
from extensions import db


class DatabaseTask(Task):
    """Clase base para tareas Celery con gestión automática
    de sesiones SQLAlchemy.

    Garantiza que la sesión se cierra y se limpia después
    de cada ejecución, independientemente del resultado.
    Sin esto, las conexiones a MySQL se acumulan hasta
    alcanzar max_connections y la plataforma se detiene.
    """
    abstract = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        """Se ejecuta SIEMPRE después de la tarea, con éxito o fallo."""
        db.session.remove()

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Limpieza adicional en caso de error: rollback explícito
        para evitar que transacciones a medias contaminen la sesión."""
        try:
            db.session.rollback()
        except Exception:
            pass  # Si el rollback falla, remove() lo resolverá
        finally:
            db.session.remove()
