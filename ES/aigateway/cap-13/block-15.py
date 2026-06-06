# Extraído de: LibroAIGateway/cap-13-tenants-cuotas.md
# En runner.py: el stage n7x_route verifica quota
if not await n7x_route.run(ctx):
    # Quota agotada → corta pipeline, responde 402
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
