# Extracted from: LibroAISafety/ch-22-secure-architecture.md
async def process_request(user_input: str, session: Session) -> Response:
    """Complete flow through the 6 security layers."""

    # Layer 1: Input validation
    validation = validate_input(user_input)
    if validation.level == ThreatLevel.BLOCKED:
        metrics.injection_blocked.inc()
        return Response(text="I cannot process that request.", blocked=True)

    # Layer 2: Model inference with alignment
    model_response = await call_model(
        input=validation.sanitized_input,
        system_prompt=session.system_prompt,
        context=session.conversation_history,
    )

    # Layer 3: Validate tool calls
    if model_response.tool_calls:
        for call in model_response.tool_calls:
            if not validate_tool_call(
                call.name, call.action, call.params,
                session.permissions, session.call_counts,
            ):
                metrics.tool_blocked.inc()
                model_response.tool_calls.remove(call)
                # Re-generate response without the blocked tool
                model_response = await call_model(
                    input=validation.sanitized_input,
                    system_prompt=session.system_prompt,
                    context=session.conversation_history,
                    blocked_tools=[call.name],
                )

    # Layer 4: Output filtering
    filtered_text, pii_detections = filter_output(model_response.text)
    if pii_detections:
        metrics.pii_detected.inc(len(pii_detections))

    # Layer 5: Audit (asynchronous, does not block the response)
    asyncio.create_task(audit_log.record(
        session_id=session.id,
        input=user_input,
        sanitized_input=validation.sanitized_input,
        model_output=model_response.text,
        filtered_output=filtered_text,
        pii_detections=pii_detections,
        tool_calls=model_response.tool_calls,
    ))

    # Layer 6: Prometheus alerts operate on metrics
    # recorded in layers 1-5 -- no code needed here

    return Response(text=filtered_text, blocked=False)
