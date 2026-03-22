# Source: The FinOps Engineer and the Machine -- Chapter 24
# Pattern: Cost awareness notification service

# services/cost_awareness_notifier.py
# Service that sends cost notifications at the right moment.
# Not in weekly reports: at the moment something relevant happens.

import anthropic
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass
from typing import Optional


class TipoNotificacion(str, Enum):
    OPERACION_CARA = "operacion_cara"         # A single call exceeds threshold
    PATRON_INEFICIENTE = "patron_ineficiente" # A cheaper model is available
    SEMANA_RECORD = "semana_record"           # The team beats its efficiency record
    LOGRO_CHAMPION = "logro_champion"         # New monthly FinOps champion
    CLOUD_RECOMENDACION = "cloud_recomendacion"  # Cloud agent recommendation


@dataclass
class Notificacion:
    tipo: TipoNotificacion
    destinatario_codigo: str  # Anonymous user/squad code
    titulo: str
    mensaje: str
    datos: dict
    accionable: bool = True   # Does the recipient have something to do?


class CostAwarenessNotifier:
    """
    Generates contextual cost awareness notifications.
    Notifications are educational, not accusatory.
    Covers both axes: AI tokens and cloud resources.
    """

    # Threshold for notifying expensive operations (in euros)
    UMBRAL_OPERACION_CARA = 0.50  # EUR 0.50 per individual call

    def __init__(self):
        self.client = anthropic.Anthropic()

    def evaluar_llamada(
        self,
        usuario_codigo: str,
        modelo: str,
        coste_eur: Decimal,
        input_tokens: int,
        output_tokens: int,
        operacion_tipo: str,
    ) -> Optional[Notificacion]:
        """
        Evaluates whether an individual LLM call deserves notification.
        Called from LLMUsageTracker after each call.
        """
        # Was the operation expensive for its type?
        if float(coste_eur) >= self.UMBRAL_OPERACION_CARA:
            # Was there a cheaper model for this task?
            alternativa = self._sugerir_alternativa(
                modelo, operacion_tipo, input_tokens
            )

            mensaje = (
                f"The operation '{operacion_tipo}' cost EUR{coste_eur:.3f} "
                f"with {modelo}."
            )
            if alternativa:
                mensaje += (
                    f" For this type of task, {alternativa['modelo']} "
                    f"would have cost approximately EUR{alternativa['coste_est']:.3f} "
                    f"(saving of {alternativa['ahorro_pct']:.0f}%)."
                )

            return Notificacion(
                tipo=TipoNotificacion.OPERACION_CARA,
                destinatario_codigo=usuario_codigo,
                titulo="High cost operation detected",
                mensaje=mensaje,
                datos={
                    "modelo_usado": modelo,
                    "coste_eur": float(coste_eur),
                    "alternativa": alternativa,
                },
            )

        return None  # Nothing to notify

    def _sugerir_alternativa(
        self,
        modelo_usado: str,
        tipo_operacion: str,
        input_tokens: int,
    ) -> Optional[dict]:
        """
        Determines if a cheaper model exists for this task.
        Uses heuristic rules: doesn't call the API to avoid cost recursion.
        """
        # Tasks that typically don't need opus or full sonnet
        tareas_haiku = {
            "clasificacion", "extraccion_entidades", "sentiment",
            "resumen_corto", "validacion", "routing_intent"
        }

        if tipo_operacion.lower() in tareas_haiku:
            if "opus" in modelo_usado:
                return {
                    "modelo": "claude-haiku-4-5",
                    "coste_est": input_tokens * 0.0000008,  # $0.80/1M tokens
                    "ahorro_pct": 95,
                }
            elif "sonnet" in modelo_usado:
                return {
                    "modelo": "claude-haiku-4-5",
                    "coste_est": input_tokens * 0.0000008,
                    "ahorro_pct": 85,
                }

        return None  # The chosen model seems correct for the task

    def generar_mensaje_champion(
        self,
        squad: str,
        mes: str,
        logro: str,
        ahorro_eur: float,
        mejora_eficiencia_pct: float,
    ) -> str:
        """
        Generates the recognition message for the monthly FinOps Champion.
        Uses claude-haiku-4-5 because it's a short writing task.
        """
        prompt = f"""
Generate a brief recognition message (maximum 4 sentences) for the team
{squad}, which has been named FinOps Champion of the month of {mes}.

Achievement: {logro}
Savings generated: EUR{ahorro_eur:.0f}
Efficiency improvement: +{mejora_eficiencia_pct:.0f}%

The tone should be celebratory but technical. No excessive emojis.
It should include an observation about what other teams can learn from this.
Write in European Spanish.
"""
        message = self.client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=256,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
