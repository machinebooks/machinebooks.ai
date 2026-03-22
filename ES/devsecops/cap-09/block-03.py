# Extraído de: LibroDevSecOps/cap-09-agente-triaje.md
import yaml
from pathlib import Path
from claude_agent_sdk import tool

# Inventario de servicios cargado desde YAML
SERVICE_INVENTORY_PATH = Path("config/service-inventory.yaml")

@tool
def check_service_exposure(service_name: str) -> dict:
    """Determina si un servicio está expuesto a internet,
    requiere autenticación y qué tipo de datos procesa."""
    # Cargar inventario
    with open(SERVICE_INVENTORY_PATH) as f:
        inventory = yaml.safe_load(f)

    service = inventory.get("services", {}).get(service_name)
    if not service:
        return {
            "service_name": service_name,
            "found": False,
            "warning": "Servicio no encontrado en inventario"
        }

    return {
        "service_name": service_name,
        "found": True,
        "internet_facing": service.get("internet_facing", False),
        "requires_auth": service.get("requires_auth", True),
        "waf_protected": service.get("waf_protected", False),
        "data_classification": service.get("data_classification", "internal"),
        "criticality": service.get("criticality", "medium"),
        "owner_team": service.get("owner_team", "unknown"),
        "compliance_scope": service.get("compliance_scope", []),
    }
