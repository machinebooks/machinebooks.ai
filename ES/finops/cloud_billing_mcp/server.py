# Extraído de: LibroFinOps/cap-12-agente-coste-cloud.md
# cloud_billing_mcp/server.py
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.types as types
import boto3
from datetime import datetime, timedelta
from azure.identity import DefaultAzureCredential
from azure.mgmt.costmanagement import CostManagementClient

app = Server("cloud-billing-mcp")

# Clientes cloud (credenciales desde variables de entorno)
aws_ce_client = boto3.client('ce', region_name='us-east-1')
azure_credential = DefaultAzureCredential()

@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """El agente descubre aquí qué herramientas tiene disponibles."""
    return [
        types.Tool(
            name="get_cloud_costs",
            description="Obtiene costes cloud para un periodo y proveedor dados",
            inputSchema={
                "type": "object",
                "properties": {
                    "provider": {"type": "string", "enum": ["aws", "azure", "all"]},
                    "start_date": {"type": "string", "description": "YYYY-MM-DD"},
                    "end_date": {"type": "string", "description": "YYYY-MM-DD"},
                    "granularity": {"type": "string", "enum": ["DAILY", "MONTHLY"]}
                },
                "required": ["provider", "start_date", "end_date"]
            }
        ),
        types.Tool(
            name="get_top_services",
            description="Lista los servicios con mayor gasto en el periodo dado",
            inputSchema={
                "type": "object",
                "properties": {
                    "provider": {"type": "string", "enum": ["aws", "azure"]},
                    "start_date": {"type": "string"},
                    "end_date": {"type": "string"},
                    "top_n": {"type": "integer", "default": 10}
                },
                "required": ["provider", "start_date", "end_date"]
            }
        ),
        types.Tool(
            name="compare_periods",
            description="Compara el gasto entre dos periodos para detectar variaciones",
            inputSchema={
                "type": "object",
                "properties": {
                    "provider": {"type": "string", "enum": ["aws", "azure", "all"]},
                    "current_start": {"type": "string"},
                    "current_end": {"type": "string"},
                    "previous_start": {"type": "string"},
                    "previous_end": {"type": "string"}
                },
                "required": ["provider", "current_start", "current_end",
                             "previous_start", "previous_end"]
            }
        )
    ]
