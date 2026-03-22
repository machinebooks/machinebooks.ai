# Extraído de: LibroTecnico/cap-10-automatizacion-rpa.md
# Ejemplo didáctico: patrones/automation/health.py

import httpx
from datetime import datetime, timedelta

def check_selenium_grid_health() -> dict:
    """Verifica el estado del Grid de Selenium y sus nodos."""
    try:
        response = httpx.get(
            "http://selenium-hub:4444/wd/hub/status",
            timeout=5.0
        )
        data = response.json()

        nodes = data.get("value", {}).get("nodes", [])
        available = sum(1 for n in nodes if n.get("availability") == "UP")

        return {
            "status": "healthy" if available > 0 else "degraded",
            "total_nodes": len(nodes),
            "available_nodes": available,
            "hub_ready": data.get("value", {}).get("ready", False)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "total_nodes": 0,
            "available_nodes": 0
        }

def check_automation_queue_depth() -> dict:
    """Verifica el estado de la cola de automatización en Redis."""
    import redis
    r = redis.Redis.from_url(os.environ["REDIS_URL"])

    queue_length = r.llen("celery:automation")

    # Alertar si hay más de 20 tareas encoladas (puede indicar bloqueo)
    status = "healthy" if queue_length < 20 else "degraded"

    return {
        "status": status,
        "queue_depth": queue_length,
        "threshold": 20
    }
