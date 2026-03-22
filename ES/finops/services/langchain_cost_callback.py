# Extraído de: LibroFinOps/cap-04-instrumentacion-llm.md
# services/langchain_cost_callback.py
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import LLMResult
import asyncio

class CostTrackingCallbackHandler(BaseCallbackHandler):
    """
    Callback de LangChain que registra el coste de cada LLM
    dentro de una cadena o agente, incluyendo sub-cadenas.
    """

    def __init__(self, service_name: str, user_id: str | None = None):
        self.service_name = service_name
        self.user_id = user_id
        self._call_start_times: dict[str, float] = {}

    def on_llm_start(self, serialized: dict, prompts: list, run_id, **kwargs):
        import time
        self._call_start_times[str(run_id)] = time.monotonic()

    def on_llm_end(self, response: LLMResult, run_id, **kwargs):
        import time
        start = self._call_start_times.pop(str(run_id), time.monotonic())
        latency_ms = int((time.monotonic() - start) * 1000)

        # Extraer uso de la respuesta
        for generation_list in response.generations:
            for generation in generation_list:
                usage = getattr(generation.message, "usage_metadata", {}) or {}
                if usage:
                    input_tokens = usage.get("input_tokens", 0)
                    output_tokens = usage.get("output_tokens", 0)
                    model = response.llm_output.get("model_name", "unknown")
                    costs = calculate_cost(
                        model=model,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                    )
                    # Fire-and-forget en el loop asyncio del hilo actual
                    try:
                        loop = asyncio.get_event_loop()
                        loop.create_task(
                            persist_log_async(
                                service_name=self.service_name,
                                user_id=self.user_id,
                                model=model,
                                input_tokens=input_tokens,
                                output_tokens=output_tokens,
                                costs=costs,
                                latency_ms=latency_ms,
                            )
                        )
                    except RuntimeError:
                        pass  # No hay event loop activo: se ignora sin bloquear
