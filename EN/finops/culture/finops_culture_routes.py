# Source: The FinOps Engineer and the Machine -- Chapter 24
# Pattern: FinOps culture gamification API

# api/finops_culture_routes.py
# Endpoints for cultural dashboards: efficiency leaderboard,
# champion history and team cost awareness metrics.

from datetime import date, datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from decimal import Decimal
import anthropic

from models.llm_usage_log import LLMUsageLog
from models.task_completion_log import TaskCompletionLog
from dependencies import get_db, require_permission

router = APIRouter(prefix="/finops/culture", tags=["FinOps Culture"])


@router.get("/leaderboard/equipos")
async def get_leaderboard_equipos(
    mes: date,
    db: Session = Depends(get_db),
    _: None = Depends(require_permission("finops:read")),
) -> dict:
    """
    Team ranking by efficiency (ROI/euro spent) in a given month.

    Does not rank by lowest cost: ranks by highest value per euro.
    This incentivizes using AI, not avoiding it.
    """
    primer_dia = mes.replace(day=1)

    # Total token cost per squad for the month
    costes_por_squad = (
        db.query(
            LLMUsageLog.squad_codigo,
            func.sum(LLMUsageLog.cost_eur).label("coste_total_eur"),
            func.count(LLMUsageLog.id).label("num_llamadas"),
        )
        .filter(
            func.date_trunc("month", LLMUsageLog.created_at) == primer_dia
        )
        .group_by(LLMUsageLog.squad_codigo)
        .all()
    )

    # Value generated per squad for the month (from TaskCompletionLog, see ch. 17)
    valor_por_squad = (
        db.query(
            TaskCompletionLog.squad_codigo,
            func.sum(TaskCompletionLog.valor_generado_eur).label("valor_total_eur"),
            func.count(TaskCompletionLog.id).label("num_tareas"),
        )
        .filter(
            func.date_trunc("month", TaskCompletionLog.created_at) == primer_dia
        )
        .group_by(TaskCompletionLog.squad_codigo)
        .all()
    )

    # Build cost and value index
    costes = {r.squad_codigo: r for r in costes_por_squad}
    valores = {r.squad_codigo: r for r in valor_por_squad}

    # Combine and calculate efficiency
    squads = set(costes.keys()) | set(valores.keys())
    leaderboard = []

    for squad in squads:
        coste = float(costes[squad].coste_total_eur) if squad in costes else 0.0
        valor = float(valores[squad].valor_total_eur) if squad in valores else 0.0

        # Efficiency = generated value / cost
        # If no cost (didn't use AI), efficiency is 0 (you can't measure what isn't used)
        eficiencia = valor / coste if coste > 0 else 0.0

        leaderboard.append({
            "squad": squad,
            "coste_eur": round(coste, 2),
            "valor_eur": round(valor, 2),
            "eficiencia": round(eficiencia, 1),  # euro-value per euro-cost
            "num_llamadas": costes[squad].num_llamadas if squad in costes else 0,
            "num_tareas": valores[squad].num_tareas if squad in valores else 0,
        })

    # Sort by descending efficiency
    leaderboard.sort(key=lambda x: x["eficiencia"], reverse=True)

    # Add position
    for i, entry in enumerate(leaderboard):
        entry["posicion"] = i + 1

    return {
        "mes": mes.isoformat(),
        "leaderboard": leaderboard,
        "meta": {
            "criterio": "valor_generado_eur / coste_tokens_eur",
            "descripcion": "Teams with the highest value per euro invested in AI"
        }
    }
