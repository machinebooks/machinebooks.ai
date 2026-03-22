# Source: The FinOps Engineer and the Machine -- Chapter 4
# Pattern: Monthly tracking completeness validation

# Monthly validation script
async def validate_tracking_completeness(month: int, year: int):
    """
    Compares the total calculated in LLMUsageLog
    with the real invoice amount.
    Difference > 5% indicates incomplete coverage.
    """
    async with get_async_session() as session:
        result = await session.execute(
            select(
                func.count().label("total_calls"),
                func.sum(LLMUsageLog.total_cost_usd).label("calculated_cost"),
                func.sum(LLMUsageLog.input_tokens).label("total_input"),
                func.sum(LLMUsageLog.output_tokens).label("total_output"),
            )
            .where(
                and_(
                    func.year(LLMUsageLog.timestamp) == year,
                    func.month(LLMUsageLog.timestamp) == month,
                )
            )
        )
        row = result.one()
        print(f"Recorded calls: {row.total_calls:,}")
        print(f"Calculated cost: ${row.calculated_cost:.4f}")
        print(f"Input tokens: {row.total_input:,} | Output: {row.total_output:,}")
        print("Compare with the Anthropic invoice for the indicated month.")
