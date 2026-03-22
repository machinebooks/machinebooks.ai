# Extraído de: LibroFinOps/cap-24-cultura-finops.md
# services/cost_awareness_notifier.py
# Servicio que envía notificaciones de coste en el momento justo.
# No en informes semanales: en el momento en que ocurre algo relevante.

import anthropic
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass
from typing import Optional


class TipoNotificacion(str, Enum):
    OPERACION_CARA = "operacion_cara"         # Una sola llamada supera umbral
    PATRON_INEFICIENTE = "patron_ineficiente" # Hay un modelo más barato disponible
    SEMANA_RECORD = "semana_record"           # El equipo bate su récord de eficiencia
    LOGRO_CHAMPION = "logro_champion"         # Nuevo FinOps champion mensual
    CLOUD_RECOMENDACION = "cloud_recomendacion"  # Recomendación del agente cloud


@dataclass
class Notificacion:
    tipo: TipoNotificacion
    destinatario_codigo: str  # Código anónimo del usuario/squad
    titulo: str
    mensaje: str
    datos: dict
    accionable: bool = True   # ¿Tiene algo que hacer el destinatario?


class CostAwarenessNotifier:
    """
    Genera notificaciones contextuales de cost awareness.
    Las notificaciones son educativas, no acusatorias.
    Cubre ambos ejes: tokens de IA y recursos cloud.
    """

    # Umbral para notificar operaciones caras (en euros)
    UMBRAL_OPERACION_CARA = 0.50  # €0.50 por llamada individual

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
        Evalúa si una llamada LLM individual merece notificación.
        Se llama desde el LLMUsageTracker después de cada llamada.
        """
        # ¿La operación fue cara para su tipo?
        if float(coste_eur) >= self.UMBRAL_OPERACION_CARA:
            # ¿Había un modelo más barato para esta tarea?
            alternativa = self._sugerir_alternativa(
                modelo, operacion_tipo, input_tokens
            )

            mensaje = (
                f"La operación '{operacion_tipo}' costó €{coste_eur:.3f} "
                f"con {modelo}."
            )
            if alternativa:
                mensaje += (
                    f" Para este tipo de tarea, {alternativa['modelo']} "
                    f"habría costado aproximadamente €{alternativa['coste_est']:.3f} "
                    f"(ahorro del {alternativa['ahorro_pct']:.0f}%)."
                )

            return Notificacion(
                tipo=TipoNotificacion.OPERACION_CARA,
                destinatario_codigo=usuario_codigo,
                titulo="Operación de alto coste detectada",
                mensaje=mensaje,
                datos={
                    "modelo_usado": modelo,
                    "coste_eur": float(coste_eur),
                    "alternativa": alternativa,
                },
            )

        return None  # Nada que notificar

    def _sugerir_alternativa(
        self,
        modelo_usado: str,
        tipo_operacion: str,
        input_tokens: int,
    ) -> Optional[dict]:
        """
        Determina si existe un modelo más económico para esta tarea.
        Usa reglas heurísticas: no llama a la API para no crear recursión de costes.
        """
        # Tareas que típicamente no necesitan opus ni sonnet completo
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

        return None  # El modelo elegido parece correcto para la tarea

    def generar_mensaje_champion(
        self,
        squad: str,
        mes: str,
        logro: str,
        ahorro_eur: float,
        mejora_eficiencia_pct: float,
    ) -> str:
        """
        Genera el mensaje de reconocimiento al FinOps Champion del mes.
        Usa claude-haiku-4-5 porque es una tarea de redacción corta.
        """
        prompt = f"""
Genera un mensaje de reconocimiento breve (máximo 4 frases) para el equipo
{squad}, que ha sido nombrado FinOps Champion del mes de {mes}.

Su logro: {logro}
Ahorro generado: €{ahorro_eur:.0f}
Mejora de eficiencia: +{mejora_eficiencia_pct:.0f}%

El tono debe ser celebratorio pero técnico. Sin emojis excesivos.
Debe incluir una observación sobre qué pueden aprender otros equipos de esto.
Escribe en español de España.
"""
        message = self.client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=256,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
