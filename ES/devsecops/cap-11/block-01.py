# Extraído de: LibroDevSecOps/cap-11-remediacion-automatica.md
"""remediation_agent.py — Agente de remediación con Claude Agent SDK."""
import anthropic
import json
from pathlib import Path

client = anthropic.Anthropic()

# Definición de herramientas del agente de remediación
tools = [
    {
        "name": "read_file",
        "description": (
            "Lee el contenido de un fichero del repositorio. "
            "Usa esta herramienta para entender el código afectado "
            "por la vulnerabilidad antes de generar un fix."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Ruta relativa al fichero"
                },
                "start_line": {
                    "type": "integer",
                    "description": "Línea inicial (opcional)"
                },
                "end_line": {
                    "type": "integer",
                    "description": "Línea final (opcional)"
                }
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "read_changelog",
        "description": (
            "Consulta el changelog de una dependencia para "
            "identificar breaking changes entre dos versiones."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "package_name": {"type": "string"},
                "current_version": {"type": "string"},
                "target_version": {"type": "string"}
            },
            "required": [
                "package_name",
                "current_version",
                "target_version"
            ]
        }
    },
    {
        "name": "create_branch",
        "description": (
            "Crea una rama nueva en el repositorio para "
            "aplicar el fix. Nunca modifica main directamente."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "branch_name": {"type": "string"},
                "base_branch": {
                    "type": "string",
                    "default": "main"
                }
            },
            "required": ["branch_name"]
        }
    },
    {
        "name": "apply_fix",
        "description": (
            "Aplica cambios a un fichero en la rama de fix. "
            "Recibe el contenido nuevo del fichero completo."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string"},
                "new_content": {"type": "string"},
                "commit_message": {"type": "string"}
            },
            "required": [
                "file_path", "new_content", "commit_message"
            ]
        }
    },
    {
        "name": "create_pull_request",
        "description": (
            "Crea un pull request en GitHub con el fix "
            "aplicado, la explicación y las etiquetas."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "body": {"type": "string"},
                "branch": {"type": "string"},
                "labels": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "reviewers": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["title", "body", "branch"]
        }
    },
    {
        "name": "check_exclusion_policy",
        "description": (
            "Verifica si el hallazgo está excluido de "
            "remediación automática por políticas OPA."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "finding_id": {"type": "string"},
                "file_path": {"type": "string"},
                "fix_category": {"type": "string"}
            },
            "required": [
                "finding_id", "file_path", "fix_category"
            ]
        }
    }
]
