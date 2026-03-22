# Extraído de: LibroDevSecOps/cap-23-excepciones-deuda.md
# Configuración del presupuesto de deuda
DEBT_BUDGET = {
    "max_total_score": 75.0,          # Puntuación máxima tolerada
    "max_critical_exceptions": 0,      # Cero excepciones CRITICAL
    "max_high_exceptions": 10,         # Máximo 10 excepciones HIGH
    "max_avg_age_days": 90,            # Edad media máxima: 90 días
    "max_expired_unresolved": 0        # Cero expiradas sin resolver
}


def evaluate_debt_budget(debt_data: dict) -> dict:
    """Evalúa la deuda actual contra el presupuesto definido."""
    violations = []

    if debt_data["total_debt_score"] > DEBT_BUDGET["max_total_score"]:
        violations.append({
            "rule": "total_score",
            "current": debt_data["total_debt_score"],
            "limit": DEBT_BUDGET["max_total_score"],
            "message": "Deuda total supera el presupuesto"
        })

    if debt_data["average_exception_age_days"] > DEBT_BUDGET["max_avg_age_days"]:
        violations.append({
            "rule": "avg_age",
            "current": debt_data["average_exception_age_days"],
            "limit": DEBT_BUDGET["max_avg_age_days"],
            "message": "Edad media de excepciones supera el límite"
        })

    if debt_data["expired_unresolved"] > DEBT_BUDGET["max_expired_unresolved"]:
        violations.append({
            "rule": "expired_unresolved",
            "current": debt_data["expired_unresolved"],
            "limit": DEBT_BUDGET["max_expired_unresolved"],
            "message": "Existen excepciones expiradas sin resolver"
        })

    budget_utilization = (
        debt_data["total_debt_score"] / DEBT_BUDGET["max_total_score"]
    ) * 100

    return {
        "budget_utilization_pct": round(budget_utilization, 1),
        "violations": violations,
        "within_budget": len(violations) == 0,
        "remaining_capacity": round(
            DEBT_BUDGET["max_total_score"] - debt_data["total_debt_score"], 1
        )
    }
