# Extraído de: LibroFinOps/cap-22-multiproveedor.md
# agents/cloud_cost_comparator.py
import anthropic
import boto3
from datetime import datetime, timedelta


def compare_cloud_providers(period_days: int = 30) -> dict:
    """
    Compara costes de infraestructura entre proveedores cloud.
    Genera un informe normalizado para negociación enterprise.
    """
    client = anthropic.Anthropic()
    end = datetime.utcnow().strftime("%Y-%m-%d")
    start = (datetime.utcnow() - timedelta(days=period_days)).strftime("%Y-%m-%d")

    # Obtener costes reales de AWS (si hay workloads activos)
    ce = boto3.client("ce")
    aws_response = ce.get_cost_and_usage(
        TimePeriod={"Start": start, "End": end},
        Granularity="MONTHLY",
        Metrics=["UnblendedCost"],
        GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
    )

    # Pedir a Claude que analice y compare con precios públicos de Azure
    analysis = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system="Eres un analista FinOps. Compara costes cloud entre proveedores.",
        messages=[{
            "role": "user",
            "content": f"""Datos de coste AWS últimos {period_days} días:
{aws_response['ResultsByTime']}

Compara estos costes con los precios públicos equivalentes en Azure.
Para cada servicio, indica: coste AWS actual, coste estimado Azure,
diferencia porcentual, y recomendación de negociación.""",
        }],
    )
    return {
        "period": f"{start} a {end}",
        "aws_data": aws_response["ResultsByTime"],
        "analysis": analysis.content[0].text,
        "analysis_cost_usd": (
            analysis.usage.input_tokens * 3 / 1_000_000
            + analysis.usage.output_tokens * 15 / 1_000_000
        ),
    }
