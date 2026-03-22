# Extraído de: LibroFinOps/cap-17-roi-humanbaseline.md
# Integración del ROITracker en el flujo de generación
async def generate_offer(client_data: dict, user: User, db: Session):
    """Genera una oferta técnica con Claude y devuelve el resultado."""
    usage_log = await llm_service.generate_with_tracking(
        prompt=build_offer_prompt(client_data),
        model="claude-sonnet-4-6",
        task_type="offer_generation",
        user_id=user.id, tenant_id=user.tenant_id,
    )
    return OfferGenerationResult(
        content=usage_log.response_content,
        llm_usage_log_id=usage_log.id,
        llm_cost_eur=usage_log.total_cost_eur,
    )

async def accept_offer(result: OfferGenerationResult, user: User, db: Session):
    """El usuario acepta la oferta. Registramos el ROI como completado."""
    tracker = ROITracker(db)
    return tracker.record_completion(
        task_type="offer_generation",
        llm_cost_eur=result.llm_cost_eur, accepted=True,
        role=user.profile.role_name, user_id=user.id,
        tenant_id=user.tenant_id,
        llm_usage_log_id=result.llm_usage_log_id,
    )
