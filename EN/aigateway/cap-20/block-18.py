# Extracted from: LibroAIGateway/cap-20-classification-guardrails-firewall.md
# gateway/app/services/pipeline/stages/security_output.py:35-86

async def run(ctx) -> None:
    """Post-LLM scan on the full response."""
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
            response.content = "[Response blocked by security policy.]"
            logger.warning("security_output:response_blocked device=%s", device_id)

    # 2) Leak detection (exfiltration patterns)
    try:
        leak_output = LeakDetectionService.scan_output(response.content)
        if leak_output.suspicious:
            await SecurityEventService.emit(...)
    except Exception:
        logger.warning("security_output:leak_scan_failed err=%s", exc)

    # 2b) Configurable guardrails (output)
    try:
        redacted = await guardrail_service.evaluate(
            ctx.db, text=response.content, direction="output",
            request_id=request_id, user_id=user_id, organization_id=org_id,
        )
        if redacted != response.content:
            response.content = redacted
    except guardrail_service.GuardrailViolation as gv:
        response.content = f"[Response blocked by guardrail '{gv.guardrail_name}']"

    # 3) Canary injection (if the org has it enabled)
    try:
        if LeakDetectionService.is_canary_enabled(org_id):
            response.content = LeakDetectionService.inject_canary(
                response.content, device_id or "", request_id or "",
            )
    except Exception:
        pass
