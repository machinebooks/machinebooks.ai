# Extraído de: LibroCISO/cap-20-docker-compose.md
# Ejemplo didáctico: tarea Celery para backup automatizado
# Fichero: backend/tasks/maintenance.py

from celery import shared_task
from datetime import datetime
import subprocess
import os
import logging

logger = logging.getLogger(__name__)

@shared_task(
    name="backup_database",
    queue="maintenance",
    bind=True,
    max_retries=2,
    default_retry_delay=300  # Reintentar a los 5 minutos si falla
)
def backup_database(self):
    """
    Backup nocturno de la base de datos.
    Ejecutado por Celery Beat a las 02:00 AM.

    - Dump transaccional (no bloquea escrituras)
    - Compresión gzip
    - Rotación: mantiene últimos 30 backups
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"/srv/grc/backups/{timestamp}"
    os.makedirs(backup_dir, exist_ok=True)

    db_host = os.environ.get("DB_HOST", "mysql")
    db_name = os.environ.get("DB_NAME", "grc_db")
    db_user = os.environ.get("DB_BACKUP_USER", "backup_readonly")

    dump_path = f"{backup_dir}/grc_db.sql.gz"

    try:
        # mysqldump con --single-transaction: no bloquea escrituras
        # --routines --triggers: incluir procedimientos y triggers
        # NUNCA usar shell=True con variables — riesgo de inyección de comandos
        dump_proc = subprocess.run(
            ["mysqldump", "-h", db_host, "-u", db_user,
             "--single-transaction", "--routines", "--triggers",
             "--set-gtid-purged=OFF", db_name],
            capture_output=True, timeout=3600
        )

        import gzip as gz
        with open(dump_path, 'wb') as f:
            f.write(gz.compress(dump_proc.stdout))

        result = dump_proc

        if result.returncode != 0:
            logger.error(f"mysqldump falló: {result.stderr}")
            raise self.retry(exc=Exception(result.stderr))

        file_size = os.path.getsize(dump_path)
        logger.info(
            f"Backup completado: {dump_path} ({file_size / 1024 / 1024:.1f} MB)"
        )

        # Rotación: eliminar backups con más de 30 días
        _rotate_backups(max_age_days=30)

        return {
            "status": "success",
            "path": dump_path,
            "size_mb": round(file_size / 1024 / 1024, 1),
            "timestamp": timestamp
        }

    except subprocess.TimeoutExpired:
        logger.error("Backup timeout después de 1 hora")
        raise self.retry(exc=Exception("Timeout"))


def _rotate_backups(max_age_days: int = 30):
    """Elimina backups más antiguos que max_age_days."""
    backup_root = "/srv/grc/backups"
    cutoff = datetime.now().timestamp() - (max_age_days * 86400)

    for entry in os.scandir(backup_root):
        if entry.is_dir() and entry.stat().st_mtime < cutoff:
            import shutil
            shutil.rmtree(entry.path)
            logger.info(f"Backup antiguo eliminado: {entry.name}")
