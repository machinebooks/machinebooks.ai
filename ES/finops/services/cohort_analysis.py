# Extraído de: LibroFinOps/cap-19-unit-economics.md
# services/cohort_analysis.py — Evolución del coste por cohorte
def cohort_cost_analysis(db: Session, cohort_month: str) -> dict:
    """Analiza cómo evoluciona el coste por MAU en una cohorte."""
    year, month = map(int, cohort_month.split("-"))

    # Usuarios registrados en el mes de la cohorte
    cohort_ids = [u.id for u in db.query(User.id).filter(
        extract("year", User.created_at) == year,
        extract("month", User.created_at) == month,
    ).all()]

    monthly_costs = []
    for offset in range(6):
        m = month + offset
        y = year + (m - 1) // 12
        m = ((m - 1) % 12) + 1
        total = db.query(func.sum(LLMUsageLog.total_cost_usd)).filter(
            LLMUsageLog.user_id.in_(cohort_ids),
            extract("year", LLMUsageLog.created_at) == y,
            extract("month", LLMUsageLog.created_at) == m,
        ).scalar() or 0
        active = db.query(func.count(distinct(LLMUsageLog.user_id))).filter(
            LLMUsageLog.user_id.in_(cohort_ids),
            extract("year", LLMUsageLog.created_at) == y,
            extract("month", LLMUsageLog.created_at) == m,
        ).scalar() or 0
        avg = round(total / active, 2) if active > 0 else 0
        monthly_costs.append({"month_offset": offset, "avg_cost_usd": avg,
                              "active_users": active})

    return {"cohort": cohort_month, "monthly_evolution": monthly_costs}
