# Extraído de: LibroFinOps/cap-04-instrumentacion-llm.md
# services/llm_usage_tracker.py
import asyncio
import time
import uuid
from typing import Any, AsyncIterator, Optional
from langchain_core.messages import BaseMessage
from langchain_anthropic import ChatAnthropic
from .llm_pricing import calculate_cost  # tabla de precios por modelo
from ..models import LLMUsageLog
from ..database import get_async_session

class LLMUsageTracker:
    """
    Wrapper transparente sobre cualquier BaseChatModel de LangChain.
    Registra cada llamada sin que el código de negocio lo sepa.
    El registro ocurre en background: no bloquea la respuesta.
    """

    def __init__(
        self,
        base_llm: ChatAnthropic,
        service_name: str,
        calling_app: str,
        user_id: Optional[str] = None,
        prompt_key: Optional[str] = None,
        rag_collection: Optional[str] = None,
        environment: str = "prod",
    ):
        self._llm = base_llm
        self.service_name = service_name
        self.calling_app = calling_app
        self.user_id = user_id
        self.prompt_key = prompt_key
        self.rag_collection = rag_collection
        self.environment = environment

    async def ainvoke(
        self,
        messages: list[BaseMessage],
        rag_query: Optional[str] = None,
        **kwargs,
    ) -> BaseMessage:
        """
        Llamada async al LLM con tracking automático de coste.
        El registro ocurre en background mediante create_task().
        """
        request_id = str(uuid.uuid4())
        start_time = time.monotonic()
        error_msg = None
        response = None

        try:
            response = await self._llm.ainvoke(messages, **kwargs)
        except Exception as exc:
            error_msg = str(exc)
            raise
        finally:
            latency_ms = int((time.monotonic() - start_time) * 1000)
            # Fire-and-forget: el tracking no bloquea la respuesta
            asyncio.create_task(
                self._persist_log(
                    request_id=request_id,
                    messages=messages,
                    response=response,
                    latency_ms=latency_ms,
                    rag_query=rag_query,
                    error_msg=error_msg,
                )
            )

        return response

    async def _persist_log(
        self,
        request_id: str,
        messages: list[BaseMessage],
        response: Optional[BaseMessage],
        latency_ms: int,
        rag_query: Optional[str],
        error_msg: Optional[str],
    ) -> None:
        """
        Construye y persiste el LLMUsageLog.
        Si falla, registra el error en logs de aplicación
        pero no propaga la excepción al flujo principal.
        """
        try:
            usage = getattr(response, "usage_metadata", {}) or {}
            input_tokens = usage.get("input_tokens", 0)
            output_tokens = usage.get("output_tokens", 0)
            cache_creation = usage.get("input_token_details", {}).get(
                "cache_creation", 0
            )
            cache_read = usage.get("input_token_details", {}).get("cache_read", 0)

            model = self._llm.model
            costs = calculate_cost(
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cache_creation_tokens=cache_creation,
                cache_read_tokens=cache_read,
            )

            # Extraer el mensaje de sistema si existe
            system_msg = next(
                (m.content[:500] for m in messages if hasattr(m, "type") and m.type == "system"),
                None,
            )
            response_text = (
                response.content[:1000] if response and response.content else None
            )

            log = LLMUsageLog(
                request_id=request_id,
                calling_app=self.calling_app,
                service_name=self.service_name,
                user_id=self.user_id,
                prompt_key=self.prompt_key,
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
                rag_collection=self.rag_collection,
                rag_query=rag_query,
                latency_ms=latency_ms,
                system_message=system_msg,
                response_text=response_text,
                error_message=error_msg,
                environment=self.environment,
            )

            async with get_async_session() as session:
                session.add(log)
                await session.commit()

        except Exception as exc:
            # El tracking nunca bloquea la funcionalidad
            import logging
            logging.getLogger(__name__).warning(
                f"LLMUsageTracker: falló el registro del log: {exc}"
            )
