# Extraído de: LibroDevSecOps/cap-18-runtime-security.md
# runtime_analyzer/auto_response.py
"""
Acciones de contención automática para alertas confirmadas
como TRUE_POSITIVE con severidad CRITICAL.
Cada acción es reversible y se registra para auditoría.
"""
import subprocess
import logging
from datetime import datetime

logger = logging.getLogger("auto_response")


def isolate_container(container_name: str) -> dict:
    """
    Aísla un contenedor comprometido desconectándolo
    de todas las redes excepto la de cuarentena.
    No destruye el contenedor para permitir análisis forense.
    """
    actions_taken = []

    # Desconectar de la red de producción
    result = subprocess.run(
        ["docker", "network", "disconnect",
         "production-net", container_name],
        capture_output=True, text=True, timeout=10
    )
    actions_taken.append({
        "action": "network_disconnect",
        "network": "production-net",
        "success": result.returncode == 0,
        "timestamp": datetime.utcnow().isoformat()
    })

    # Conectar a la red de cuarentena (sin acceso externo)
    result = subprocess.run(
        ["docker", "network", "connect",
         "quarantine-net", container_name],
        capture_output=True, text=True, timeout=10
    )
    actions_taken.append({
        "action": "network_connect_quarantine",
        "success": result.returncode == 0,
        "timestamp": datetime.utcnow().isoformat()
    })

    logger.critical(
        f"Contenedor {container_name} aislado. "
        f"Acciones: {actions_taken}"
    )

    return {
        "container": container_name,
        "status": "isolated",
        "actions": actions_taken,
        "forensics_note": "Contenedor preservado para análisis"
    }
