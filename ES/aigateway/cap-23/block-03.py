# Extraído de: LibroAIGateway/cap-23-compliance-regulatorio.md
# Esbozo ilustrativo (no es código del repo)
async def compliance_check(ctx: PipelineContext) -> None:
    use_case = await use_case_service.get(ctx.use_case_id)
    if not use_case or not use_case.is_active:
        raise UseCaseInactive("Caso de uso no activo")

    if use_case.ai_act_risk_level == "high_risk" and use_case.human_oversight_required:
        # La supervisión humana es un requisito de conformidad: se gestiona
        # fuera del request inline, no con una cola de espera bloqueante.
        ctx.requires_oversight = True

    # Transparencia obligatoria al usuario final
    if use_case.transparency_required:
        ctx.transparency_notice = True
