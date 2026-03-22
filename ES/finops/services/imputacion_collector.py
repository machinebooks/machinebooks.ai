# Extraído de: LibroFinOps/cap-23-coste-equipo.md
# services/imputacion_collector.py
# Recoge imputaciones mensuales de forma conversacional usando Claude.
# Se integra con el sistema de mensajería del equipo (Slack, Teams, etc.).

import anthropic
import json
from datetime import date
from decimal import Decimal

client = anthropic.Anthropic()

SYSTEM_PROMPT = """Eres un asistente de FinOps que recoge la distribución mensual
de dedicación de un miembro del equipo. Debes:

1. Preguntar a qué proyectos ha dedicado tiempo este mes.
2. Pedir un porcentaje aproximado para cada proyecto (redondeado al 10%).
3. Verificar que la suma no supere el 100%.
4. Si falta dedicación para llegar al 100%, preguntar si hay proyectos olvidados
   o si el tiempo restante es administrativo/reuniones internas.
5. Confirmar el resumen final antes de registrar.

Responde siempre en español. Sé breve y directo. No uses jerga de RRHH.
Los proyectos válidos son: PLATAFORMA_IA, PLATAFORMA_GRC, CLIENTE_EXT,
PLATAFORMA_IA:EXPLORACION, INTERNO_FORMACION, INTERNO_ADMIN."""


def iniciar_recogida(persona_codigo: str, mes: date) -> str:
    """Inicia la conversación de recogida de imputación."""
    mensaje_inicial = (
        f"Necesito registrar tu dedicación de {mes.strftime('%B %Y')}. "
        f"¿A qué proyectos has dedicado tu tiempo este mes?"
    )
    response = client.messages.create(
        model="claude-haiku-4-5",  # Conversación simple, coste mínimo (~€0.001)
        max_tokens=256,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": mensaje_inicial}],
    )
    return response.content[0].text


def validar_imputacion(dedicaciones: dict[str, float]) -> list[str]:
    """Valida que las dedicaciones sean coherentes."""
    errores = []
    total = sum(dedicaciones.values())
    if total > 1.0:
        errores.append(f"La suma de dedicaciones ({total:.0%}) supera el 100%.")
    if total < 0.8:
        errores.append(
            f"Solo has imputado el {total:.0%}. ¿Falta algún proyecto?"
        )
    for proyecto, pct in dedicaciones.items():
        if pct < 0.1:
            errores.append(f"{proyecto}: dedicación inferior al 10%, ¿es significativa?")
    return errores
