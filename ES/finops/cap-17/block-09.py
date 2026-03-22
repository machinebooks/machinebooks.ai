# Extraído de: LibroFinOps/cap-17-roi-humanbaseline.md
# Cálculo del ROI acumulado con inversión de ingeniería
def calculate_cumulative_roi(
    db: Session, engineering_investment_eur: float, start_date: datetime,
) -> dict:
    """ROI acumulado desde el inicio del proyecto, incluyendo ingeniería."""
    from sqlalchemy import func

    total_value, total_cost = (
        db.query(
            func.sum(TaskCompletionLog.human_value_eur),
            func.sum(TaskCompletionLog.llm_cost_eur),
        )
        .filter(TaskCompletionLog.completed_at >= start_date)
        .first()
    )
    total_value = total_value or 0
    total_cost = total_cost or 0
    total_investment = total_cost + engineering_investment_eur

    cumulative_roi = (
        (total_value - total_investment) / total_investment
        if total_investment > 0 else 0
    )
    return {
        "total_value_eur": round(total_value, 2),
        "total_llm_cost_eur": round(total_cost, 2),
        "engineering_investment_eur": engineering_investment_eur,
        "total_investment_eur": round(total_investment, 2),
        "cumulative_roi": round(cumulative_roi, 2),
        "payback_achieved": total_value >= total_investment,
        "net_value_eur": round(total_value - total_investment, 2),
    }
