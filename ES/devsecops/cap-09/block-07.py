# Extraído de: LibroDevSecOps/cap-09-agente-triaje.md
from claude_agent_sdk import tool

@tool
def get_business_context(service_name: str) -> dict:
    """Recupera metadatos de negocio: SLAs, regulaciones
    aplicables, impacto de una brecha en el servicio."""
    # En producción, esto consultaría un CMDB o service catalog
    # Aquí usamos el mismo inventario enriquecido
    exposure = check_service_exposure(service_name)
    if not exposure.get("found"):
        return {"service_name": service_name, "context_available": False}

    # Calcular impacto potencial según clasificación de datos
    data_class = exposure.get("data_classification", "internal")
    impact_map = {
        "public": {"breach_impact": "low", "regulatory_risk": "none"},
        "internal": {"breach_impact": "medium", "regulatory_risk": "low"},
        "confidential": {"breach_impact": "high", "regulatory_risk": "medium"},
        "restricted": {"breach_impact": "critical", "regulatory_risk": "high"},
    }

    impact = impact_map.get(data_class, impact_map["internal"])
    compliance = exposure.get("compliance_scope", [])

    return {
        "service_name": service_name,
        "context_available": True,
        "criticality": exposure.get("criticality"),
        "owner_team": exposure.get("owner_team"),
        "breach_impact": impact["breach_impact"],
        "regulatory_risk": impact["regulatory_risk"],
        "compliance_frameworks": compliance,
        "internet_facing": exposure.get("internet_facing"),
    }
