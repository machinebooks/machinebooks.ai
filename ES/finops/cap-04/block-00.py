# Extraído de: LibroFinOps/cap-04-instrumentacion-llm.md
async def astream_with_tracking(
    self,
    messages: list,
    **kwargs,
) -> AsyncIterator:
    """
    Streaming con tracking al final del stream.
    Los tokens de uso solo están disponibles en el último evento.
    """
    request_id = str(uuid.uuid4())
    start_time = time.monotonic()
    input_tokens = output_tokens = 0

    async with self._llm.astream_events(messages, version="v2", **kwargs) as stream:
        async for event in stream:
            # Capturar tokens del evento final de uso
            if event["event"] == "on_llm_end":
                usage = event.get("data", {}).get("output", {}).get("usage_metadata", {})
                input_tokens = usage.get("input_tokens", 0)
                output_tokens = usage.get("output_tokens", 0)
            yield event

    # Registrar uso al completar el stream
    latency_ms = int((time.monotonic() - start_time) * 1000)
    costs = calculate_cost(
        model=self._llm.model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )
    asyncio.create_task(
        self._persist_minimal_log(
            request_id=request_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            costs=costs,
            latency_ms=latency_ms,
        )
    )
