# Extraído de: LibroFinOps/cap-04-instrumentacion-llm.md
# services/native_usage_tracker.py
import anthropic
import time
import uuid
import asyncio
from typing import Optional
from .llm_pricing import calculate_cost
from ..models import LLMUsageLog
from ..database import get_async_session

class NativeClientUsageTracker:
    """
    Wrapper sobre anthropic.AsyncAnthropic.
    Captura cache_creation_input_tokens y cache_read_input_tokens
    directamente desde la respuesta del SDK nativo.
    """

    def __init__(
        self,
        client: anthropic.AsyncAnthropic,
        service_name: str,
        calling_app: str,
        user_id: Optional[str] = None,
        environment: str = "prod",
    ):
        self._client = client
        self.service_name = service_name
        self.calling_app = calling_app
        self.user_id = user_id
        self.environment = environment

    async def create_message(
        self,
        model: str,
        messages: list[dict],
        max_tokens: int = 4096,
        system: Optional[str] = None,
        temperature: float = 1.0,
        **kwargs,
    ) -> anthropic.Message:
        """
        Equivalente a client.messages.create() con tracking automático.
        """
        request_id = str(uuid.uuid4())
        start_time = time.monotonic()

        params = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            **kwargs,
        }
        if system:
            params["system"] = system

        response = await self._client.messages.create(**params)
        latency_ms = int((time.monotonic() - start_time) * 1000)

        # El SDK nativo expone los campos de caching directamente
        usage = response.usage
        asyncio.create_task(
            self._persist_native_log(
                request_id=request_id,
                model=model,
                usage=usage,
                system=system,
                response=response,
                temperature=temperature,
                max_tokens=max_tokens,
                latency_ms=latency_ms,
            )
        )

        return response

    async def _persist_native_log(
        self,
        request_id: str,
        model: str,
        usage,
        system: Optional[str],
        response: anthropic.Message,
        temperature: float,
        max_tokens: int,
        latency_ms: int,
    ) -> None:
        try:
            # El SDK nativo expone estos campos directamente en usage
            input_tokens = usage.input_tokens
            output_tokens = usage.output_tokens
            cache_creation = getattr(usage, "cache_creation_input_tokens", 0) or 0
            cache_read = getattr(usage, "cache_read_input_tokens", 0) or 0

            costs = calculate_cost(
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cache_creation_tokens=cache_creation,
                cache_read_tokens=cache_read,
            )

            response_text = ""
            if response.content:
                for block in response.content:
                    if hasattr(block, "text"):
                        response_text = block.text[:1000]
                        break

            log = LLMUsageLog(
                request_id=request_id,
                calling_app=self.calling_app,
                service_name=self.service_name,
                user_id=self.user_id,
                model=model,
                provider="anthropic",
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cache_creation_tokens=cache_creation,
                cache_read_tokens=cache_read,
                total_tokens=input_tokens + output_tokens,
                input_cost_usd=costs["input"],
                output_cost_usd=costs["output"],
                cache_cost_usd=costs["cache"],
                total_cost_usd=costs["total"],
                temperature=temperature,
                max_tokens=max_tokens,
                system_message=system[:500] if system else None,
                response_text=response_text,
                latency_ms=latency_ms,
                environment=self.environment,
            )

            async with get_async_session() as session:
                session.add(log)
                await session.commit()

        except Exception as exc:
            import logging
            logging.getLogger(__name__).warning(
                f"NativeClientUsageTracker: error en persistencia: {exc}"
            )
