# Extraído de: LibroFinOps/apendice-b-apis-coste-cloud.md
import anthropic
import boto3
import json
from datetime import datetime, timedelta

client = anthropic.Anthropic()

# Definir tools que el agente puede invocar
tools = [
    {
        "name": "get_aws_costs",
        "description": "Consulta costes AWS por servicio para un periodo dado",
        "input_schema": {
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "Número de días hacia atrás"
                }
            },
            "required": ["days"]
        }
    }
]

def handle_tool_call(tool_name, tool_input):
    """Ejecuta la tool solicitada por el agente."""
    if tool_name == "get_aws_costs":
        ce = boto3.client("ce", region_name="us-east-1")
        end = datetime.now().strftime("%Y-%m-%d")
        start = (datetime.now() - timedelta(days=tool_input["days"])).strftime("%Y-%m-%d")
        response = ce.get_cost_and_usage(
            TimePeriod={"Start": start, "End": end},
            Granularity="DAILY",
            Metrics=["UnblendedCost"],
            GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}]
        )
        return json.dumps(response, default=str)

# El agente razona sobre los datos de coste
message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=4096,
    tools=tools,
    messages=[{
        "role": "user",
        "content": "Analiza los costes AWS de los últimos 7 días e identifica anomalías"
    }]
)
