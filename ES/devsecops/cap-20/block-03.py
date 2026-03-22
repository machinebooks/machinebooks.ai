# Extraído de: LibroDevSecOps/cap-20-respuesta-incidentes.md
import json
import time
import hashlib
import hmac

# Registro de todas las acciones para auditoría
action_log: list[dict] = []

def execute_containment(action: dict, incident_id: str) -> dict:
    """Ejecuta una acción de contención tras aprobación humana."""

    # Clasificar la acción por nivel de riesgo
    destructive_actions = {"isolate_container", "revoke_credentials",
                          "block_ip_range", "scale_down_service"}

    if action["type"] in destructive_actions:
        # Solicitar aprobación humana vía Slack
        approval = send_slack_approval_request(
            channel="#incident-response",
            message=(
                f":rotating_light: *Acción de contención propuesta*\n"
                f"Incidente: `{incident_id}`\n"
                f"Acción: {action['description']}\n"
                f"Impacto: {action['impact']}\n"
                f"Justificación: {action['rationale']}\n\n"
                f"Responde :white_check_mark: para aprobar "
                f"o :x: para rechazar."
            ),
            timeout_seconds=300  # 5 minutos para responder
        )

        if not approval.get("approved"):
            log_action(incident_id, action, "rejected", approval.get("reason"))
            return {"status": "rejected", "reason": approval.get("reason")}

    # Ejecutar la acción aprobada (o no destructiva)
    result = _dispatch_action(action)

    # Registrar para auditoría y post-mortem
    log_action(incident_id, action, "executed", json.dumps(result))

    return {"status": "executed", "result": result}

def log_action(incident_id: str, action: dict, status: str, detail: str):
    """Registra cada acción para trazabilidad completa."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "incident_id": incident_id,
        "action_type": action["type"],
        "description": action["description"],
        "status": status,
        "detail": detail,
        "operator": action.get("approved_by", "system")
    }
    action_log.append(entry)
