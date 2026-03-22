# Extraído de: LibroDevSecOps/cap-24-security-champions.md
from datetime import datetime, timedelta
from dataclasses import dataclass, field

@dataclass
class ChampionMetrics:
    champion_name: str
    team: str
    period_start: datetime
    period_end: datetime
    # Remediación
    findings_assigned: int = 0
    findings_resolved: int = 0
    avg_resolution_hours: float = 0.0
    # Formación
    training_modules_completed: int = 0
    qa_bot_queries: int = 0
    # Influencia en el equipo
    security_prs_reviewed: int = 0
    team_mttr_days: float = 0.0
    team_mttr_previous_period: float = 0.0

def generate_champion_dashboard(
    champions: list[ChampionMetrics]
) -> dict:
    """Genera datos del dashboard de champions."""

    dashboard = {
        "generated_at": datetime.now().isoformat(),
        "program_summary": {},
        "leaderboard": [],
        "teams": [],
        "alerts": []
    }

    # Resumen del programa
    total_assigned = sum(c.findings_assigned for c in champions)
    total_resolved = sum(c.findings_resolved for c in champions)
    resolution_rate = (
        total_resolved / total_assigned * 100
        if total_assigned > 0 else 0
    )

    dashboard["program_summary"] = {
        "active_champions": len(champions),
        "total_findings_assigned": total_assigned,
        "total_findings_resolved": total_resolved,
        "resolution_rate_pct": round(resolution_rate, 1),
        "avg_mttr_days": round(
            sum(c.team_mttr_days for c in champions) / len(champions), 1
        ) if champions else 0,
        "total_training_modules": sum(
            c.training_modules_completed for c in champions
        ),
        "total_qa_queries": sum(c.qa_bot_queries for c in champions)
    }

    # Leaderboard por ratio de resolución
    for c in sorted(
        champions,
        key=lambda x: (
            x.findings_resolved / x.findings_assigned
            if x.findings_assigned > 0 else 0
        ),
        reverse=True
    ):
        rate = (
            c.findings_resolved / c.findings_assigned * 100
            if c.findings_assigned > 0 else 0
        )
        mttr_improvement = (
            (c.team_mttr_previous_period - c.team_mttr_days)
            / c.team_mttr_previous_period * 100
            if c.team_mttr_previous_period > 0 else 0
        )

        dashboard["leaderboard"].append({
            "champion": c.champion_name,
            "team": c.team,
            "resolution_rate_pct": round(rate, 1),
            "mttr_improvement_pct": round(mttr_improvement, 1),
            "training_modules": c.training_modules_completed,
            "qa_queries": c.qa_bot_queries
        })

    # Alertas de programa
    for c in champions:
        if c.qa_bot_queries == 0 and c.findings_assigned > 0:
            dashboard["alerts"].append({
                "type": "inactive_champion",
                "champion": c.champion_name,
                "message": (
                    f"{c.champion_name} tiene {c.findings_assigned} "
                    f"hallazgos asignados pero 0 consultas al bot. "
                    f"Posible desenganche del programa."
                )
            })
        if c.findings_assigned > 0:
            rate = c.findings_resolved / c.findings_assigned
            if rate < 0.3:
                dashboard["alerts"].append({
                    "type": "low_resolution",
                    "champion": c.champion_name,
                    "message": (
                        f"Ratio de resolución de {c.champion_name}: "
                        f"{rate:.0%}. Revisar carga o formación."
                    )
                })

    return dashboard
