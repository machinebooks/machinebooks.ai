# Extracted from: LibroAIGateway/cap-23-compliance-regulatory.md
# Illustrative sketch (not the repo's code)
async def compliance_check(ctx: PipelineContext) -> None:
    use_case = await use_case_service.get(ctx.use_case_id)
    if not use_case or not use_case.is_active:
        raise UseCaseInactive("Use case is not active")

    if use_case.ai_act_risk_level == "high_risk" and use_case.human_oversight_required:
        # Human oversight is a compliance requirement: it is handled
        # outside the inline request, not with a blocking wait queue.
        ctx.requires_oversight = True

    # Mandatory transparency to the end user
    if use_case.transparency_required:
        ctx.transparency_notice = True
