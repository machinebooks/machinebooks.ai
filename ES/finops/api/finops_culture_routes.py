# Extraído de: LibroFinOps/cap-24-cultura-finops.md
# api/finops_culture_routes.py
# Endpoints para dashboards culturales: leaderboard por eficiencia,
# historial de campeones y métricas de cost awareness del equipo.

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

router = APIRouter(prefix="/finops/culture", tags=["FinOps Cultura"])


@router.get("/leaderboard/equipos")
async def get_leaderboard_equipos(
    mes: date,
    db: Session = Depends(get_db),
    _: None = Depends(require_permission("finops:read")),
) -> dict:
    """
    Ranking de equipos por eficiencia (ROI/euro gastado) en un mes dado.

    No clasifica por menor coste: clasifica por mayor valor por euro.
    Esto incentiva usar la IA, no evitarla.
    """
    primer_dia = mes.replace(day=1)

    # Coste total de tokens por squad en el mes
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

    # Valor generado por squad en el mes (de TaskCompletionLog, ver cap 17)
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

    # Construir índice de costes y valores
    costes = {r.squad_codigo: r for r in costes_por_squad}
    valores = {r.squad_codigo: r for r in valor_por_squad}

    # Combinar y calcular eficiencia
    squads = set(costes.keys()) | set(valores.keys())
    leaderboard = []

    for squad in squads:
        coste = float(costes[squad].coste_total_eur) if squad in costes else 0.0
        valor = float(valores[squad].valor_total_eur) if squad in valores else 0.0

        # Eficiencia = valor generado / coste
        # Si no hay coste (no usaron IA), eficiencia es 0 (no se mide lo que no se usa)
        eficiencia = valor / coste if coste > 0 else 0.0

        leaderboard.append({
            "squad": squad,
            "coste_eur": round(coste, 2),
            "valor_eur": round(valor, 2),
            "eficiencia": round(eficiencia, 1),  # euro-valor por euro-coste
            "num_llamadas": costes[squad].num_llamadas if squad in costes else 0,
            "num_tareas": valores[squad].num_tareas if squad in valores else 0,
        })

    # Ordenar por eficiencia descendente
    leaderboard.sort(key=lambda x: x["eficiencia"], reverse=True)

    # Añadir posicion
    for i, entry in enumerate(leaderboard):
        entry["posicion"] = i + 1

    return {
        "mes": mes.isoformat(),
        "leaderboard": leaderboard,
        "meta": {
            "criterio": "valor_generado_eur / coste_tokens_eur",
            "descripcion": "Equipos con mayor valor por euro invertido en IA"
        }
    }
