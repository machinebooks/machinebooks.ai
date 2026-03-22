# Extraído de: LibroDevSecOps/cap-24-security-champions.md
def calculate_gamification_score(
    champion: ChampionMetrics,
    findings_detail: list[dict]
) -> dict:
    """Score de gamificación que incentiva comportamientos correctos."""

    # Métrica 1: Ratio de resolución ponderada por severidad
    severity_weights = {"critical": 5, "high": 3, "medium": 1}
    weighted_resolved = sum(
        severity_weights.get(f["severity"], 1)
        for f in findings_detail
        if f["status"] == "resolved"
    )
    weighted_total = sum(
        severity_weights.get(f["severity"], 1)
        for f in findings_detail
    )
    resolution_score = (
        weighted_resolved / weighted_total * 40
        if weighted_total > 0 else 0
    )

    # Métrica 2: Velocidad de resolución (bonificación por resolver rápido)
    fast_resolutions = sum(
        1 for f in findings_detail
        if f["status"] == "resolved"
        and f["resolution_hours"] < 48
    )
    speed_score = min(30, fast_resolutions * 3)

    # Métrica 3: Actividad formativa (demuestra compromiso continuo)
    training_score = min(30, (
        champion.training_modules_completed * 2 +
        min(champion.qa_bot_queries, 20) * 1  # Cap para evitar gaming
    ))

    total = resolution_score + speed_score + training_score

    return {
        "champion": champion.champion_name,
        "total_score": round(total, 1),
        "breakdown": {
            "resolution_weighted": round(resolution_score, 1),
            "speed_bonus": round(speed_score, 1),
            "training_engagement": round(training_score, 1)
        },
        "tier": (
            "Gold" if total >= 75
            else "Silver" if total >= 50
            else "Bronze" if total >= 25
            else "Starter"
        )
    }
