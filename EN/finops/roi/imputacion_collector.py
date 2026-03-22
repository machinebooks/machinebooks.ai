# Source: The FinOps Engineer and the Machine -- Chapter 23
# Pattern: Automated cost imputation collector

# services/imputacion_collector.py
# Collects monthly allocations conversationally using Claude.
# Integrates with the team's messaging system (Slack, Teams, etc.).

import anthropic
import json
from datetime import date
from decimal import Decimal

client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are a FinOps assistant collecting the monthly time
distribution from a team member. You must:

1. Ask which projects they have dedicated time to this month.
2. Request an approximate percentage for each project (rounded to 10%).
3. Verify the sum does not exceed 100%.
4. If dedication is missing to reach 100%, ask if there are forgotten projects
   or if the remaining time is administrative/internal meetings.
5. Confirm the final summary before recording.

Always reply in English. Be brief and direct. Do not use HR jargon.
Valid projects are: AI_PLATFORM, GRC_PLATFORM, EXTERNAL_CLIENT,
AI_PLATFORM:EXPLORATION, INTERNAL_TRAINING, INTERNAL_ADMIN."""


def iniciar_recogida(persona_codigo: str, mes: date) -> str:
    """Starts the allocation collection conversation."""
    initial_message = (
        f"I need to record your time allocation for {mes.strftime('%B %Y')}. "
        f"Which projects have you dedicated your time to this month?"
    )
    response = client.messages.create(
        model="claude-haiku-4-5",  # Simple conversation, minimal cost (~EUR0.001)
        max_tokens=256,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": initial_message}],
    )
    return response.content[0].text


def validar_imputacion(dedicaciones: dict[str, float]) -> list[str]:
    """Validates that the allocations are coherent."""
    errores = []
    total = sum(dedicaciones.values())
    if total > 1.0:
        errores.append(f"The sum of allocations ({total:.0%}) exceeds 100%.")
    if total < 0.8:
        errores.append(
            f"You have only allocated {total:.0%}. Is there a missing project?"
        )
    for proyecto, pct in dedicaciones.items():
        if pct < 0.1:
            errores.append(f"{proyecto}: dedication below 10%, is it significant?")
    return errores
