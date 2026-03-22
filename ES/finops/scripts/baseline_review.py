# Extraído de: LibroFinOps/cap-17-roi-humanbaseline.md
# scripts/baseline_review.py — Revisión trimestral automatizada
def generate_review_report(db: Session) -> dict:
    """Compara configuración contra comportamiento real de los últimos 90 días."""
    from sqlalchemy import func, Integer
    from datetime import datetime, timedelta

    cutoff = datetime.utcnow() - timedelta(days=90)
    real_acceptance = (
        db.query(
            TaskCompletionLog.task_type,
            func.count(TaskCompletionLog.id).label("total"),
            func.sum(func.cast(TaskCompletionLog.accepted, Integer)).label("accepted"),
        )
        .filter(TaskCompletionLog.completed_at >= cutoff)
        .group_by(TaskCompletionLog.task_type)
        .all()
    )

    discrepancies = []
    for row in real_acceptance:
        config = db.query(HumanBaselineConfig).filter(
            HumanBaselineConfig.task_type == row.task_type,
            HumanBaselineConfig.active == True,
        ).first()
        if not config or row.total < 20:  # mínimo 20 observaciones
            continue

        real_rate = row.accepted / row.total
        delta = abs(real_rate - config.acceptance_rate)
        if delta > 0.10:  # discrepancia > 10 puntos porcentuales
            discrepancies.append({
                "task_type": row.task_type,
                "configured": round(config.acceptance_rate, 3),
                "real_90d": round(real_rate, 3),
                "delta": round(delta, 3),
                "observations": row.total,
                "priority": "high" if delta > 0.20 else "medium",
            })

    return {
        "review_date": datetime.utcnow().isoformat(),
        "discrepancies": discrepancies,
        "recommendation": (
            "Actualizar valores con delta > 0.20 antes del próximo reporting."
            if any(d["priority"] == "high" for d in discrepancies)
            else "Discrepancias menores. Actualizar en la próxima revisión de ciclo."
        ),
    }
