# Extracted from: LibroAIGateway/cap-13-tenants-quotas.md
# In runner.py: the n7x_route stage checks quota
if not await n7x_route.run(ctx):
    # Quota exhausted → cuts pipeline, responds with 402
    raise HTTPException(
        status_code=402,
        detail={
            "detail": BUDGET_EXHAUSTED_MESSAGE,
            "bucket_hit": quota_result["bucket_hit"],
            "reset_at": quota_result["reset_at"],
            "plan": quota_result.get("plan"),
            "estimated_cost_eur": quota_result.get("estimated_cost_eur"),
        },
    )
