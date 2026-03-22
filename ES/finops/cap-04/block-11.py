# Extraído de: LibroFinOps/cap-04-instrumentacion-llm.md
# Script de validación mensual
async def validate_tracking_completeness(month: int, year: int):
    """
    Compara el total calculado en LLMUsageLog
    con el importe real de la factura.
    Diferencia > 5% indica cobertura incompleta.
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
        print(f"Llamadas registradas: {row.total_calls:,}")
        print(f"Coste calculado: ${row.calculated_cost:.4f}")
        print(f"Tokens entrada: {row.total_input:,} | Salida: {row.total_output:,}")
        print("Comparar con factura Anthropic del mes indicado.")
