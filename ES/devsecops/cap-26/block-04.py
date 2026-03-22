# Extraído de: LibroDevSecOps/cap-26-caso-pipeline.md
import anthropic
import json
from pathlib import Path

client = anthropic.Anthropic()

# Definir tools para el agente de triaje
tools = [
    {
        "name": "get_service_context",
        "description": "Obtiene el contexto de negocio de un servicio: "
                       "exposición a internet, datos sensibles, criticidad.",
        "input_schema": {
            "type": "object",
            "properties": {
                "service_name": {
                    "type": "string",
                    "description": "Nombre del microservicio"
                }
            },
            "required": ["service_name"]
        }
    },
    {
        "name": "check_exploitability",
        "description": "Verifica si una CVE tiene exploit público conocido.",
        "input_schema": {
            "type": "object",
            "properties": {
                "cve_id": {"type": "string"}
            },
            "required": ["cve_id"]
        }
    },
    {
        "name": "get_code_path_usage",
        "description": "Verifica si la función vulnerable está en el "
                       "code path de ejecución real del servicio.",
        "input_schema": {
            "type": "object",
            "properties": {
                "package_name": {"type": "string"},
                "function_name": {"type": "string"},
                "service_name": {"type": "string"}
            },
            "required": ["package_name", "service_name"]
        }
    }
]
