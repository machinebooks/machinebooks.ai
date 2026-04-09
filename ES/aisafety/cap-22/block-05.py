# Extraido de: LibroAISafety/cap-22-arquitectura-segura.md
async def process_request(user_input: str, session: Session) -> Response:
    """Flujo completo a través de las 6 capas de seguridad."""

    # Capa 1: Validación de entrada
    validation = validate_input(user_input)
    if validation.level == ThreatLevel.BLOCKED:
        metrics.injection_blocked.inc()
        return Response(text="No puedo procesar esa petición.", blocked=True)

    # Capa 2: Model inference con alignment
    model_response = await call_model(
        input=validation.sanitized_input,
        system_prompt=session.system_prompt,
        context=session.conversation_history,
    )

    # Capa 3: Validar llamadas a herramientas
    if model_response.tool_calls:
        for call in model_response.tool_calls:
            if not validate_tool_call(
                call.name, call.action, call.params,
                session.permissions, session.call_counts,
            ):
                metrics.tool_blocked.inc()
                model_response.tool_calls.remove(call)
                # Re-generar respuesta sin la herramienta bloqueada
                model_response = await call_model(
                    input=validation.sanitized_input,
                    system_prompt=session.system_prompt,
                    context=session.conversation_history,
                    blocked_tools=[call.name],
                )

    # Capa 4: Filtrado de salida
    filtered_text, pii_detections = filter_output(model_response.text)
    if pii_detections:
        metrics.pii_detected.inc(len(pii_detections))

    # Capa 5: Auditoría (asíncrona, no bloquea la respuesta)
    asyncio.create_task(audit_log.record(
        session_id=session.id,
        input=user_input,
        sanitized_input=validation.sanitized_input,
        model_output=model_response.text,
        filtered_output=filtered_text,
        pii_detections=pii_detections,
        tool_calls=model_response.tool_calls,
    ))

    # Capa 6: Las alertas de Prometheus operan sobre las métricas
    # registradas en las capas 1-5 — no requieren código aquí

    return Response(text=filtered_text, blocked=False)
