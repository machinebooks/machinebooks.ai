# Extraído de: LibroFinOps/cap-17-roi-humanbaseline.md
# services/roi_tracker.py — Método de resumen por periodo
def get_summary(self, tenant_id: Optional[int] = None, days: int = 30) -> dict:
    """Resumen de ROI para el periodo indicado, con desglose por tipo de tarea."""
    from datetime import datetime, timedelta
    from sqlalchemy import func

    cutoff = datetime.utcnow() - timedelta(days=days)
    query = self.db.query(TaskCompletionLog).filter(
        TaskCompletionLog.completed_at >= cutoff
    )
    if tenant_id:
        query = query.filter(TaskCompletionLog.tenant_id == tenant_id)
    logs = query.all()

    if not logs:
        return {"message": "Sin datos en el periodo", "days": days}

    total_cost = sum(l.llm_cost_eur for l in logs)
    total_value = sum(l.human_value_eur or 0 for l in logs)
    accepted = [l for l in logs if l.accepted]
    acceptance_rate = len(accepted) / len(logs)

    # ROI por tipo de tarea
    by_task: dict = {}
    for log in logs:
        t = log.task_type
        if t not in by_task:
            by_task[t] = {"count": 0, "llm_cost": 0, "value": 0}
        by_task[t]["count"] += 1
        by_task[t]["llm_cost"] += log.llm_cost_eur
        by_task[t]["value"] += log.human_value_eur or 0

    for t in by_task:
        c, v = by_task[t]["llm_cost"], by_task[t]["value"]
        by_task[t]["roi"] = round((v - c) / c, 1) if c > 0 else 0

    return {
        "period_days": days, "total_tasks": len(logs),
        "accepted_tasks": len(accepted),
        "acceptance_rate": round(acceptance_rate, 3),
        "total_llm_cost_eur": round(total_cost, 2),
        "total_value_eur": round(total_value, 2),
        "roi_global": round((total_value - total_cost) / total_cost, 1) if total_cost > 0 else 0,
        "net_value_eur": round(total_value - total_cost, 2),
        "by_task_type": by_task,
    }
