# Extraído de: LibroFinOps/cap-05-tagging-cloud.md
# agents/tag_audit_agent.py
import anthropic
import boto3
import json
from typing import Optional
from datetime import datetime, timezone

client = anthropic.Anthropic()

# Definición de herramientas que el agente puede invocar
TAG_AUDIT_TOOLS = [
    {
        "name": "list_untagged_ec2",
        "description": (
            "Lista instancias EC2 sin todas las etiquetas obligatorias. "
            "Devuelve id, nombre, tipo, estado, VPC, fecha de creación y etiquetas actuales."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "region": {"type": "string", "description": "Región AWS (ej. eu-west-1)"},
                "required_tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Lista de etiquetas obligatorias",
                },
            },
            "required": ["region", "required_tags"],
        },
    },
    {
        "name": "list_untagged_rds",
        "description": "Lista instancias RDS sin etiquetas obligatorias.",
        "input_schema": {
            "type": "object",
            "properties": {
                "region": {"type": "string"},
                "required_tags": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["region", "required_tags"],
        },
    },
    {
        "name": "propose_tag_correction",
        "description": (
            "Registra una propuesta de corrección de etiquetas para un recurso. "
            "No ejecuta la corrección: solo la registra para revisión humana."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "resource_id": {"type": "string"},
                "resource_type": {"type": "string"},
                "proposed_tags": {
                    "type": "object",
                    "description": "Dict con los tags propuestos y sus valores",
                },
                "reasoning": {
                    "type": "string",
                    "description": "Justificación de los valores propuestos",
                },
                "confidence": {
                    "type": "string",
                    "enum": ["high", "medium", "low"],
                    "description": "Confianza en la propuesta basada en el contexto disponible",
                },
            },
            "required": ["resource_id", "resource_type", "proposed_tags", "reasoning", "confidence"],
        },
    },
]
