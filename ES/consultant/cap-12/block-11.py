# Extraído de: LibroConsultor/cap-12-auditorias-automatizadas.md
# Ejemplo de herramientas MCP para auditoría
from claude_agent_sdk import Agent, tool

@tool
def read_policy_document(document_id: str) -> str:
    """Lee una política o procedimiento del repositorio del cliente.

    Args:
        document_id: Identificador del documento en el repositorio
    Returns:
        Contenido textual del documento
    """
    # Conexión al repositorio documental del cliente
    # (SharePoint, Confluence, repositorio Git)
    content = document_repository.get_document(document_id)
    # Sanitizar antes de procesar
    guard = ConfidentialityGuard(SECTOR_PUBLICO_CONFIG)
    return guard.sanitize_before_api(content)

@tool
def get_access_control_records(system_id: str, period: str) -> dict:
    """Obtiene registros de control de acceso de un sistema.

    Args:
        system_id: Identificador del sistema
        period: Periodo de consulta (ej: "2026-Q1")
    Returns:
        Estadísticas de acceso: usuarios activos, revisiones, anomalías
    """
    records = access_management.get_records(system_id, period)
    return {
        "active_users": len(records["users"]),
        "reviews_completed": records["quarterly_reviews"],
        "anomalies_detected": records["anomalies"],
        "last_review_date": records["last_review"]
    }

@tool
def check_security_configuration(asset_type: str, asset_id: str) -> dict:
    """Verifica la configuración de seguridad de un activo.

    Args:
        asset_type: Tipo de activo (firewall, server, database, cloud_service)
        asset_id: Identificador del activo
    Returns:
        Estado de configuración contra baseline de seguridad
    """
    config = asset_inventory.get_config(asset_type, asset_id)
    baseline = security_baselines.get(asset_type)
    deviations = compare_config_to_baseline(config, baseline)
    return {
        "asset": asset_id,
        "baseline_compliance": len(deviations) == 0,
        "deviations": deviations[:10],  # Limitar para contexto
        "total_deviations": len(deviations)
    }
