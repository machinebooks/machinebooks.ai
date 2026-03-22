# Extraído de: LibroFinOps/cap-07-dashboards.md
# services/monthly_report.py
import anthropic
import json
from .dashboard import get_cfo_metrics, get_pm_metrics

async def generate_monthly_narrative():
    """
    Genera un resumen narrativo del mes para dirección.
    Usa claude-haiku-4-5 por su bajo coste ($0.80/1M tokens de entrada).
    """
    cfo_data = await get_cfo_metrics(months=3)
    pm_data = await get_pm_metrics(days=30)

    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": (
                "Genera un resumen ejecutivo de 3 párrafos "
                "sobre el gasto en IA de este mes. "
                "Datos del CFO: "
                f"{json.dumps(cfo_data, ensure_ascii=False)}. "
                "Datos por servicio: "
                f"{json.dumps(pm_data, ensure_ascii=False)}. "
                "Vocabulario de negocio, euros, sin "
                "términos técnicos. Menciona si estamos "
                "dentro del presupuesto y la tendencia."
            ),
        }],
    )
    return message.content[0].text
