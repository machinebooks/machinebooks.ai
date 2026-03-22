# Source: The FinOps Engineer and the Machine -- Chapter 17
# Pattern: ROITracker integration in generation flow

# Integration of ROITracker in the generation flow
async def generate_offer(client_data: dict, user: User, db: Session):
    """Generates a technical proposal with Claude and returns the result."""
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
    """The user accepts the proposal. We record the ROI as completed."""
    tracker = ROITracker(db)
    return tracker.record_completion(
        task_type="offer_generation",
        llm_cost_eur=result.llm_cost_eur, accepted=True,
        role=user.profile.role_name, user_id=user.id,
        tenant_id=user.tenant_id,
        llm_usage_log_id=result.llm_usage_log_id,
    )
