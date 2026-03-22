# Extraído de: LibroCyberrange/cap-16-ia-por-que.md
# Ejemplo didáctico: patrones/ia/ai_service.py
import anthropic
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Callable
import time
import logging

logger = logging.getLogger("ai_service")

class AIModel(str, Enum):
    """Modelos disponibles, ordenados por capacidad."""
    OPUS = "claude-opus-4-6"       # Razonamiento complejo, generación de escenarios
    SONNET = "claude-sonnet-4-6"   # Balance capacidad/coste, mayoría de tareas
    HAIKU = "claude-haiku-4-5"     # Velocidad, coaching en tiempo real, clasificación

@dataclass
class AIRequest:
    """Petición al servicio de IA."""
    task_type: str              # "scenario_gen", "coaching", "red_team", "evaluation"
    model: AIModel              # Modelo solicitado
    system_prompt: str          # Instrucción del sistema
    user_message: str           # Mensaje del usuario/servicio
    max_tokens: int = 4096
    temperature: float = 0.7
    correlation_id: Optional[str] = None  # Para trazabilidad

@dataclass
class AIResponse:
    """Respuesta del servicio de IA."""
    content: str
    model_used: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    cost_usd: float
    correlation_id: Optional[str] = None

class CyberRangeAIService:
    """
    Servicio centralizado de IA del Cyber Range.

    Responsabilidades:
    - Gestión del cliente Anthropic
    - Selección de modelo por tipo de tarea
    - Logging de cada petición (tokens, coste, latencia)
    - Circuit breaker ante fallos de la API
    - Cálculo de costes en tiempo real
    """

    # Precios por millón de tokens (USD, junio 2026)
    PRICING = {
        AIModel.OPUS:   {"input": 15.00, "output": 75.00},
        AIModel.SONNET: {"input": 3.00,  "output": 15.00},
        AIModel.HAIKU:  {"input": 0.25,  "output": 1.25},
    }

    # Política de modelo por tipo de tarea
    DEFAULT_MODELS = {
        "scenario_gen":    AIModel.SONNET,   # Generación: balance
        "coaching":        AIModel.HAIKU,    # Coaching: velocidad
        "red_team":        AIModel.SONNET,   # Red team: razonamiento táctico
        "blue_team":       AIModel.HAIKU,    # Blue team: respuesta rápida
        "evaluation":      AIModel.SONNET,   # Evaluación: análisis profundo
        "report":          AIModel.SONNET,   # Informes: redacción
        "classification":  AIModel.HAIKU,    # Clasificación MITRE: velocidad
    }

    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self._consecutive_errors = 0
        self._circuit_open = False
        self._total_cost_usd = 0.0

    def get_model_for_task(self, task_type: str) -> AIModel:
        """Devuelve el modelo óptimo para el tipo de tarea."""
        return self.DEFAULT_MODELS.get(task_type, AIModel.SONNET)

    def _calculate_cost(self, model: AIModel,
                        input_tokens: int,
                        output_tokens: int) -> float:
        """Calcula el coste de una petición en USD."""
        prices = self.PRICING[model]
        cost = (input_tokens * prices["input"] / 1_000_000 +
                output_tokens * prices["output"] / 1_000_000)
        return round(cost, 6)

    async def execute(self, request: AIRequest) -> AIResponse:
        """
        Ejecuta una petición de IA con logging y circuit breaker.
        """
        if self._circuit_open:
            raise AIServiceUnavailable(
                "Circuit breaker abierto: la API de IA no está disponible"
            )

        start = time.monotonic()

        try:
            response = self.client.messages.create(
                model=request.model.value,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                system=request.system_prompt,
                messages=[{
                    "role": "user",
                    "content": request.user_message
                }]
            )

            latency = (time.monotonic() - start) * 1000
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            cost = self._calculate_cost(
                request.model, input_tokens, output_tokens
            )

            # Reset circuit breaker ante éxito
            self._consecutive_errors = 0
            self._total_cost_usd += cost

            # Log de la petición
            logger.info(
                "AI request completed",
                extra={
                    "task_type": request.task_type,
                    "model": request.model.value,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "latency_ms": round(latency, 1),
                    "cost_usd": cost,
                    "correlation_id": request.correlation_id,
                }
            )

            return AIResponse(
                content=response.content[0].text,
                model_used=request.model.value,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                latency_ms=round(latency, 1),
                cost_usd=cost,
                correlation_id=request.correlation_id,
            )

        except anthropic.APIStatusError as e:
            self._consecutive_errors += 1
            if self._consecutive_errors >= 3:
                self._circuit_open = True
                logger.error("Circuit breaker OPEN: 3 errores consecutivos")
            raise

class AIServiceUnavailable(Exception):
    pass
