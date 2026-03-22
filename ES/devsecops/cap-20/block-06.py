# Extraído de: LibroDevSecOps/cap-20-respuesta-incidentes.md
import re

# Validación de entradas antes de que lleguen al agente
def sanitize_alert_data(alert: dict) -> dict:
    """Elimina contenido potencialmente malicioso de las alertas."""
    sanitized = {}

    # Solo permitir campos conocidos del esquema de alertas
    allowed_fields = {
        "source", "timestamp", "severity", "description",
        "container_id", "service_name", "cve_id", "rule_name",
        "namespace", "process_name", "network_destination"
    }

    for key, value in alert.items():
        if key not in allowed_fields:
            continue
        if isinstance(value, str):
            # Eliminar patrones sospechosos de injection
            cleaned = re.sub(
                r'(ignore previous|system prompt|you are now|'
                r'forget your instructions|new role)',
                '[FILTERED]', value, flags=re.IGNORECASE
            )
            # Limitar longitud para evitar prompt stuffing
            sanitized[key] = cleaned[:500]
        else:
            sanitized[key] = value

    return sanitized

# Presupuesto de acciones por incidente
MAX_CONTAINMENT_ACTIONS = 10
MAX_API_CALLS_PER_INCIDENT = 50

def check_action_budget(incident_id: str) -> bool:
    """Verifica que el agente no exceda el presupuesto de acciones."""
    actions_taken = sum(
        1 for a in action_log
        if a["incident_id"] == incident_id and a["status"] == "executed"
    )
    if actions_taken >= MAX_CONTAINMENT_ACTIONS:
        notify_team(
            channel="#incident-response",
            summary=f"ALERTA: Incidente {incident_id} alcanzó el límite "
                    f"de {MAX_CONTAINMENT_ACTIONS} acciones de contención. "
                    f"Se requiere intervención manual."
        )
        return False
    return True
