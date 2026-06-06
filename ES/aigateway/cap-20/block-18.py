# Extraído de: LibroAIGateway/cap-20-clasificacion-guardrails-firewall.md
# gateway/app/services/pipeline/stages/security_output.py:35-86

async def run(ctx) -> None:
    """Escaneo post-LLM sobre la respuesta completa."""
    response = getattr(ctx, "response", None)
    if response is None or not getattr(response, "content", None):
        return

    # 1) Output filter (PII leak, system prompt leak, code vulns)
    if not skip_policy:
        try:
            output_result = OutputFilterService.scan_output(
                content=response.content,
                system_prompt=sys_for_filter,
                check_prompt_leak=check_prompt_leak,
            )
            if output_result.was_modified:
                response.content = output_result.filtered_content
        except PolicyBlocked:
            response.content = "[Respuesta bloqueada por política de seguridad.]"
            logger.warning("security_output:response_blocked device=%s", device_id)

    # 2) Leak detection (exfiltration patterns)
    try:
        leak_output = LeakDetectionService.scan_output(response.content)
        if leak_output.suspicious:
            await SecurityEventService.emit(...)
    except Exception:
        logger.warning("security_output:leak_scan_failed err=%s", exc)

    # 2b) Guardrails configurables (output)
    try:
        redacted = await guardrail_service.evaluate(
            ctx.db, text=response.content, direction="output",
            request_id=request_id, user_id=user_id, organization_id=org_id,
        )
        if redacted != response.content:
            response.content = redacted
    except guardrail_service.GuardrailViolation as gv:
        response.content = f"[Respuesta bloqueada por guardrail '{gv.guardrail_name}']"

    # 3) Canary injection (si la org lo tiene activado)
    try:
        if LeakDetectionService.is_canary_enabled(org_id):
            response.content = LeakDetectionService.inject_canary(
                response.content, device_id or "", request_id or "",
            )
    except Exception:
        pass
