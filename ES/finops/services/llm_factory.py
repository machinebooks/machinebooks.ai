# Extraído de: LibroFinOps/cap-10-selfhosted-vs-api.md
# services/llm_factory.py
import anthropic
from enum import Enum
from dataclasses import dataclass
from typing import Optional
import httpx
import logging

logger = logging.getLogger(__name__)

class LLMProvider(str, Enum):
    """Proveedores de LLM disponibles en la Plataforma."""
    LOCAL_OLLAMA   = "local_ollama"    # Ollama local, coste en tokens: $0
    LOCAL_VLLM     = "local_vllm"      # vLLM local, alto throughput
    ANTHROPIC_API  = "anthropic_api"   # API de Anthropic, coste variable

@dataclass
class LLMRequest:
    """Petición normalizada, independiente del proveedor."""
    system:     str
    user:       str
    max_tokens: int = 1024
    task_tier:  str = "balanced"   # fast | balanced | powerful

@dataclass
class LLMResponse:
    """Respuesta normalizada, independiente del proveedor."""
    content:      str
    provider:     LLMProvider
    model:        str
    input_tokens: int
    output_tokens: int
    cost_usd:     float

# Mapa de tier a modelo local disponible en Ollama
LOCAL_MODEL_MAP = {
    "fast":     "qwen2.5:7b",      # extracciones y clasificaciones
    "balanced": "mistral-nemo",    # generación guiada
    "powerful": None,              # sin modelo local para nivel powerful
}

# Mapa de tier a modelo Anthropic (fallback o principal)
ANTHROPIC_MODEL_MAP = {
    "fast":     "claude-haiku-4-5",
    "balanced": "claude-sonnet-4-6",
    "powerful": "claude-opus-4-6",
}

class LLMFactory:
    """
    Fábrica de llamadas LLM con cadena de fallback local → API.
    Selecciona el proveedor según el tier de la tarea y la disponibilidad.
    """

    # Proveedores a intentar en orden (primero el local si está disponible)
    FALLBACK_CHAIN = [
        LLMProvider.LOCAL_OLLAMA,
        LLMProvider.ANTHROPIC_API,
    ]

    def __init__(self, ollama_base_url: str = "http://localhost:11434"):
        self.anthropic_client = anthropic.Anthropic()
        self.ollama_url = ollama_base_url

    def _is_local_available(self, tier: str) -> bool:
        """Comprueba si hay modelo local disponible para este tier."""
        if LOCAL_MODEL_MAP.get(tier) is None:
            return False  # no hay modelo local para nivel powerful

        try:
            # Ping al servidor Ollama con timeout corto
            resp = httpx.get(f"{self.ollama_url}/api/tags", timeout=1.0)
            return resp.status_code == 200
        except (httpx.ConnectError, httpx.TimeoutException):
            return False

    def _call_ollama(self, request: LLMRequest) -> LLMResponse:
        """Llama al modelo local vía API de Ollama."""
        model = LOCAL_MODEL_MAP[request.task_tier]

        resp = httpx.post(
            f"{self.ollama_url}/api/chat",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": request.system},
                    {"role": "user",   "content": request.user},
                ],
                "stream": False,
                "options": {"num_predict": request.max_tokens},
            },
            timeout=60.0,
        )
        resp.raise_for_status()
        data = resp.json()

        return LLMResponse(
            content=      data["message"]["content"],
            provider=     LLMProvider.LOCAL_OLLAMA,
            model=        model,
            input_tokens= data.get("prompt_eval_count", 0),
            output_tokens=data.get("eval_count", 0),
            cost_usd=     0.0,  # modelo local: sin coste de tokens
        )

    def _call_anthropic(self, request: LLMRequest) -> LLMResponse:
        """Llama a la API de Anthropic con el modelo correspondiente al tier."""
        model = ANTHROPIC_MODEL_MAP[request.task_tier]

        msg = self.anthropic_client.messages.create(
            model=     model,
            max_tokens=request.max_tokens,
            system=    request.system,
            messages=  [{"role": "user", "content": request.user}],
        )

        input_t  = msg.usage.input_tokens
        output_t = msg.usage.output_tokens
        cost     = self._calculate_cost(model, input_t, output_t)

        return LLMResponse(
            content=      msg.content[0].text,
            provider=     LLMProvider.ANTHROPIC_API,
            model=        model,
            input_tokens= input_t,
            output_tokens=output_t,
            cost_usd=     cost,
        )

    def complete(self, request: LLMRequest) -> LLMResponse:
        """
        Ejecuta la llamada LLM con la cadena de fallback configurada.
        Intenta el local primero; si no está disponible, usa la API.
        """
        for provider in self.FALLBACK_CHAIN:
            try:
                if provider == LLMProvider.LOCAL_OLLAMA:
                    if not self._is_local_available(request.task_tier):
                        continue  # saltar; probar el siguiente en la cadena
                    logger.info("Usando modelo local para tier=%s", request.task_tier)
                    return self._call_ollama(request)

                elif provider == LLMProvider.ANTHROPIC_API:
                    logger.info("Usando API Anthropic para tier=%s", request.task_tier)
                    return self._call_anthropic(request)

            except Exception as exc:
                logger.warning("Proveedor %s falló: %s; probando siguiente", provider, exc)
                continue

        raise RuntimeError("Todos los proveedores LLM fallaron")

    @staticmethod
    def _calculate_cost(model: str, input_t: int, output_t: int) -> float:
        """Calcula el coste en USD de una llamada a la API de Anthropic."""
        prices = {
            "claude-haiku-4-5":  (0.80, 4.00),
            "claude-sonnet-4-6": (3.00, 15.00),
            "claude-opus-4-6":   (15.00, 75.00),
        }
        inp_price, out_price = prices.get(model, (3.00, 15.00))
        return (input_t / 1_000_000 * inp_price
                + output_t / 1_000_000 * out_price)
