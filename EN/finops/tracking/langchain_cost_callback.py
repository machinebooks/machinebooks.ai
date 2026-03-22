# Source: The FinOps Engineer and the Machine -- Chapter 4
# Pattern: LangChain callback handler for cost tracking

# services/langchain_cost_callback.py
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import LLMResult
import asyncio

class CostTrackingCallbackHandler(BaseCallbackHandler):
    """
    LangChain callback that records the cost of each LLM
    within a chain or agent, including sub-chains.
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

        # Extract usage from the response
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
                    # Fire-and-forget in the current thread's asyncio loop
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
                        pass  # No active event loop: ignore without blocking
