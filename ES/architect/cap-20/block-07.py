# Extraído de: LibroTecnico/cap-20-docker.md
# Ejemplo didáctico: patrones/monitoring/health_check_service.py
import time
import redis
import requests
from sqlalchemy import text
from celery.app.control import Control

class HealthCheckService:
    """
    Servicio de verificación de salud de la plataforma completa.
    Implementa dos modos: quick (DB + Redis, <200ms) y full (11 servicios, <3s).
    """

    def __init__(self, db_sessions: dict, redis_client, celery_app):
        self.dbs = db_sessions        # {'ops': session, 'core': session, 'analytics': session}
        self.redis = redis_client
        self.celery = celery_app

    def quick_check(self) -> dict:
        """
        Verificación rápida para readiness probe de Docker y load balancer.
        Solo comprueba DB principal y Redis: los dos servicios críticos de los que
        depende cada petición HTTP al backend.
        """
        results = {}
        overall = "healthy"

        # Verificación MySQL principal (operations_db)
        start = time.monotonic()
        try:
            self.dbs['ops'].execute(text("SELECT 1"))
            results['mysql_ops'] = {
                "status": "healthy",
                "latency_ms": round((time.monotonic() - start) * 1000, 2)
            }
        except Exception as e:
            results['mysql_ops'] = {"status": "unhealthy", "error": str(e)}
            overall = "unhealthy"

        # Verificación Redis
        start = time.monotonic()
        try:
            self.redis.ping()
            results['redis'] = {
                "status": "healthy",
                "latency_ms": round((time.monotonic() - start) * 1000, 2)
            }
        except Exception as e:
            results['redis'] = {"status": "unhealthy", "error": str(e)}
            overall = "unhealthy"

        return {"status": overall, "checks": results, "mode": "quick"}

