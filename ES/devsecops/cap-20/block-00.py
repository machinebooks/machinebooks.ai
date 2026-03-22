# Extraído de: LibroDevSecOps/cap-20-respuesta-incidentes.md
import anthropic
from datetime import datetime, timezone
from typing import Any

client = anthropic.Anthropic()

# Definición de tools para el agente de respuesta a incidentes
incident_tools = [
    {
        "name": "correlate_alerts",
        "description": (
            "Correlaciona alertas de seguridad de múltiples fuentes "
            "(Falco, pipeline, WAF) en un período de tiempo dado. "
            "Retorna alertas agrupadas por vector de ataque probable."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "time_window_minutes": {
                    "type": "integer",
                    "description": "Ventana de tiempo en minutos para correlacionar"
                },
                "sources": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Fuentes de alertas: falco, pipeline, waf, ids"
                }
            },
            "required": ["time_window_minutes", "sources"]
        }
    },
    {
        "name": "query_sbom",
        "description": (
            "Consulta el SBOM del servicio afectado para identificar "
            "dependencias vulnerables relacionadas con el incidente."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "service_name": {"type": "string"},
                "cve_id": {"type": "string", "description": "CVE específica a buscar, opcional"}
            },
            "required": ["service_name"]
        }
    },
    {
        "name": "isolate_container",
        "description": (
            "Aísla un contenedor de la red, aplicando network policy "
            "que bloquea todo el tráfico excepto el de monitorización. "
            "REQUIERE aprobación humana."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "container_id": {"type": "string"},
                "namespace": {"type": "string"},
                "reason": {"type": "string"}
            },
            "required": ["container_id", "namespace", "reason"]
        }
    },
    {
        "name": "request_human_approval",
        "description": (
            "Envía una solicitud de aprobación al canal de incidentes "
            "con el detalle de la acción propuesta. Bloquea hasta "
            "recibir aprobación o rechazo."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "action_summary": {"type": "string"},
                "impact_description": {"type": "string"},
                "urgency": {
                    "type": "string",
                    "enum": ["critical", "high", "medium"]
                }
            },
            "required": ["action_summary", "impact_description", "urgency"]
        }
    },
    {
        "name": "generate_postmortem",
        "description": (
            "Genera un borrador de post-mortem estructurado a partir "
            "del timeline del incidente, acciones tomadas y métricas."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "incident_id": {"type": "string"},
                "include_metrics": {"type": "boolean", "default": True}
            },
            "required": ["incident_id"]
        }
    }
]
