# Extracted from: LibroAIGateway/cap-14-pricing-cost-roi.md
async def calculate_builtin_tools_cost_usd(
    db: AsyncSession, model_key: str, response_raw: Any,
    organization_id: int | None = None,
) -> float:
    counts = _count_calls_by_type(response_raw)
    if not any(counts.values()):
        return 0.0

    # Rates configurable in orchestrator_configs.system_infra
    infra = await get_system_infra(db)
    web_per_call  = infra.get("builtin_web_search_usd_per_call") or 0.025
    file_per_1k   = infra.get("builtin_file_search_usd_per_1k") or 2.50
    code_per_sess = infra.get("builtin_code_interpreter_usd_per_session") or 0.03

    total = (
        counts["web_search"] * float(web_per_call)
        + (counts["file_search"] / 1000.0) * float(file_per_1k)
        + counts["code_interpreter"] * float(code_per_sess)
    )
    return round(total, 6)
